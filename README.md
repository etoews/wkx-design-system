# wkx-namespace

The design system for the operational user interfaces of
[wkx-platform](../wkx-platform/), a personal Docker Compose platform running in
two homes: AWS (public-facing) and an on-prem home server (LAN-only).

The whole system is one self-contained page, [index.html](index.html): static
HTML and JS, no build step, no external requests.

## The design in five sentences

The namespace is the interface: every panel is addressed by its path
(`/wkx/<service>/<env>`), and the two Hosts appear as env groups (`env=prod`,
`env=home`). Status speaks the canonical vocabulary from the platform glossary,
up / stabilising / down with plan symbols `+ ~ −`, plus unlit for reserved
namespaces; source-system states (CloudWatch ALARM) are always shown verbatim
beside the operator's reading, never softened. Any token of the ubiquitous
language lights up wherever else it appears: hover or focus to find, click to
pin, Esc to release. Light and dark schemes follow the system setting, with an
auto / light / dark override in the nav persisted in localStorage. The layout
is fluid: the console takes the whole screen, panels share rows as the screen
grows, and prose stays capped inside panels.

## Viewing

Open [index.html](index.html) directly in a browser, or serve the folder:

```sh
python3 -m http.server
```

Typefaces are macOS system stacks (Avenir Next, Menlo, SF Mono) with standard
fallbacks elsewhere. The page respects `prefers-reduced-motion`, keeps visible
keyboard focus, and holds up down to mobile widths.

## Provenance

Chosen from four explored directions (Red Ledger, Harbour Watch, Namespace v0,
and this one); the rejected options live in git history on this branch. The
status vocabulary is canonical in wkx-platform's `CONTEXT.md` under
"Operational status". Registered in Claude Design as `wkx-namespace`.
