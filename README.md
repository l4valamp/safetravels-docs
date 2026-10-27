# Safe Travels Documentation

Obsidian notes published with MkDocs Material at https://l4valamp.github.io/safetravels-docs/.
The Obsidian vault is **docs/**; the parent folder is the Git repository.

## Setup and preview

From this repository in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/install_obsidian_exporter.py
```

Open `docs` as the vault in desktop Obsidian 1.10 or newer. Enable Bases and
**Reading Wiki Exporter** in Community plugins. Keep this vault open when building.
Rerun the installer and toggle the companion off/on after updating its source or
changing `docs_dir` or `snapshot_manifest`. The installer extracts those settings
to `obsidian-export.json` because Obsidian cannot interpret MkDocs' Python YAML tags.

```powershell
.\.venv\Scripts\python.exe -m mkdocs serve
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

Obsidian evaluates Bases filters, formulas, groups, and page context. The companion
exports the results automatically; MkDocs requests a fresh export before building.
Missing exports stop the build. Templates remain in the vault but are excluded
from the published site. Note links, table views, and image embeds are supported;
book cards are available in the plugin but are not enabled for this documentation.
The existing entity syntax, Material theme, CSS, and JavaScript remain in place.

## Publish with GitHub Actions

1. In the repository's **Settings > Pages > Build and deployment**, choose
   **GitHub Actions** as the source. This replaces branch-based publishing; the
   existing `gh-pages` branch is left intact.
2. With the `docs` vault open and the exporter enabled, run the strict local build.
3. Review `git status` and `git diff`. Include the intended note moves, new notes,
   configuration, plugin source, tools, tests, `obsidian-export.json`, and
   `database-snapshots/` in your commit. Do not commit `.venv`, installed plugin
   files, or `site/`. Review existing deletions before staging them.
4. Commit and push normally to `main`. The **Deploy Documentation** workflow
   validates the exports, builds the site, and deploys a Pages artifact. It never
   force-pushes. You can also run the workflow manually from Actions.

GitHub cannot run desktop Obsidian. CI therefore uses committed snapshots and
checks their source-content fingerprint plus manifest and snapshot hashes.
Editing, adding, deleting, or renaming a note or Base requires another local build
and a commit containing both notes and refreshed snapshots. Windows/Linux checkout
timestamps and CRLF/LF conversion do not invalidate the source fingerprint.
Snapshot files use LF through `.gitattributes` to preserve export hashes.

To test the same mode locally after a successful live build:

```powershell
$env:OBSIDIAN_AUTO_EXPORT = 'false'
$env:OBSIDIAN_COMMITTED_EXPORT = 'true'
try { .\.venv\Scripts\python.exe -m mkdocs build --strict }
finally {
  Remove-Item Env:OBSIDIAN_AUTO_EXPORT, Env:OBSIDIAN_COMMITTED_EXPORT
}
```

## Tests

```powershell
node --test plugins/obsidian-reading-wiki-exporter/exporter.test.js plugins/obsidian-reading-wiki-exporter/main.test.js
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

See [MIGRATION.md](MIGRATION.md) for the initial repository inspection and preserved
working changes. Nothing is published by installing or building locally.
