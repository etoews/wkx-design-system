# wkx-design-system

The WKX design system: the look and feel of every WKX app.

It covers visual language only. That means colour tokens for the Night and Day
themes, type, spacing, radii, glows, 13 components with live previews, and a
brand book. It carries no domain vocabulary. Each app supplies its own words.

## Viewing it

[index.html](index.html) is a local copy of the WKX artifact in Claude: the
brand book, every token in both themes, and a live preview of each component.
It is also served at <https://etoews.github.io/wkx-design-system/>. Locally,
serve the folder:

```sh
python3 -m http.server
```

The component previews load React 18 from jsDelivr, as they do in the
artifact. The rest of the page is local.

## Where it lives

[system/](system/) is the source of truth. Everything else is generated from it
or published from it.

| Path | What |
| --- | --- |
| [system/tokens.json](system/tokens.json) | Every token. The one source for every value |
| [system/README.md](system/README.md) | The brand book: principles and usage rules that name tokens |
| [system/components/](system/components/) | `bundle.js`, `bundle.css`, `index.d.ts`, and a README and live preview per component |
| [system/assets/Logos/](system/assets/Logos/) | `wkx-mark.svg`, the mark and favicon |
| [system/design-system.json](system/design-system.json) | The index the Claude artifact reads |
| [system/tokens.css](system/tokens.css) | Generated from `tokens.json` |
| [index.html](index.html) | Generated from `system/` |

### Changing it

Change the files in `system/`, then:

```sh
python3 scripts/wkx.py build       # regenerate system/tokens.css and index.html
python3 scripts/wkx.py check       # both generated files are current
python3 -m unittest discover -s tests
```

CI runs `check` and the tests on every push and pull request.

### WKX in Claude

The system is published to Claude as the **WKX** Design System artifact:
<https://claude.ai/artifact/MMMcptPJx2svx85wF4FKXH>. To design or build an app
in the WKX look, ask Claude to use the WKX design system.

The artifact is a read-only copy. Its index carries `"editing": "code"`, so its
page says it is synced from code and takes no edits.

Publishing is automatic and goes one way, from `main` to Claude. Only Claude
Code can write to the artifact, so publishing runs there, not in CI. A project
hook ([.claude/settings.json](.claude/settings.json)) runs after every
`git push` from `main`, and again at session start. When `system/` has commits
that are not yet published, the hook tells Claude to publish them.
[CLAUDE.md](CLAUDE.md) has the procedure. The local git tag
`artifact-published` marks the commit the artifact was last published from.

## Apps built with WKX

- [wkx-ecosystem-localhost](../wkx-ecosystem-localhost/) is a local dashboard
  of the WKX ecosystem. It consumes the design system by adaptation. Its own
  stylesheet vendors the WKX palette, type stacks and panel idiom, and it
  diverges where its board needs to: a tinted panel and a `--sky` wayfinding
  colour. It vendors an earlier copy, so its variables do not track
  `system/tokens.json`.
