from pathlib import Path
import tempfile
import unittest

from mkdocs.commands.build import build
from mkdocs.config import load_config


class BackgroundOverrideTest(unittest.TestCase):
    def test_background_is_page_specific(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            overrides = Path(__file__).resolve().parents[1] / 'overrides'
            (root / 'mkdocs.yml').write_text(
                'site_name: Background test\nplugins: []\ntheme:\n'
                f'  name: material\n  custom_dir: {overrides.as_posix()}\n', encoding='utf8')
            for name, metadata in {
                'index': '',
                'custom': 'override background image url: https://example.com/scene.png?x=1&y=2',
                'empty': 'override background image url: ',
                'invalid': 'override background image url: javascript:alert(1)',
                'escaped': 'override background image url: https://example.com/</style><script>.png',
            }.items():
                (root / 'docs' / f'{name}.md').write_text(
                    f'---\n{metadata}\n---\n# Example\n', encoding='utf8')
            build(load_config(str(root / 'mkdocs.yml'), strict=True))
            for name in ('index', 'empty', 'invalid'):
                path = root / 'site' / ('index.html' if name == 'index' else f'{name}/index.html')
                self.assertNotIn('--rv-background-image:', path.read_text(encoding='utf8'))
            custom = (root / 'site/custom/index.html').read_text(encoding='utf8')
            self.assertIn('--rv-background-image: url("https://example.com/scene.png', custom)
            self.assertIn(r'x=1\000026y=2', custom)
            escaped = (root / 'site/escaped/index.html').read_text(encoding='utf8')
            self.assertNotIn('</style><script>', escaped)
