from __future__ import annotations

import posixpath
import hashlib
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree

import yaml
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import AtomicString
from mkdocs.config import config_options
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin

from .automatic_export import input_digest, request_export, read_export_state
from .book_cards import cover_url, render_cards


BASE_EMBED_RE = re.compile(r"!\[\[([^\]#]+?\.base)(?:#([^\]]+))?\]\]", re.IGNORECASE)
WIKI_PATTERN = r"(?<!!)\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]"


class NoteLinks(InlineProcessor):
    def __init__(self, plugin):
        super().__init__(WIKI_PATTERN)
        self.plugin = plugin

    def handleMatch(self, match, data):
        name, heading, alias = match.groups()
        target = self.plugin.resolve_note(name.strip())
        label = (alias or name).strip()
        if target is None:
            # Obsidian permits links to notes that do not exist yet. Keep the
            # label readable without generating a URL that would return 404.
            element = ElementTree.Element("span", {"class": "unresolved-wikilink"})
            element.text = AtomicString(label)
        else:
            href = self.plugin.note_href(target)
            if heading:
                from markdown.extensions.toc import slugify
                href += "#" + slugify(heading.strip(), "-")
            element = ElementTree.Element("a", {"href": href})
            element.text = AtomicString(label)
        return element, match.start(0), match.end(0)


class AttachmentLinks(InlineProcessor):
    def __init__(self, plugin):
        super().__init__(r'!\[\[([^\]|]+\.(?:png|jpe?g|gif|svg|webp|avif))(?:\|([^\]]+))?\]\]')
        self.plugin = plugin

    def handleMatch(self, match, data):
        name, size = match.groups()
        matches = [file for file in self.plugin.files
                   if file.src_uri.casefold() == name.casefold()
                   or Path(file.src_uri).name.casefold() == name.casefold()]
        if len(matches) != 1:
            element = ElementTree.Element('span', {'class': 'unresolved-attachment'})
            element.text = AtomicString(name)
        else:
            href = posixpath.relpath(matches[0].src_uri, posixpath.dirname(self.plugin.current_page) or '.')
            element = ElementTree.Element('img', {'src': quote(href, safe='/'), 'alt': name})
            if size and re.fullmatch(r'\d+(?:x\d+)?', size):
                width, _, height = size.partition('x')
                element.set('width', width)
                if height:
                    element.set('height', height)
        return element, match.start(0), match.end(0)


class NoteLinksExtension(Extension):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def extendMarkdown(self, md):
        # Code spans and fenced code are handled first by Python-Markdown.
        md.inlinePatterns.register(NoteLinks(self.plugin), "databaseview-wikilinks", 175)
        md.inlinePatterns.register(AttachmentLinks(self.plugin), "databaseview-attachments", 176)


class DBViewPlugin(BasePlugin):
    """Publish exported Obsidian tables without evaluating Bases expressions."""

    config_scheme = (
        ("auto_export", config_options.Type(bool, default=False)),
        ("committed_export", config_options.Type(bool, default=False)),
        ("export_timeout", config_options.Type(int, default=90)),
        ("snapshot_manifest", config_options.Type(str, default="database-snapshots/manifest.yml")),
        ("book_card_views", config_options.ListOfItems(config_options.Type(str), default=[])),
    )

    def on_config(self, config):
        root = Path(config.config_file_path).resolve().parent
        self.manifest_path = (root / self.config["snapshot_manifest"]).resolve()
        if not self.config["auto_export"]:
            self.load_manifest()
        self.site_url_path = urlsplit(config.get("site_url") or "").path.rstrip("/")
        config["markdown_extensions"].append(NoteLinksExtension(self))
        return config

    def load_manifest(self):
        try:
            self.manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8-sig")) or {}
        except (OSError, yaml.YAMLError) as exc:
            raise PluginError(f"Cannot read database snapshot manifest {self.manifest_path}: {exc}") from exc
        if not isinstance(self.manifest, dict):
            raise PluginError("Database snapshot manifest must map page paths to embed/snapshot mappings.")

    def on_pre_build(self, config):
        if self.config["committed_export"]:
            if self.config["auto_export"]:
                raise PluginError('Choose live auto_export or committed_export, not both.')
            self.export_state, text = read_export_state(self.manifest_path)
            self.manifest = yaml.safe_load(text) or {}
            if not isinstance(self.manifest, dict):
                raise PluginError('Invalid committed export manifest.')
            self.check_fresh(config)
            return
        if not self.config["auto_export"]:
            return
        from mkdocs.structure.files import get_files
        pages = [file.src_uri for file in get_files(config).documentation_pages()]
        result = request_export(config["docs_dir"], pages, self.config["export_timeout"])
        self.export_state, text = read_export_state(self.manifest_path)
        self.manifest = yaml.safe_load(text) or {}
        if not isinstance(self.manifest, dict):
            raise PluginError("Automatic export returned an invalid manifest.")
        if self.export_state.get("inputDigest") != result["inputDigest"]:
            raise PluginError("Snapshot metadata does not match the completed Obsidian export.")
        self.check_fresh(config)

    def check_fresh(self, config):
        if self.config["committed_export"] and input_digest(config["docs_dir"], content_only=True) != self.export_state.get("contentDigest"):
            raise PluginError('Committed Obsidian exports are stale. Run a local live build and commit database-snapshots with the notes.')
        if self.config["auto_export"] and input_digest(config["docs_dir"]) != self.export_state["inputDigest"]:
            raise PluginError("Notes changed since the Obsidian export; rerun the build before publishing.")

    def on_post_build(self, config):
        self.check_fresh(config)

    def on_files(self, files, config):
        self.check_fresh(config)
        self.files = files
        self.notes = {}
        self.note_names = {}
        for file in files.documentation_pages():
            key = file.src_uri.casefold()
            self.notes[key] = file
            self.note_names.setdefault(Path(file.src_uri).stem.casefold(), []).append(file)
        errors = []
        # Validate every published view before generating pages or deploying.
        # Never substitute invented rows or fall back to a filter evaluator.
        for file in files.documentation_pages():
            if not file.abs_src_path:
                continue
            markdown = Path(file.abs_src_path).read_text(encoding="utf-8-sig")
            for match in self.embeds_in_markdown(markdown):
                try:
                    self.read_snapshot(file.src_uri, match)
                except PluginError as exc:
                    errors.append(str(exc))
        if errors:
            raise PluginError("Database snapshots are required before publishing:\n" + "\n".join(errors))
        return files

    @staticmethod
    def embeds_in_markdown(markdown):
        # Protect code examples from being interpreted as database embeds.
        fence = None
        for line in markdown.splitlines(keepends=True):
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if marker:
                token = marker.group(1)
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
                continue
            if fence is None and not line.startswith(("    ", "\t")):
                # Inline code may contain examples of embeds too.
                for part in re.split(r"(`+)(.*?)(?:\1)", line)[::3]:
                    yield from BASE_EMBED_RE.finditer(part)

    @staticmethod
    def embed_key(match):
        base = match.group(1).strip().replace("\\", "/")
        view = match.group(2)
        return base + ("#" + view.strip() if view else "")

    def read_snapshot(self, page, match):
        key = self.embed_key(match)
        entries = self.manifest.get(page, {})
        if not isinstance(entries, dict):
            raise PluginError(f"{page}: manifest entry must map embeds to Markdown snapshots.")
        relative = entries.get(key)
        if not isinstance(relative, str) or not relative:
            raise PluginError(f"{page}: no snapshot mapped for ![[{key}]] in {self.manifest_path}")
        root = self.manifest_path.parent
        path = (root / relative).resolve()
        if root not in path.parents:
            raise PluginError(f"{page}: snapshot must stay inside {root}: {relative}")
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise PluginError(f"{page}: export ![[{key}]] from Obsidian to {path}: {exc.strerror}") from exc
        if self.config["auto_export"] or self.config["committed_export"]:
            expected = self.export_state.get("hashes", {}).get(relative)
            if not expected or hashlib.sha256(text.encode("utf-8")).hexdigest() != expected:
                raise PluginError(f"{page}: snapshot {path} does not match its Obsidian export.")
        if not text.strip():
            raise PluginError(f"{page}: snapshot {path} is empty; export a table or an explicit 'No results.' message.")
        if list(self.embeds_in_markdown(text)):
            raise PluginError(f"{page}: {path} still contains a .base embed; export the rendered table instead.")
        return text

    def on_page_markdown(self, markdown, page, config, files):
        self.current_page = page.file.src_uri
        # Replace only real embeds, leaving code examples untouched.
        output = []
        fence = None
        for line in markdown.splitlines(keepends=True):
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if marker:
                token = marker.group(1)
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
                output.append(line)
            elif fence is not None or line.startswith(("    ", "\t")):
                output.append(line)
            else:
                parts = re.split(r"(`+.*?`+)", line)
                for index in range(0, len(parts), 2):
                    parts[index] = BASE_EMBED_RE.sub(
                        lambda match: "\n\n" + self.render_snapshot(match) + "\n\n",
                        parts[index],
                    )
                output.append("".join(parts))
        return "".join(output)

    def render_snapshot(self, match):
        snapshot = self.read_snapshot(self.current_page, match)
        if self.embed_key(match) in self.config['book_card_views']:
            return render_cards(snapshot, self.book_card_data)
        return snapshot

    def book_card_data(self, source):
        target = self.resolve_note(unquote(urlsplit(source).path))
        if target is None:
            raise PluginError(f'{self.current_page}: Book card target not found: {source}')
        text = Path(target.abs_src_path).read_text(encoding='utf-8-sig')
        frontmatter = re.match(r'\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)', text, re.DOTALL)
        metadata = yaml.safe_load(frontmatter.group(1)) if frontmatter else {}
        cover = cover_url(metadata.get('cover image')) if isinstance(metadata, dict) else None
        return self.note_href(target, rendered=True), cover

    def resolve_note(self, name):
        name = name.replace("\\", "/")
        if not name.lower().endswith(".md"):
            name += ".md"
        parent = posixpath.dirname(self.current_page)
        for candidate in (posixpath.normpath(posixpath.join(parent, name)), name.lstrip("/")):
            target = self.notes.get(candidate.casefold())
            if target:
                return target
        matches = self.note_names.get(Path(name).stem.casefold(), [])
        return matches[0] if len(matches) == 1 else None

    def note_href(self, target, rendered=False):
        if self.site_url_path:
            return self.site_url_path + "/" + target.url
        if rendered:
            current = self.notes[self.current_page.casefold()]
            href = posixpath.relpath(target.url, posixpath.dirname(current.url) or '.')
            return href + ('/' if target.url.endswith('/') else '')
        source = posixpath.relpath(target.src_uri, posixpath.dirname(self.current_page) or ".")
        return quote(source, safe="/")
