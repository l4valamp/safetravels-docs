"""Install the local Obsidian exporter; no npm dependencies or build tools required."""
from pathlib import Path
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]


def install():
    import yaml
    config = yaml.load((ROOT / 'mkdocs.yml').read_text(encoding='utf-8-sig'), Loader=yaml.BaseLoader)
    registration = next((item for item in config.get('plugins', [])
                         if isinstance(item, dict) and 'databaseview' in item), {})
    settings = {'docs_dir': config.get('docs_dir', 'docs'), 'plugins': [
        {'databaseview': {'snapshot_manifest': registration.get('databaseview', {}).get(
            'snapshot_manifest', 'database-snapshots/manifest.yml')}}]}
    (ROOT / 'obsidian-export.json').write_text(json.dumps(settings, indent=2) + '\n', encoding='utf-8')
    vault = (ROOT / config.get('docs_dir', 'docs')).resolve()
    source = ROOT / 'plugins/obsidian-reading-wiki-exporter'
    target = vault / '.obsidian/plugins/reading-wiki-exporter'
    target.mkdir(parents=True, exist_ok=True)
    core = (source / 'exporter.js').read_text(encoding='utf-8')
    main = (source / 'main.js').read_text(encoding='utf-8')
    # Obsidian supplies its own require function; local relative modules must
    # be bundled into main.js rather than resolved from the app directory.
    bundled = '(function () { const module = { exports: {} };\n' + core + '\nreturn module.exports; })()'
    main = main.replace("require('./exporter')", bundled)
    (target / 'main.js').write_text(main, encoding='utf-8')
    shutil.copyfile(source / 'manifest.json', target / 'manifest.json')
    return target


if __name__ == '__main__':
    print(f'Installed {install()}')
