# DataTable

A mono table with condensed uppercase column heads and hairline row dividers, which can sort by any column, filter its rows and hide columns.

**Use** for event histories and records people scan by column. Write the outcome as a word and tone it `good`, `caution` or `danger`; tone timestamps and notes `muted` so the identifiers stand out.

**Sort.** With `sortable`, each column head is a button. A click sorts ascending (▲), then descending (▼), then returns the rows to the order you gave. The sorted head steps up to `ink` and carries `aria-sort`; on any other head the triangle shows faintly on hover or focus. Numbers sort as numbers, words in natural order, and blanks (`—`, `·`) go last either way. Mark number columns `num` so they right-align.

**Filter.** With `filterable`, a pill sits above the table on the right. A row stays when any visible cell's text contains the filter, ignoring case, and each match in a plain-text cell is marked with `highlight`. The `N of M` count appears to the left of the pill, so the pill never moves as you type. When nothing matches, the table says so in one muted row.

**Columns.** With `hideable`, a `columns ▾` pill sits to the right of the filter and drops a checklist of the columns. A `locked` column stays shown, and the last visible column can't be hidden. A hidden column is outside the filter's reach. The menu closes on a click outside it or Escape.

**Sticky heads.** The column heads stick to the top of the screen as a long table scrolls past, on a `surface` ground. Under a fixed page header, set `stickyTop` to its height. Below `breakpoint-stack` the table scrolls sideways inside its own wrapper instead.

**Consumer provides** `columns` (`{key, label, num?, sortable?, locked?}`), `rows` (objects keyed by column, with optional `id`, `tones`, `sorts` and `search` per row), and an optional `caption`. Give `sorts` when a cell's text does not sort right (a date shown as `18 Jul 14:32`), and `search` when a cell is not plain text. To keep sort, filter or hidden columns across visits, control them with `sort` / `onSortChange`, `filter` / `onFilterChange` and `hidden` / `onHiddenChange`; otherwise set `defaultSort`, `defaultFilter` and `defaultHidden`.

**Don't** zebra-stripe, box cells, or centre text. Don't filter a table of a handful of rows: the pill earns its place at about a dozen. Put a table in a `Panel`, so its sticky heads match the ground behind them.
