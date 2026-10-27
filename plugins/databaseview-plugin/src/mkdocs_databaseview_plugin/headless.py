"""Small, explicit Bases subset for Safe Travels' server-side category tables.

This is not an implementation of the Obsidian expression language. Unknown
syntax fails the build, even when a filter would otherwise match no notes.
"""
from pathlib import Path
import math
import posixpath
import re
from urllib.parse import quote

import yaml
from mkdocs.exceptions import PluginError

from .page_cards import render_page_cards


def unsupported(value):
    raise PluginError(f'Headless Bases does not support {value!r}. Ask the wiki maintainer to adapt the Base; no stale table was published.')


def compile_filter(spec):
    if spec is None:
        return lambda note, context: True
    if isinstance(spec, dict) and len(spec) == 1:
        operation, children = next(iter(spec.items()))
        if operation not in ('and', 'or', 'not') or not isinstance(children, list):
            unsupported(spec)
        predicates = [compile_filter(child) for child in children]
        def predicate(note, context):
            values = [test(note, context) for test in predicates]
            return all(values) if operation == 'and' else any(values) if operation == 'or' else not any(values)
        return predicate
    if not isinstance(spec, str):
        unsupported(spec)
    expression = spec.strip()
    if expression.startswith('!'):
        inner = compile_filter(expression[1:])
        return lambda note, context: not inner(note, context)
    match = re.fullmatch(r'file\.hasTag\("([^"\\]+)"\)', expression)
    if match:
        tag = match[1].lstrip('#').casefold()
        return lambda note, context: any(value == tag or value.startswith(tag + '/') for value in note['tags'])
    match = re.fullmatch(r'file\.name\.contains\("([^"\\]*)"\)', expression)
    if match:
        return lambda note, context: match[1] in note['name']
    match = re.fullmatch(r'(?:note\.)?([A-Za-z_][\w ]*)\.contains\((?:this\.file\.name\.toString\(\)|"([^"\\]*)")\)', expression)
    if match:
        key = match[1]
        literal = match[2]
        def contains(note, context):
            value = note['properties'].get(key)
            if value is None:
                return False
            if not isinstance(value, str):
                # Obsidian Link values in lists differ from strings. Never
                # silently approximate those comparisons.
                unsupported(f'{key} must be Text for this category filter')
            return (context if literal is None else literal) in value
        return contains
    unsupported(spec)


def load_notes(vault):
    notes = []
    for file in sorted(Path(vault).rglob('*.md')):
        relative = file.relative_to(vault)
        if any(part.startswith('.') for part in relative.parts):
            continue
        text = file.read_text(encoding='utf-8-sig')
        frontmatter = re.match(r'\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)', text, re.S)
        try:
            properties = (yaml.safe_load(frontmatter[1]) or {}) if frontmatter else {}
        except yaml.YAMLError as exc:
            raise PluginError(f'{relative}: invalid note properties: {exc}') from exc
        if not isinstance(properties, dict):
            raise PluginError(f'{relative}: note properties must be a mapping.')
        tags = properties.get('tags') or []
        if isinstance(tags, str):
            tags = re.split(r'[,\s]+', tags)
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise PluginError(f'{relative}: tags must be text or a list of text.')
        body = text[frontmatter.end():] if frontmatter else text
        body = re.sub(r'(?ms)^\s*(`{3,}|~{3,}).*?^\s*\1\s*$', '', body)
        body = re.sub(r'`[^`]*`', '', body)
        tags += re.findall(r'(?<![\w/#])#([\w/-]+)', body)
        notes.append({'path': relative.as_posix(), 'name': file.stem,
                      'properties': properties, 'tags': [tag.lstrip('#').casefold() for tag in tags]})
    return notes


def cell(value):
    if value is None:
        return ''
    if isinstance(value, list):
        return ', '.join(cell(item) for item in value)
    return str(value).replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', '<br>')


class HeadlessBases:
    def __init__(self, vault):
        self.vault = Path(vault)
        self.notes = load_notes(self.vault)
        self.bases = [file for file in self.vault.rglob('*.base')
                      if not any(part.startswith('.') for part in file.relative_to(self.vault).parts)]

    def render(self, page, base, view_name, card_href=None):
        relative = posixpath.normpath(posixpath.join(posixpath.dirname(page), base))
        exact = [file for file in self.bases if file.relative_to(self.vault).as_posix().casefold() in (relative.casefold(), base.casefold())]
        candidates = exact or [file for file in self.bases if file.name.casefold() == Path(base).name.casefold()]
        if len(candidates) != 1:
            raise PluginError(f'{page}: Base missing or ambiguous: {base}')
        try:
            definition = yaml.safe_load(candidates[0].read_text(encoding='utf-8-sig'))
        except yaml.YAMLError as exc:
            raise PluginError(f'{base}: invalid YAML: {exc}') from exc
        if not isinstance(definition, dict):
            unsupported(definition)
        for key in definition:
            if key not in ('filters', 'views', 'properties'):
                unsupported(f'{base}: {key}')
        views = definition.get('views')
        if not isinstance(views, list) or not views or any(not isinstance(view, dict) for view in views):
            unsupported(f'{base}: views')
        selected = [view for view in views if view.get('name') == view_name] if view_name else views[:1]
        if len(selected) != 1:
            raise PluginError(f'{base}: view missing or ambiguous: {view_name}')
        view = selected[0]
        view_type = view.get('type')
        allowed = {'type', 'name', 'filters', 'order'}
        allowed |= {'image', 'imageFit', 'imageAspectRatio', 'cardSize'} if view_type == 'cards' else {'columnSize'}
        for key in view:
            if key not in allowed:
                unsupported(f'{base}: view setting {key}')
        if view_type not in ('table', 'cards'):
            unsupported(f'{base}: view type {view.get("type")}')
        global_filter = compile_filter(definition.get('filters'))
        view_filter = compile_filter(view.get('filters'))
        columns = view.get('order', ['file.name'])
        if not isinstance(columns, list) or not columns or any(not isinstance(column, str) or column.startswith(('formula.', 'file.')) and column != 'file.name' for column in columns):
            unsupported(f'{base}: columns {columns}')
        rows = [note for note in self.notes if global_filter(note, Path(page).stem) and view_filter(note, Path(page).stem)]
        rows.sort(key=lambda note: (note['name'].casefold(), note['path']))
        properties = definition.get('properties') or {}
        if not isinstance(properties, dict):
            unsupported(f'{base}: properties')
        if view_type == 'cards':
            if columns != ['file.name']:
                unsupported(f'{base}: cards display only file.name')
            image = view.get('image', 'note.header image url')
            if not isinstance(image, str) or not image.startswith('note.') or not image[5:].strip():
                unsupported(f'{base}: cards image must be a note property')
            size = view.get('cardSize', 220)
            aspect = view.get('imageAspectRatio', 16 / 9)
            for label, value in [('cardSize', size), ('imageAspectRatio', aspect)]:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                    unsupported(f'{base}: invalid {label}')
            fit = view.get('imageFit', 'cover')
            if fit not in ('cover', 'contain'):
                unsupported(f'{base}: invalid imageFit')
            # The plugin supplies MkDocs' actual output URLs. The default also
            # allows standalone rendering with the usual directory URL layout.
            def default_href(path):
                target = posixpath.splitext(path)[0] + '/'
                current = posixpath.splitext(page)[0]
                return quote(posixpath.relpath(target, current), safe='/') + '/'
            return render_page_cards(rows, image[5:], card_href or default_href, size, aspect, fit)
        labels = []
        for column in columns:
            setting = properties.get(column, {})
            if not isinstance(setting, dict) or set(setting) - {'displayName'}:
                unsupported(f'{base}: property {column}')
            labels.append(cell(setting.get('displayName', 'file name' if column == 'file.name' else column.removeprefix('note.'))))
        lines = ['| ' + ' | '.join(labels) + ' |', '| ' + ' | '.join('---' for _ in columns) + ' |']
        for note in rows:
            values = []
            for column in columns:
                if column == 'file.name':
                    href = quote(posixpath.relpath(note['path'], posixpath.dirname(page) or '.'), safe='/')
                    label = cell(note['name']).replace('[', '\\[').replace(']', '\\]')
                    values.append(f'[{label}]({href})')
                else:
                    values.append(cell(note['properties'].get(column.removeprefix('note.'))))
            lines.append('| ' + ' | '.join(values) + ' |')
        return '\n'.join(lines) + '\n'
