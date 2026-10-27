"""Save an Obsidian Markdown table from stdin or a file; never evaluate Bases."""
import argparse
import re
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='List all configured snapshots and their status')
    parser.add_argument('--page', help='Source page, e.g. books/index.md')
    parser.add_argument('--embed', help='Embed reference, e.g. Books.base or Books.base#OnTopicPage')
    parser.add_argument('--file', type=Path, help='Read an exported Markdown file instead of stdin')
    args = parser.parse_args()
    config = yaml.load((ROOT / 'mkdocs.yml').read_text(encoding='utf-8-sig'), Loader=yaml.BaseLoader)
    settings = next((entry['databaseview'] or {} for entry in config['plugins']
                     if isinstance(entry, dict) and 'databaseview' in entry), {})
    manifest_path = ROOT / settings.get('snapshot_manifest', 'database-snapshots/manifest.yml')
    directory = manifest_path.resolve().parent
    manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8-sig'))
    if args.list:
        for page, views in manifest.items():
            for embed, relative in views.items():
                status = 'saved' if (directory / relative).is_file() else 'MISSING'
                print(f'{status}: {page} | {embed} -> {relative}')
        return
    if not args.page or not args.embed:
        parser.error('--page and --embed are required unless --list is used')
    relative = manifest.get(args.page, {}).get(args.embed)
    if not isinstance(relative, str):
        parser.error('This page/embed is not mapped in the snapshot manifest; add it first.')
    target = (directory / relative).resolve()
    if directory not in target.parents:
        parser.error('Snapshot path must stay inside the manifest directory.')
    text = args.file.read_text(encoding='utf-8-sig') if args.file else sys.stdin.read()
    if not text.strip():
        parser.error('Nothing to save. Copy the rendered table, or supply an explicit No results. message.')
    if re.search(r"!\[\[[^\]]+\.base(?:#[^\]]*)?\]\]", text, re.IGNORECASE):
        parser.error('Input still contains a Base embed. Copy the rendered table, not the source embed.')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
    print(f'Saved {target}')


if __name__ == '__main__':
    main()
