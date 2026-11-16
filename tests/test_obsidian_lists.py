import unittest
from types import SimpleNamespace

import markdown
from mkdocs_databaseview_plugin.plugin import NoteLinksExtension


class ObsidianListsTest(unittest.TestCase):
    def render(self, source):
        return markdown.markdown(source, extensions=[
            'pymdownx.superfences', NoteLinksExtension(SimpleNamespace())])

    def test_lists_after_paragraphs_keep_nested_items(self):
        html = self.render('**PRIORITY 1:**\n- Car\n\t- Description\n- Roads\n\n'
                           '**PRIORITY 2:**\n- Story\n\nSteps:\n1. First\n2. Second')
        self.assertEqual(html.count('<ul>'), 3)
        self.assertEqual(html.count('<ol>'), 1)
        self.assertIn('<li>Car<ul>', html)
        self.assertIn('<li>Description</li>', html)
        self.assertNotIn('PRIORITY 1:</strong>\n-', html)

    def test_code_and_html_remain_literal(self):
        html = self.render('```text\nLabel\n- example\n```\n\n'
                           '    Label\n    - example\n\n'
                           '<div>\nLabel\n- example\n</div>')
        self.assertNotIn('<ul>', html)
        self.assertIn('Label\n- example\n</div>', html)
