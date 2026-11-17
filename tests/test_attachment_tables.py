import unittest
from types import SimpleNamespace

import markdown
from mkdocs_databaseview_plugin.plugin import NoteLinksExtension


class AttachmentTablesTest(unittest.TestCase):
    def test_table_sizes_and_code_examples(self):
        plugin = SimpleNamespace(
            files=[SimpleNamespace(src_uri='Assets/Passenger image.png')],
            current_page='Passengers/Body Bag.md',
        )
        for suffix, attributes in [('', ''), (r'\|234', 'width="234"'),
                                   (r'\|234x120', 'height="120"')]:
            with self.subTest(suffix=suffix):
                embed = '![[Passenger image.png' + suffix + ']]'
                html = markdown.markdown(
                    '| Appearance |\n| --- |\n| ' + embed + ' |\n\n`' + embed + '`',
                    extensions=['tables', NoteLinksExtension(plugin)],
                )
                self.assertEqual(html.count('<img '), 1)
                self.assertIn('src="../Assets/Passenger%20image.png"', html)
                self.assertIn(attributes, html)
                self.assertIn('<code>![[Passenger image.png', html)
