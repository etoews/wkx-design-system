# DataTable

A mono table with condensed uppercase column heads and hairline row dividers, which can sort by any column and filter its rows.

**Use** for event histories and records people scan by column. Write the outcome as a word and tone it `good`, `caution` or `danger`; tone timestamps and notes `muted` so the identifiers stand out. It scrolls sideways inside its own wrapper on narrow screens.

**Sort.** With `sortable`, each column head is a button. A click sorts ascending (▲), then descending (▼), then returns the rows to the order you gave. The sorted head steps up to `ink` and carries `aria-sort`; on any other head the triangle shows faintly on hover or focus. Numbers sort as numbers, words in natural order, and blanks (`—`, `·`) go last either way. Mark number columns `num` so they right-align.

**Filter.** With `filterable`, a pill sits above the table on the right. A row stays when any cell's text contains the filter, ignoring case. The `N of M` count appears to the left of the pill, so the pill never moves as you type. When nothing matches, the table says so in one muted row.

**Consumer provides** `columns` (`{key, label, num?, sortable?}`), `rows` (objects keyed by column, with optional `id`, `tones`, `sorts` and `search` per row), and an optional `caption`. Give `sorts` when a cell's text does not sort right (a date shown as `18 Jul 14:32`), and `search` when a cell is not plain text. To keep sort or filter across visits, control them with `sort` / `onSortChange` and `filter` / `onFilterChange`; otherwise set `defaultSort` / `defaultFilter`.

**Don't** zebra-stripe, box cells, or centre text. Don't filter a table of a handful of rows: the pill earns its place at about a dozen.
