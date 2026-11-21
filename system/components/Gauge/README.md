# Gauge

A key, a big mono figure with its unit, one line of detail, and an optional `Meter`.

**Use** in a `.wkx-gauges` row (four-up, two-up below 860px) for the handful of numbers someone checks first. The figure is `ink-strong`; the unit and detail drop to `ink-muted`.

**Consumer provides** `label`, `value` (a string, already formatted), `unit`, `detail`, and for a meter `percent` (0–100), `threshold` (where the tick sits) and `tone` (`good`, `caution`, `danger`) chosen by the app from that threshold.

**Write** a space between a number and its unit (`6 %`, `4 h 38 m`), and say what the figure means in the detail line rather than repeating the key.
