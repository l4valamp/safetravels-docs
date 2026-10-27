import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import Abort
from mkdocs_databaseview_plugin.automatic_export import input_digest


class CommittedExportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = self.root / 'docs'
        self.docs.mkdir()
        (self.docs / 'index.md').write_text('# Home\n![[Pages.base]]\n[[Other]]\n![[pic.png|120]]\n', encoding='utf8')
        (self.docs / 'Other.md').write_text('# Other\n', encoding='utf8')
        (self.docs / 'pic.png').write_bytes(b'fixture')
        self.snapshot = self.root / 'rows.md'
        self.snapshot.write_bytes(b'| Name |\n| --- |\n| [[Other]] |\n')
        manifest = 'index.md:\n  Pages.base: rows.md\n'
        (self.root / 'manifest.yml').write_bytes(manifest.encode())
        self.state = {
            'contentDigest': input_digest(self.docs, content_only=True),
            'manifestDigest': hashlib.sha256(manifest.encode()).hexdigest(),
            'hashes': {'rows.md': hashlib.sha256(self.snapshot.read_bytes()).hexdigest()},
        }
        (self.root / 'state.json').write_text(json.dumps(self.state), encoding='utf8')
        (self.root / 'mkdocs.yml').write_text(
            'site_name: Test\nsite_url: https://l4valamp.github.io/safetravels-docs/\n'
            'plugins:\n  - databaseview:\n      committed_export: true\n'
            '      snapshot_manifest: manifest.yml\n', encoding='utf8')

    def build(self):
        build(load_config(str(self.root / 'mkdocs.yml')), dirty=False)

    def test_checkout_timestamps_and_line_endings_do_not_stale_export(self):
        for file in self.docs.glob('*.md'):
            file.write_bytes(file.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
            os.utime(file, (1000000, 1000000))
        self.build()
        html = (self.root / 'site/index.html').read_text(encoding='utf8')
        self.assertIn('/safetravels-docs/Other/', html)
        self.assertIn('width="120"', html)
        self.assertNotIn('![[', html)

    def test_changed_note_stops_build(self):
        (self.docs / 'Other.md').write_text('# Changed\n', encoding='utf8')
        with self.assertLogs('mkdocs', level='ERROR') as logs:
            with self.assertRaises(Abort):
                self.build()
        self.assertIn('stale', str(logs.output))

    def test_changed_snapshot_stops_build(self):
        self.snapshot.write_text('Tampered rows\n', encoding='utf8')
        with self.assertLogs('mkdocs', level='ERROR') as logs:
            with self.assertRaises(Abort):
                self.build()
        self.assertIn('does not match', str(logs.output))

    def test_javascript_and_python_content_hashes_match(self):
        script = "require('./plugins/obsidian-reading-wiki-exporter/exporter').inputDigest(process.argv[1], true).then(console.log)"
        output = subprocess.check_output(['node', '-e', script, str(self.docs)], text=True)
        self.assertEqual(output.strip(), self.state['contentDigest'])
