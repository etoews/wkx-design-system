# wkx-design-system

The look and feel of every WKX app, and Namespace, the operational console of
[wkx-platform](../wkx-platform/) that it grew out of.

## The design system

[system/](system/) is the WKX design system and its source of truth. It covers
visual language only: colour tokens for the Night and Day themes, type,
spacing, radii, glows, 13 components with live previews, and a brand book. It
carries no domain vocabulary. Each app supplies its own words.

| Path | What |
| --- | --- |
| [system/tokens.json](system/tokens.json) | Every token. The one source for every value |
| [system/tokens.css](system/tokens.css) | Generated from `tokens.json`. Never edit it by hand |
| [system/README.md](system/README.md) | The brand book: principles and usage rules that name tokens |
| [system/components/](system/components/) | `bundle.js`, `bundle.css`, `index.d.ts`, and a README and live preview per component |
| [system/assets/Logos/](system/assets/Logos/) | `wkx-mark.svg`, the mark and favicon |
| [system/design-system.json](system/design-system.json) | The index the Claude artifact reads |

### Changing it

Change the files in `system/`, then:

```sh
python3 scripts/wkx.py build       # regenerate system/tokens.css
python3 scripts/wkx.py check       # tokens.css is current; Namespace matches the tokens
python3 -m unittest discover -s tests
```

### WKX in Claude

The system is published to Claude as the **WKX** Design System artifact:
<https://claude.ai/artifact/MMMcptPJx2svx85wF4FKXH>. To design or build an app
in the WKX look, ask Claude to use the WKX design system.

The artifact is a read-only copy. Its index carries `"editing": "code"`, so its
page says it is synced from code and takes no edits. Publishing goes one way,
from this repo to Claude. After a change lands on `main`, ask Claude Code to
publish `system/` to the WKX artifact. Each file in `system/` is published at
`project/<same path>`, with these exceptions:

- `wkx-mark.svg` stays an uploaded asset. It is re-uploaded only when it
  changes, and then its record in `design-system.json` gets the new blob id.
- `design-system.json` goes last. It is re-read from the artifact first, so
  that no keys are lost.

## Namespace: the reference console

[index.html](index.html) is Namespace, the console for wkx-platform, a personal
Docker Compose platform running in two homes: AWS (public-facing) and an
on-prem home server (LAN-only). It is the WKX look applied with wkx-platform's
vocabulary. It is one self-contained page of static HTML and JS, with no build
step and no external requests.

Namespace at a glance:

- **Panels are addressed by path.** Every panel is addressed by its path
  (`/wkx/<service>/<env>`), and the two Hosts appear as env groups (`env=prod`,
  `env=home`).
- **Status uses the platform glossary.** States are up / stabilising / down,
  with plan symbols `+ ~ −`, plus unlit for reserved namespaces.
  Source-system states (CloudWatch ALARM) are always shown verbatim beside the
  operator's reading, never softened.
- **Terms light up everywhere.** Any token of the ubiquitous language lights up
  wherever else it appears: hover or focus to find, click to pin, Esc to
  release.
- **Light and dark schemes** follow the system setting, with an auto / light /
  dark override in the nav persisted in localStorage.
- **The layout is fluid.** The console takes the whole screen, panels share
  rows as the screen grows, and prose stays capped inside panels.

Namespace keeps its own CSS variable names, which use platform vocabulary
(`--add`, `--chg`, `--del`). Each one mirrors a WKX token, including the darker
Day values that keep all text at 4.5:1 contrast or better. `scripts/wkx.py
check` fails if any Namespace value drifts from the token it mirrors. The
mapping is `NAMESPACE_COLOURS` in [scripts/wkx.py](scripts/wkx.py).

### Viewing

Open [index.html](index.html) directly in a browser, or serve the folder:

```sh
python3 -m http.server
```

Typefaces are macOS system stacks (Avenir Next, Menlo, SF Mono) with standard
fallbacks elsewhere. The page respects `prefers-reduced-motion`, keeps visible
keyboard focus, and holds up down to mobile widths.

## Provenance

Namespace was chosen from four explored directions (Red Ledger, Harbour Watch,
Namespace v0, and this one); the rejected options live in git history. The
status vocabulary is canonical in wkx-platform's `CONTEXT.md` under
"Operational status".
