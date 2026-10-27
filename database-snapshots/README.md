# Native Obsidian Bases snapshots

The companion plugin evaluates each embedded Base inside Obsidian, with the
embedding note as `this`. It exports all rows, groups, formulas, and summaries
as static Markdown tables. MkDocs does not reinterpret Bases filters.

Enable Bases and Reading Wiki Exporter in the project's `docs` vault, and keep
that vault open. Run from the repository root:

```powershell
.\.venv\Scripts\python.exe tools/install_obsidian_exporter.py
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

After installing or updating the companion, toggle it off/on in Obsidian.

A successful export writes `manifest.yml`, `state.json`, and immutable files in
`generated/<generation>/`. Commit these files with the matching notes. They are
outside the vault so that snapshot tables never appear in their own databases.
The installed companion and its temporary request bridge are ignored by Git.

Local builds request a fresh export. GitHub Actions uses committed exports,
validates the note/Base content fingerprint and manifest/snapshot hashes, and
rejects stale or missing data. Run another local live build after changing notes.
Only a successful complete generation should be committed. Previous generations
can be removed after confirming no manifest refers to them; no automatic cleanup
is performed.

Only native table views are supported. New embeds are discovered automatically.
Templates are excluded from publishing but remain available to resolve embedded
Bases. A Base under Templates/Bases therefore still works in published notes.

The manual `tools/save_database_snapshot.py` helper is retained for deliberate
manual/offline use. It does not generate freshness metadata for normal CI.
See the root README for preview, tests, and publication instructions.
