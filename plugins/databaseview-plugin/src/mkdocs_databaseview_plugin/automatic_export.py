"""File-based request bridge to the running Obsidian companion plugin."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
import uuid

from mkdocs.exceptions import PluginError

PLUGIN_ID = 'reading-wiki-exporter'


def input_digest(vault_root, content_only=False):
    entries = []
    for path in Path(vault_root).rglob('*'):
        relative = path.relative_to(vault_root)
        if any(part.startswith('.') for part in relative.parts):
            continue
        if path.is_file() and path.suffix.lower() in ('.md', '.base'):
            data = path.read_bytes()
            if content_only:
                data = data.replace(b'\r\n', b'\n')
            digest = hashlib.sha256(data).hexdigest()
            entries.append((relative.as_posix(), digest, '' if content_only else str(path.stat().st_mtime_ns)))
    result = hashlib.sha256()
    for name, digest, modified in sorted(entries, key=lambda entry: entry[0].encode('utf-8')):
        result.update((name + '\0' + digest + '\0' + modified + '\n').encode('utf-8'))
    return result.hexdigest()


def request_export(vault_root, pages, timeout=90):
    bridge = Path(vault_root) / '.obsidian/plugins' / PLUGIN_ID / 'bridge'
    installed = bridge.parent / 'main.js'
    if not installed.is_file():
        raise PluginError('Install the Obsidian exporter with .venv/Scripts/python.exe '
                          'tools/install_obsidian_exporter.py and enable Reading Wiki Exporter in Obsidian.')
    request_id = str(uuid.uuid4())
    requests = bridge / 'requests'
    requests.mkdir(parents=True, exist_ok=True)
    request = requests / (request_id + '.json')
    response = bridge / (request_id + '.json')
    temporary = request.with_suffix('.tmp')
    temporary.write_text(json.dumps({'id': request_id, 'createdAt': int(time.time() * 1000),
                                      'pages': list(pages)}), encoding='utf-8')
    temporary.replace(request)
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            if response.is_file():
                try:
                    result = json.loads(response.read_text(encoding='utf-8'))
                except (PermissionError, FileNotFoundError):
                    # Windows/OneDrive may briefly hold a just-renamed file.
                    time.sleep(0.1)
                    continue
                if not result.get('ok'):
                    raise PluginError('Obsidian export failed: ' + result.get('error', 'Unknown error'))
                if result.get('id') != request_id:
                    raise PluginError('Obsidian returned the wrong export request ID.')
                if result.get('inputDigest') != input_digest(vault_root):
                    raise PluginError('Notes changed during export; rerun the MkDocs build.')
                return result
            time.sleep(0.1)
        raise PluginError('Automatic database export timed out. Open this project\'s docs vault in Obsidian '
                          'and enable Reading Wiki Exporter, then run the build again. '
                          'No stale database results were published.')
    finally:
        request.unlink(missing_ok=True)
        response.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)


def read_export_state(manifest_path):
    """Read a consistent manifest/state pair even as an auto-export finishes."""
    manifest_path = Path(manifest_path)
    state_path = manifest_path.parent / 'state.json'
    for attempt in range(20):
        try:
            state = json.loads(state_path.read_text(encoding='utf-8'))
            manifest = manifest_path.read_bytes()
        except (OSError, ValueError) as exc:
            if attempt == 19:
                raise PluginError(f'Cannot read automatic export metadata: {exc}') from exc
        else:
            if hashlib.sha256(manifest).hexdigest() == state.get('manifestDigest'):
                return state, manifest.decode('utf-8-sig')
        time.sleep(0.05)
    raise PluginError('Snapshot manifest changed during export; rerun the build.')
