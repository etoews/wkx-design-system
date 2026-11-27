# Panel

The container for one job on a page: `surface` fill, a 1px `line` border, 6px corners, no shadow.

**Variants.** Default panels open with a `SectionLabel` (`label`, optional `labelCode`). A `ruled` panel carries a 3px `ink-muted` top rule with square top corners and a mono `title` plus `aside` head: use it for top-level groups, such as one per environment or location.

**Layout.** Put panels in a `.wkx-grid` (two columns, `space-6` gap, stacking below 860px); `wide` spans the full row. On wide screens, let more panels share a row rather than stretching prose: keep prose under `prose-max`.

**Consumer provides** children, and `label` or `title`.

**Don't** nest panels, add shadows, or colour a panel's border by status: status lives in lights and words.
