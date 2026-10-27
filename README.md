# Safe Travels Documentation

Write in Obsidian, sync to GitHub, and let GitHub Actions publish the website.
Teammates do not need Python, MkDocs, an exporter, or local build commands.

- [Team setup and daily workflow](docs/Team%20Guide.md)
- Website: https://l4valamp.github.io/safetravels-docs/
- Publishing branch: `main`

## Maintainer setup on GitHub

1. Give teammates write access to this repository (or use reviewed pull requests
   if branch protection requires them). They need access before cloning/pushing.
2. Under **Settings > Pages > Build and deployment**, choose **GitHub Actions**.
3. Under **Settings > Actions > General**, allow the actions referenced by
   `.github/workflows/deploy-docs.yml`. No personal access token or Pages secret
   is needed: deployment uses GitHub's short-lived built-in token.
4. If the `github-pages` environment restricts deployment branches, allow `main`.
   Required reviewers will add a manual approval step; omit that requirement for
   fully automatic publication.
5. Review and commit this change, then push normally. A push to `main` runs the
   build and deploys only if tests and the strict MkDocs build pass. Pull requests
   run validation without deploying. Never force-push to resolve sync problems.

The workflow runs on clean Ubuntu with Python 3.12 and Node 24. It installs both
local Python plugins from this repository. Build permissions are read-only;
only the deploy job receives Pages and OIDC write permissions. Existing Git
history and the old `gh-pages` branch are retained.

## How tables are published

`databaseview.headless: true` generates the current Bases table views directly
from committed notes on every build. No snapshot files or Obsidian installation
are required. Category membership uses the existing Text `Categories` property
and `this.file.name` context. All eight existing tables matched the last native
Obsidian export exactly during validation.

This is a deliberately limited server-side adapter, not all of Obsidian Bases.
It supports the current tag/name filters, boolean filter groups, Text category
containment, table columns, and display names. Rows are ordered by note name.
Formulas, custom sorts, grouping, summaries, limits, non-table views, and list
category comparisons fail clearly instead of silently changing results. Have a
maintainer extend and test the adapter before adding those Base features.
Details: [plugin README](plugins/databaseview-plugin/README.md).

The native exporter source and historical snapshots remain for reference, but
are not used for team publication. The companion is no longer enabled in shared
settings. If it is still active in an already-open Obsidian window, disable
**Reading Wiki Exporter** once; teammates never need to install it.

## Optional developer checks

These commands are for maintainers, not teammates:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test plugins/obsidian-reading-wiki-exporter/exporter.test.js plugins/obsidian-reading-wiki-exporter/main.test.js
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

See [MIGRATION.md](MIGRATION.md) for preserved content and validation details.
