# ThemeToggle

A small mono button that cycles **auto**, **light** and **dark**.

Night (dark) is the identity; day (light) is its equal. Auto follows the system setting and tracks changes; light and dark override it and persist in `localStorage` when storage is allowed. It sets `data-theme` on `<html>`, which is what the tokens key on.

**Use** one per app, top right of the page chrome.

**Consumer provides** an optional `storageKey` (default `wkx-theme`) and `label={false}` to drop the "theme:" prefix.

**Apps** should also apply a saved override before first paint, so there is no flash.
