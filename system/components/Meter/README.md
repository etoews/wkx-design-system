# Meter

A 6px track in `surface-raised` with a fill and a hairline threshold tick.

**Tone** is the app's judgement, not the meter's: pass `good` (default, `accent`), `caution` or `danger` once the value crosses the line you care about, and place `threshold` at that line so the reader can see the margin.

**Consumer provides** `value` (0–100), optional `threshold` (0–100), `tone` and an accessible `label`.
