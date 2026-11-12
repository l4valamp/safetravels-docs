# Safe Travels Documentation

Write in Obsidian, sync to GitHub, and let GitHub Actions publish the website.
Teammates do not need Python, MkDocs, an exporter, or local build commands.

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

## How database views are published

`databaseview.headless: true` generates the current Bases table and card views directly
from committed notes on every build. No snapshot files or Obsidian installation
are required. Category membership uses the existing Text `Categories` property
and `this.file.name` context. Team pages share the `Pages.base#ByCategory` card
view. Cards show only the page title and its `header image url` cover; the
basic page template supplies the default game screenshot. Card titles reserve
two lines and truncate longer names with an ellipsis; the full name remains
available to screen readers and on hover.

This is a deliberately limited server-side adapter, not all of Obsidian Bases.
It supports the current tag/name filters, boolean filter groups, Text category
containment, table columns, display names, and title/image cards. Rows are ordered by note name.
Formulas, custom sorts, grouping, summaries, limits, other view types, and list
category comparisons fail clearly instead of silently changing results. Have a
maintainer extend and test the adapter before adding those Base features.
Details: [plugin README](plugins/databaseview-plugin/README.md).

The native exporter source and historical snapshots remain for reference, but
are not used for team publication. The companion is no longer enabled in shared
settings. If it is still active in an already-open Obsidian window, disable
**Reading Wiki Exporter** once; teammates never need to install it.

## Visual theme

Home and the five team navigation tabs link directly to the homepage and
the landing notes inside their matching `docs/Team Folders` directories. Other notes, including reusable snippets, stay available
through existing links and search without cluttering the navigation.

Rearview uses Material's existing slate palette, navigation, search, tabs and
callouts. `docs/stylesheets/rearview.css` contains the color tokens and visual
rules, loaded after the original entity stylesheet. `overrides/main.html` adds
the homepage wrapper automatically; regular Obsidian notes need no extra HTML,
classes or front matter. Existing embeds resize to fit mobile screens.

To override the fixed background on one page, add this Text property to the
note's YAML front matter (or Obsidian Properties):

```yaml
override background image url: "https://example.com/background.png"
```

Use a direct HTTP or HTTPS image URL. The existing gradient and content opacity
still apply. Removing the property or leaving it empty restores the default
background; other pages keep their own backgrounds.

Display headings use locally installed Georgia/Times with serif
fallbacks; body and code use system sans-serif and monospace stacks. No font
files are redistributed or downloaded, and appearance varies slightly by OS.
The pitch and art-bible embeds are retained. The supplied slide images inform
the wide, heavy headings, charcoal, aged cream, muddy brown and orange-red
accents. No unverified stock or reference art is used as a homepage background.

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
