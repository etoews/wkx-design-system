# Field

A labelled text input: the label is mono `ink-muted` above an inset (`ground`) input with a 4px radius.

**Use** a machine-readable label when the field edits a named setting (its key or path); otherwise a short plain label. Sit fields in a row with the button that commits them, bottoms aligned.

**Consumer provides** `label`, `id` (stable, for form restoration), and any native input props (`value`/`onChange` or `defaultValue`).
