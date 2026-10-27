# Reading Wiki functionality migration

## Inspection on 2026-10-27

**Current workflow:** the native-snapshot setup recorded below has been superseded
for Safe Travels by `databaseview.headless: true`. See the root README and
`docs/Team Guide.md` for current instructions. Teammates clone, open `docs`, enable
Obsidian Git, and write/sync. No exporter, Python, or local build is required.
ReadingWiki itself remains unchanged.

The team adapter supports the limited table/filter subset used by the embedded
category views. All eight tables matched the last native exports exactly, ignoring
trailing whitespace. Unsupported features stop the build. The new, unembedded
`docs/Bases/TechPages.base` cards view was left untouched; cards and folder filters
would require adapter support before embedding it in a published note.

Actions now validates pull requests and builds/deploys pushes to `main`, using a
Pages artifact and separate minimal deployment permissions. Dependencies list
direct packages and both local plugins. Existing notes, the theme, entity plugin,
site URL, branches, and history are preserved. In-progress Art note edits and new
Bases files were left untouched.

The shared exporter enablement was removed. Native snapshots remain as historical
artifacts and are not used by team builds. Already-running Obsidian windows may
still export until the companion is disabled there. Personal Git plugin files
and settings are ignored; credentials are never stored in the repository.

Current validation: 26 Python tests and 9 JavaScript tests pass. A fresh virtual
environment installed both local plugins as packaged wheels and passed dependency
checks, tests, and a strict full-site build in an isolated copy with no `.git`,
`.obsidian`, snapshots, or reference to ReadingWiki. This machine uses Windows
and Python 3.14; the actual Ubuntu/Python 3.12 Actions run remains to be verified
after review and push. No changes were pushed or remotely triggered by this work.

The remaining sections record the initial inspection and native-export history.

`C:\Users\Greta\Vaults\safetravels-docs` is a complete Git repository, including
its `.git` history, MkDocs configuration, local entity plugin, and GitHub Actions
workflow. This was a move of the whole repository, not only the Obsidian vault.
The content vault is the nested `docs` directory. Additional `.obsidian` folders
exist at the repository root and under `.github`; those were left untouched.

The origin fetch and push URL is correctly set to
`https://github.com/l4valamp/safetravels-docs.git`. A read-only remote check found
`main` and local HEAD both at `c2bd49d88d41b0e1062d13fc5733e29d0d329ce1`.
The existing published branch is `gh-pages` at
`13eaf324c00dd4149dc0501cbe5b500ee8ed1e0f`. No branch was pushed or rewritten.

The source project is the adjacent `ReadingWiki` repository, whose origin is
`https://github.com/l4valamp/reading-wiki.git`. Its current working tree includes
uncommitted plugin changes, book-card support, styling, book metadata updates,
new assets, and deleted/moved Copilot skill files. The current plugin source,
including untracked `book_cards.py`, was copied; ReadingWiki was not edited.

## Existing work preserved

Safe Travels already had uncommitted vault settings, homepage and template edits,
new team pages, Bases and templates, and reorganized notes under `Team Folders`.
Git reports the old `All Team`, `Art`, `Design`, and `Tech` paths as deleted and
the new paths as untracked until the moves are staged. The pasted image moved to
`docs/Assets`. There is also an untracked root `Untitled.md`, and pre-existing
entity-plugin build/package metadata. None of these were reverted or cleaned up.

Some old tracked pages have no exact replacement path in the new tree, including
the hub pages and Architecture Overview. These deletions predate this work; inspect
them before committing. Git history retains the originals. The homepage still
contains links using the former hub names, and some referenced notes
are absent. Unresolved wiki links/images remain readable labels; no replacement
notes or fabricated database results are created.

## Files carried over and adaptations

| Area | Implementation |
| --- | --- |
| MkDocs plugin | `plugins/databaseview-plugin/`: snapshot tables, context-specific views, note links, optional book-card renderer |
| Obsidian companion | `plugins/obsidian-reading-wiki-exporter/`: automatic native Bases exports and build request bridge |
| Tools | Installer and optional manual snapshot helper in `tools/` |
| Tests | Source plugin tests plus committed-export integrity and cross-platform fingerprint tests |
| Dependencies | Existing pinned Safe Travels requirements retained, local databaseview package added; UTF-16 requirements converted to UTF-8; roamlinks removed because it rewrites wiki syntax before the new renderer |
| MkDocs settings | Explicit `docs_dir`, native snapshot exporter, environment-controlled committed-export mode, templates excluded, duplicate superfences declaration removed |
| Attachments | Image wikilinks and optional dimensions handled by the new renderer alongside note links |
| CI | Existing workflow replaced with build/test and artifact-based Pages deployment, without force-push |
| Export portability | Content fingerprints ignore checkout timestamps and normalize CRLF; manifest and snapshot hashes verified; `.gitattributes` keeps snapshot files LF |
| Documentation | Setup, validation, preview, and publication steps in `README.md` |

Safe Travels keeps its existing name, Material theme, slate/amber/deep-orange
palette, navigation behavior, Markdown extensions, entity plugin, CSS, JavaScript,
and site URL `https://l4valamp.github.io/safetravels-docs/`. Reading Wiki's fonts,
library styling, homepage, books, and card-view configuration were not copied.

Snapshot exports must be committed for GitHub Actions, unlike ReadingWiki's
local-only workflow. CI rejects missing, stale, or tampered snapshots. The local
default still requests fresh exports from the open Obsidian vault.

Publication requires selecting **GitHub Actions** in repository Settings > Pages
and pushing reviewed changes to `main`. Existing `gh-pages` history is retained.
See `README.md` for the complete workflow.

## Validation status

All 18 Python tests and all 9 JavaScript tests pass. Coverage includes snapshot
tables and links, native exporter behavior, freshness, tamper rejection, image
embeds, and cross-language fingerprints on Windows/Linux-style checkout changes.
`git diff --check` found no whitespace errors.

After enabling the companion, the strict full-site live build passed and exported
eight real native Bases views. A second strict build using committed-export mode
also passed, verifying the same workflow used by GitHub Actions without requesting
another Obsidian export. Generated tables and their integrity metadata are in
`database-snapshots/`; built HTML is in the ignored `site/` directory.

MkDocs reports the existing `Car Controller` Markdown link in `Team Pages/Tech.md`
as unrecognized. Old homepage hub names also remain unresolved wiki labels. These
pre-existing content issues were preserved and do not prevent the strict build.
No commits, pushes, Pages settings changes, or deployments were performed.
