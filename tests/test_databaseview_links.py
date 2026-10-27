import contextlib
import io
import importlib.util
import sys
from unittest.mock import patch
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import yaml
from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import Abort, PluginError


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.append(dict(attrs).get("href", ""))


class SnapshotPublishingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.docs = self.root / "docs"
        self.snapshots = self.root / "snapshots"
        (self.docs / "books").mkdir(parents=True)
        (self.docs / "topics").mkdir()
        self.snapshots.mkdir()
        (self.docs / "index.md").write_text("# Home\n", encoding="utf-8")
        (self.docs / "books/index.md").write_text(
            '# Books\n\n![[Books.base]]\n\n[[topics/A topic#Details|Read topic]]\n'
            '\n`[[A topic]]`\n\n[[Missing note]]\n\n```\n![[Not a real.base]]\n```\n',
            encoding="utf-8",
        )
        (self.docs / "topics/A topic.md").write_text(
            '# A topic\n\n## Details\n\n![[Books.base#OnTopicPage]]\n', encoding="utf-8"
        )
        (self.docs / "books/A book (draft) #1.md").write_text('# Book\n', encoding="utf-8")
        # Deliberately invalid Bases syntax: the publisher must never parse it.
        (self.docs / "Books.base").write_text('filters: [not valid YAML', encoding="utf-8")
        # Source Markdown links support punctuation in note filenames.
        self.table = '| Book | Value |\n| --- | --- |\n| [Selected book](A%20book%20%28draft%29%20%231.md) | 42 |\n'
        (self.snapshots / "books.md").write_text(self.table, encoding="utf-8")
        (self.snapshots / "topic.md").write_text('No results.\n', encoding="utf-8")
        self.manifest = {
            'books/index.md': {'Books.base': 'books.md'},
            'topics/A topic.md': {'Books.base#OnTopicPage': 'topic.md'},
        }
        self.save_manifest()
        (self.root / "mkdocs.yml").write_text(
            'site_name: Test\nplugins:\n  - databaseview:\n      snapshot_manifest: snapshots/manifest.yml\n',
            encoding="utf-8",
        )

    def save_manifest(self):
        (self.snapshots / "manifest.yml").write_text(yaml.safe_dump(self.manifest), encoding="utf-8")

    def run_build(self, directory_urls=True, site_url='https://example.com/reading-wiki/'):
        config = load_config(config_file=str(self.root / "mkdocs.yml"),
                             use_directory_urls=directory_urls, site_url=site_url, strict=True)
        with contextlib.redirect_stdout(io.StringIO()):
            build(config)

    def test_snapshot_rows_and_note_links(self):
        for directory_urls in (True, False):
            for site_url in ('', 'https://example.com/reading-wiki/'):
                with self.subTest(directory_urls=directory_urls, site_url=site_url):
                    self.run_build(directory_urls, site_url)
                    html = (self.root / "site/books/index.html").read_text(encoding="utf-8")
                    self.assertIn('Selected book', html)
                    self.assertIn('<td>42</td>', html)
                    self.assertIn('<code>[[A topic]]</code>', html)
                    self.assertIn('![[Not a real.base]]', html)
                    self.assertIn('unresolved-wikilink', html)
                    parser = Links()
                    parser.feed(html)
                    topic_links = [h for h in parser.hrefs if h.endswith('#details')]
                    self.assertEqual(len(topic_links), 1)
                    if site_url:
                        self.assertTrue(topic_links[0].startswith('/reading-wiki/topics/'))
                    for href in [h for h in parser.hrefs if '#details' in h or 'draft' in h]:
                        url = urlsplit(urljoin('https://example.com/reading-wiki/books/', href))
                        self.assertTrue(url.path.startswith('/reading-wiki/'), href)
                        target = self.root / 'site' / unquote(url.path[len('/reading-wiki/'):])
                        if url.path.endswith('/'):
                            target /= 'index.html'
                        self.assertTrue(target.is_file(), href)
                    topic_output = 'topics/A topic/index.html' if directory_urls else 'topics/A topic.html'
                    topic_html = (self.root / 'site' / topic_output).read_text(encoding='utf-8')
                    self.assertIn('No results.', topic_html)
                    self.assertNotIn('Selected book', topic_html)

    def assert_rejected(self, pattern):
        with self.assertRaises(Abort) as caught:
            self.run_build()
        self.assertIsInstance(caught.exception.__context__, PluginError)
        self.assertRegex(str(caught.exception.__context__), pattern)

    def test_book_cards_preserve_groups_links_and_other_views(self):
        config_path = self.root / 'mkdocs.yml'
        data = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        data['plugins'][0]['databaseview']['book_card_views'] = ['Books.base', 'Books.base#View']
        config_path.write_text(yaml.safe_dump(data), encoding='utf-8')
        book = self.docs / 'books/A book (draft) #1.md'
        book.write_text('---\ncover image: "https://example.com/cover.jpg?a=1&b=2"\n---\n# Book\n', encoding='utf-8')
        table = '| file.name | author |\n| --- | --- |\n| [A & B](A%20book%20%28draft%29%20%231.md) | Writer & Co |\n'
        (self.snapshots / 'books.md').write_text('### 2026\n\n' + table + '\n### 2024\n\n' + table, encoding='utf-8')
        self.manifest['books/index.md']['Books.base#View'] = 'books.md'
        self.save_manifest()
        for explicit in (False, True):
            if explicit:
                page = self.docs / 'books/index.md'
                page.write_text('# Books\n\n![[Books.base#View]]\n', encoding='utf-8')
            for directory_urls in (True, False):
                for site_url in ('', 'https://example.com/reading-wiki/'):
                    with self.subTest(explicit=explicit, directory_urls=directory_urls, site_url=site_url):
                        self.run_build(directory_urls, site_url)
                        html = (self.root / 'site/books/index.html').read_text(encoding='utf-8')
                        self.assertEqual(html.count('class="rw-book-card"'), 2)
                        self.assertIn('id="2026"', html)
                        self.assertLess(html.index('id="2026"'), html.index('id="2024"'))
                        self.assertIn('A &amp; B', html)
                        self.assertIn('Writer &amp; Co', html)
                        self.assertIn('cover.jpg?a=1&amp;b=2', html)
                        self.assertIn('loading="lazy"', html)
                        parser = Links()
                        parser.feed(html)
                        for href in [h for h in parser.hrefs if 'draft' in h]:
                            url = urlsplit(urljoin('https://example.com/reading-wiki/books/', href))
                            target = self.root / 'site' / unquote(url.path[len('/reading-wiki/'):])
                            if url.path.endswith('/'):
                                target /= 'index.html'
                            self.assertTrue(target.is_file(), href)
                        topic_output = 'topics/A topic/index.html' if directory_urls else 'topics/A topic.html'
                        topic = (self.root / 'site' / topic_output).read_text(encoding='utf-8')
                        self.assertIn('No results.', topic)
                        self.assertNotIn('rw-book-grid', topic)

    def test_book_cover_validation_and_empty_cards(self):
        from mkdocs_databaseview_plugin.book_cards import cover_url, render_cards
        for value in (None, '', '   ', [], 42, 'javascript:alert(1)', 'data:image/png;base64,abc',
                      '/cover.jpg', '//example.com/cover.jpg', 'https://', 'https://example.com:bad/a',
                      'https://example.com/a b.jpg', 'https://[invalid/a'):
            with self.subTest(value=value):
                self.assertIsNone(cover_url(value))
        for value in ('https://example.com/a.jpg', 'http://example.com/a%20b.jpg?x=1&y=2'):
            self.assertEqual(cover_url(' ' + value + ' '), value)
        table = '| file.name | author |\n| --- | --- |\n| [A & B](book.md) | null |\n'
        result = render_cards(table, lambda source: ('/book/', None))
        self.assertIn('rw-book-placeholder', result)
        self.assertNotIn('<img', result)
        self.assertNotIn('rw-book-author', result)
        self.assertIn('A &amp; B', result)
        self.assertIn('No books in this view.', render_cards('| Book |\n| --- |\n', lambda _: None))
        self.assertIn('No books in this view.', render_cards('No results.', lambda _: None))

    def test_capture_helper_saves_export_without_changing_rows(self):
        script = Path(__file__).resolve().parents[1] / 'tools/save_database_snapshot.py'
        spec = importlib.util.spec_from_file_location('save_database_snapshot', script)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        exported = '| Note | Value |\n| --- | --- |\n| [[A topic]] | 99 |\n'
        helper.ROOT = self.root
        args = ['save_database_snapshot.py', '--page', 'books/index.md', '--embed', 'Books.base']
        with patch.object(sys, 'argv', args), patch.object(sys, 'stdin', io.StringIO(exported)):
            with contextlib.redirect_stdout(io.StringIO()):
                helper.main()
        self.assertEqual((self.snapshots / 'books.md').read_text(encoding='utf-8'), exported)
        self.run_build()
        html = (self.root / 'site/books/index.html').read_text(encoding='utf-8')
        self.assertIn('<td>99</td>', html)
        self.assertIn('/reading-wiki/topics/A%20topic/', html)

    def test_missing_export_fails_without_inventing_results(self):
        (self.snapshots / 'books.md').unlink()
        self.assert_rejected('export.*Books.base')

    def test_page_context_requires_its_own_snapshot(self):
        del self.manifest['topics/A topic.md']
        self.save_manifest()
        self.assert_rejected('no snapshot mapped.*OnTopicPage')

    def test_empty_export_and_unrendered_embeds_are_rejected(self):
        for text in ('', '![[Books.base]]'):
            (self.snapshots / 'books.md').write_text(text, encoding='utf-8')
            self.assert_rejected('snapshot|export')

    def test_manifest_cannot_read_outside_snapshot_directory(self):
        self.manifest['books/index.md']['Books.base'] = '../docs/index.md'
        self.save_manifest()
        self.assert_rejected('must stay inside')


if __name__ == '__main__':
    unittest.main()
