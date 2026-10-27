# MkDocs databaseview plugin

Safe Travels uses `headless: true`: every server-side build generates tables and cards
from the committed notes and `.base` files. There is no dependency on desktop
Obsidian, local builds, generated snapshots, or installed Obsidian plugins.

```yaml
plugins:
  - databaseview:
      headless: true
```

## Supported team Bases subset

- Visible Markdown files, YAML properties, and frontmatter/inline tags.
- `file.hasTag("page")`, including nested tags; `file.name.contains("text")`.
- `!`, and recursive `and`, `or`, `not` filter groups.
- `Categories.contains(this.file.name.toString())`, with Categories stored as Text.
- Global plus selected-view filters; default first view or exact named view.
- Table views with `order` columns (`file.name` and note properties), display names,
  and column widths (widths are presentation-only and ignored on the website).
- Stable rows ordered by case-insensitive filename, then path; empty tables.
- Cards views displaying only `file.name`, with a remote HTTP(S) note-image
  property, `cardSize`, `imageAspectRatio`, and `imageFit` (cover or contain).
  Missing or invalid image URLs use the default Rearview screenshot. Empty
  categories show a short message. Native Obsidian Cards uses the same Base;
  the website applies uniform dimensions and two-line title ellipses through CSS.
- Case-insensitive Base lookup with ambiguity rejection.

Unsupported expressions/settings stop the build. No `eval` or arbitrary code
execution is used. Formulas, custom sorts, groups, summaries, limits, other view
types, and list category comparisons require a maintainer change with tests.
This is a supported subset, not a complete replica of Obsidian's query engine.
See the official [Bases syntax](https://obsidian.md/help/bases/syntax) and
[function reference](https://obsidian.md/help/bases/functions).

Wikilinks, headings, aliases, image embeds/dimensions, and optional book cards
are retained from the Reading Wiki implementation. Safe Travels keeps its
existing Material theme and entity plugin.

## Optional legacy modes

The plugin also retains native snapshot modes for deliberate maintainer use:
`auto_export: true` requests a live export from the companion in desktop Obsidian;
`committed_export: true` validates previously committed native exports. With
neither flag, manual snapshots can be mapped by `snapshot_manifest`.
Do not combine those modes with `headless`. The team's normal workflow needs
none of them. ReadingWiki itself was not modified.
