# LogView

A mono log in an inset `ground` well that follows new lines to the bottom.

**Use** for streams people glance at: request logs, job output. Colour only the parts that carry state (status codes `good`, `caution`, `danger`) and mute timestamps and timings. Offer Pause in the footer for any live stream.

**Consumer provides** `lines` (`{id, time, parts: [{text, tone}]}` or `{text}`), `height` (default 11.5rem), `follow` (default true), `label` and an optional `footer`.
