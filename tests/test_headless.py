from pathlib import Path
import tempfile
import unittest

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import PluginError

from mkdocs_databaseview_plugin.headless import HeadlessBases, compile_filter


class HeadlessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = self.root / 'docs'
        (self.docs / 'Templates/Bases').mkdir(parents=True)
        (self.docs / 'Team Folders/Tech').mkdir(parents=True)
        self.base = self.docs / 'Templates/Bases/Pages.base'
        self.base.write_text('''filters:
  and:
    - file.hasTag("page")
    - '!file.name.contains("template")'
views:
  - type: table
    name: Table
    order: [file.name, Categories]
  - type: table
    name: ByCategory
    filters:
      and:
        - Categories.contains(this.file.name.toString())
    order: [file.name, Categories]
''', encoding='utf8')
        (self.docs / 'Team Folders/Tech/Tech.md').write_text('# Tech\n![[pages.base#ByCategory]]\n', encoding='utf8')
        (self.docs / 'index.md').write_text('# Home\n![[Pages.base]]\n', encoding='utf8')
        self.note('Physics', 'Tech')
        self.note('Textures', 'Art')
        (self.root / 'mkdocs.yml').write_text('''site_name: Team
site_url: https://l4valamp.github.io/safetravels-docs/
exclude_docs: |
  /Templates/**
plugins:
  - databaseview:
      headless: true
''', encoding='utf8')

    def note(self, name, category):
        (self.docs / f'{name}.md').write_text(f'---\ntags: ["#page"]\nCategories: "[[{category}]]"\n---\n# {name}\n', encoding='utf8')

    def test_category_context_matches_native_export_shape(self):
        engine = HeadlessBases(self.docs)
        self.assertEqual(engine.render('Team Folders/Tech/Tech.md', 'pages.base', 'ByCategory'),
                         '| file name | Categories |\n| --- | --- |\n| [Physics](../../Physics.md) | [[Tech]] |\n')
        art = engine.render('Team Folders/Art/Art.md', 'pages.base', 'ByCategory')
        self.assertIn('[Textures]', art)
        self.assertNotIn('[Physics]', art)

    def test_new_edits_and_deletions_build_without_exporter_or_snapshots(self):
        def run():
            build(load_config(str(self.root / 'mkdocs.yml'), strict=True))
            return (self.root / 'site/Team Folders/Tech/Tech/index.html').read_text(encoding='utf8')
        self.assertIn('Physics', run())
        self.note('New page', 'Tech')
        (self.docs / 'Physics.md').unlink()
        html = run()
        self.assertIn('New page', html)
        self.assertNotIn('Physics', html)
        self.assertNotIn('![[', html)
        self.assertFalse((self.root / 'database-snapshots').exists())
        self.assertFalse((self.docs / '.obsidian').exists())

    def test_unsupported_syntax_fails_even_with_no_matching_rows(self):
        self.base.write_text(self.base.read_text().replace('file.hasTag("page")', 'file.hasTag("missing")').replace(
            'Categories.contains(this.file.name.toString())', 'today() > date("2020-01-01")'), encoding='utf8')
        with self.assertRaisesRegex(PluginError, 'does not support'):
            HeadlessBases(self.docs).render('Team Folders/Tech/Tech.md', 'Pages.base', 'ByCategory')

    def test_formulas_sorting_grouping_and_unknown_views_fail_explicitly(self):
        original = self.base.read_text()
        for extra in ('formulas: {test: "1 + 1"}\n',):
            self.base.write_text(original + extra, encoding='utf8')
            with self.assertRaises(PluginError):
                HeadlessBases(self.docs).render('index.md', 'Pages.base', None)
        for key in ('sort', 'groupBy', 'summaries', 'limit'):
            self.base.write_text(original.replace('name: ByCategory', f'name: ByCategory\n    {key}: []'), encoding='utf8')
            with self.assertRaises(PluginError):
                HeadlessBases(self.docs).render('index.md', 'Pages.base', 'ByCategory')
        self.base.write_text(original, encoding='utf8')
        with self.assertRaisesRegex(PluginError, 'view missing'):
            HeadlessBases(self.docs).render('index.md', 'Pages.base', 'Nonexistent')

    def test_ambiguous_bases_fail(self):
        (self.docs / 'Second').mkdir()
        (self.docs / 'Second/Pages.base').write_text(self.base.read_text(), encoding='utf8')
        with self.assertRaisesRegex(PluginError, 'ambiguous'):
            HeadlessBases(self.docs).render('index.md', 'Pages.base', None)

    def test_inline_and_nested_tags_but_not_code_or_hidden_notes(self):
        (self.docs / 'Inline.md').write_text('---\nCategories: Tech\n---\n#page/subtag\n', encoding='utf8')
        (self.docs / 'Code.md').write_text('---\nCategories: Tech\n---\n```\n#page\n```\n', encoding='utf8')
        (self.docs / '.hidden').mkdir()
        (self.docs / '.hidden/Secret.md').write_text('#page\n', encoding='utf8')
        output = HeadlessBases(self.docs).render('Team Folders/Tech/Tech.md', 'Pages.base', 'ByCategory')
        self.assertIn('[Inline]', output)
        self.assertNotIn('[Code]', output)
        self.assertNotIn('Secret', output)

    def test_list_category_is_rejected_instead_of_guessing_link_semantics(self):
        (self.docs / 'Physics.md').write_text('---\ntags: [page]\nCategories: ["[[Tech]]"]\n---\n', encoding='utf8')
        with self.assertRaisesRegex(PluginError, 'must be Text'):
            HeadlessBases(self.docs).render('Team Folders/Tech/Tech.md', 'Pages.base', 'ByCategory')

    def test_recursive_boolean_filters(self):
        predicate = compile_filter({'or': ['file.hasTag("page")', {'not': ['file.name.contains("hide")']}]})
        self.assertTrue(predicate({'tags': [], 'name': 'visible'}, 'Tech'))
        self.assertFalse(predicate({'tags': [], 'name': 'hide'}, 'Tech'))
