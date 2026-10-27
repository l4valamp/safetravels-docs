# MkDocs databaseview plugin

Publishes exported Obsidian Markdown tables in place of `.base` embeds and resolves in-page Obsidian wikilinks. No Bases expression evaluator is included.

```yaml
plugins:
  - databaseview:
      auto_export: true
      snapshot_manifest: database-snapshots/manifest.yml
      export_timeout: 90
```

The Obsidian companion creates snapshots and mappings automatically. MkDocs waits for a fresh export before building and verifies source and snapshot hashes. Requires the companion plugin enabled in the running local `docs` vault. See `database-snapshots/README.md` for setup and normal usage.

For intentional manual/offline snapshots, omit `auto_export` or set it to `false`; the manifest must then already exist and map source page + exact embed to a Markdown snapshot. Missing snapshots stop either kind of build.
