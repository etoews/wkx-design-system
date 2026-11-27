# DataTable

A mono table with condensed uppercase column heads and hairline row dividers.

**Use** for event histories and records people scan by column. Write the outcome as a word and tone it `good`, `caution` or `danger`; tone timestamps and notes `muted` so the identifiers stand out. It scrolls sideways inside its own wrapper on narrow screens.

**Consumer provides** `columns` (`{key, label}`), `rows` (objects keyed by column, with optional `id` and `tones` per column), and an optional `caption`.

**Don't** zebra-stripe, box cells, or centre text.
