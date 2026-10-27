# Reading Wiki Exporter for Obsidian

Desktop companion to the MkDocs databaseview plugin. It uses Obsidian's public BasesView API to capture evaluated table results automatically. It does not implement any filter or formula evaluator.

Install from the project root:

```powershell
.\.venv\Scripts\python.exe tools/install_obsidian_exporter.py
```

Enable Reading Wiki Exporter in the `docs` vault's Community plugins. The plugin exports on startup and note/Base changes. MkDocs also requests an export before each build through a local file-based bridge. Obsidian must be running; no browser automation or CLI is needed.

See `database-snapshots/README.md` for the complete workflow. The command palette also includes **Reading Wiki Exporter: Export all database views now**, for diagnostics; normal editing requires no export command.

Source files are bundled into the installed `main.js` by the Python installer, without npm or third-party runtime dependencies.
