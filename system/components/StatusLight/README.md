# StatusLight

An 11px lit disc that shows state at a glance: good, caution, danger or off.

**Good** (`accent`) and **caution** (`caution`) breathe slowly; **danger** (`danger`) holds still so it reads as urgent, not ambient; **off** is an empty ring for something reserved or not running. Breathing stops under `prefers-reduced-motion`.

**Consumer provides** `status` and an accessible `label` naming the state in the app's own words (it defaults to the status name).

**Always** pair a light with a word nearby. Green and red differ by hue more than lightness, so the light alone is not enough for colour-blind readers.
