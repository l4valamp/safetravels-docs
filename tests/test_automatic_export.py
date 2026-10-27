import hashlib
import json
from pathlib import Path
import tempfile
import threading
import subprocess
import shutil
import time
import unittest

from mkdocs.exceptions import PluginError
from mkdocs_databaseview_plugin.automatic_export import input_digest, read_export_state, request_export


class AutomaticExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vault = self.root / 'docs'
        self.plugin = self.vault / '.obsidian/plugins/reading-wiki-exporter'
        self.plugin.mkdir(parents=True)
        (self.plugin / 'main.js').write_text('// installed', encoding='utf-8')
        (self.vault / 'note.md').write_text('# Note', encoding='utf-8')

    def responder(self, ok=True, stale=False):
        errors = []
        def respond():
            try:
                folder = self.plugin / 'bridge/requests'
                deadline = time.monotonic() + 2
                while time.monotonic() < deadline:
                    requests = list(folder.glob('*.json'))
                    if requests:
                        request = json.loads(requests[0].read_text(encoding='utf-8'))
                        self.assertEqual(request['pages'], ['note.md'])
                        result = {'id': request['id'], 'ok': ok, 'inputDigest': 'stale' if stale else input_digest(self.vault),
                                  'error': 'Obsidian query failed'}
                        target = self.plugin / 'bridge' / requests[0].name
                        temporary = target.with_suffix('.tmp')
                        temporary.write_text(json.dumps(result), encoding='utf-8')
                        temporary.replace(target)
                        return
                    time.sleep(.01)
                raise RuntimeError('Test did not receive an export request')
            except Exception as exc:
                errors.append(exc)
        thread = threading.Thread(target=respond)
        thread.start()
        self.addCleanup(lambda: thread.join(timeout=3))
        return thread, errors

    def test_handshake_waits_for_matching_fresh_export_and_cleans_requests(self):
        thread, errors = self.responder()
        result = request_export(self.vault, ['note.md'], timeout=2)
        thread.join()
        self.assertFalse(errors)
        self.assertEqual(result['inputDigest'], input_digest(self.vault))
        self.assertFalse(list((self.plugin / 'bridge/requests').glob('*.json')))
        self.assertFalse(list((self.plugin / 'bridge').glob('*.json')))

    def test_failed_or_stale_response_stops_publishing(self):
        for ok, stale, message in ((False, False, 'query failed'), (True, True, 'Notes changed')):
            with self.subTest(ok=ok, stale=stale):
                thread, errors = self.responder(ok, stale)
                with self.assertRaisesRegex(PluginError, message):
                    request_export(self.vault, ['note.md'], timeout=2)
                thread.join()
                self.assertFalse(errors)

    def test_closed_obsidian_times_out_instead_of_using_old_snapshots(self):
        with self.assertRaisesRegex(PluginError, 'Open this project'):
            request_export(self.vault, ['note.md'], timeout=.05)

    def test_missing_plugin_explains_installation(self):
        (self.plugin / 'main.js').unlink()
        with self.assertRaisesRegex(PluginError, 'install_obsidian_exporter'):
            request_export(self.vault, ['note.md'], timeout=.05)

    @unittest.skipUnless(shutil.which('node'), 'Node.js is needed for the cross-language fingerprint check')
    def test_python_and_obsidian_use_identical_source_fingerprints(self):
        (self.vault / 'café.md').write_text('# Unicode note', encoding='utf-8')
        script = Path(__file__).resolve().parents[1] / 'plugins/obsidian-reading-wiki-exporter/exporter.js'
        code = 'require(process.argv[1]).inputDigest(process.argv[2]).then(console.log)'
        result = subprocess.run(['node', '-e', code, str(script), str(self.vault)],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), input_digest(self.vault))

    def test_manifest_metadata_must_match_atomic_manifest(self):
        manifest = b'{}\n'
        snapshot_root = self.root / 'snapshots'
        snapshot_root.mkdir()
        (snapshot_root / 'manifest.yml').write_bytes(manifest)
        state = {'manifestDigest': hashlib.sha256(manifest).hexdigest()}
        (snapshot_root / 'state.json').write_text(json.dumps(state), encoding='utf-8')
        actual, text = read_export_state(snapshot_root / 'manifest.yml')
        self.assertEqual(actual, state)
        self.assertEqual(text, '{}\n')
        (snapshot_root / 'manifest.yml').write_text('modified: true', encoding='utf-8')
        with self.assertRaisesRegex(PluginError, 'manifest changed'):
            read_export_state(snapshot_root / 'manifest.yml')


if __name__ == '__main__':
    unittest.main()
