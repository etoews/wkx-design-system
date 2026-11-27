# wkx-design-system

The WKX design system: visual language for every WKX app. No domain
vocabulary; each app brings its own words. README.md covers the layout. This
file covers the rules.

## Source of truth

- `system/` is the source of truth. The Claude artifact
  (https://claude.ai/artifact/MMMcptPJx2svx85wF4FKXH) is a read-only copy
  published from `main`. Never edit the artifact directly. Never pull changes
  from it into the repo; if it differs from `system/`, the repo wins.
- `system/tokens.json` holds every value. A colour, size or font stack appears
  nowhere else by hand: not in `bundle.css`, not in previews, not in
  `index.html`. Those use `var(--token)`.
- Generated files are never edited by hand. They are `system/tokens.css` and
  `index.html`. Change `system/`, then run `python3 scripts/wkx.py build`, and
  commit the generated files with the change that caused them.
- `system/design-system.json` keeps `"editing": "code"`. Removing it would make
  the artifact editable, and then edits made there would be lost at the next
  publish.

## The system's format

`system/` mirrors the artifact's `project/` folder, one file to one path. Its
format belongs to Claude's Design System artifact type. Read the type's
references on the artifact before changing structure. They are
`artifact-type/reference/format.md` and `craft.md`, read with the Artifact
tool's read action and a `path`. The rules that bite most often:

- `tokens.json` families are lists of `{name, value, usage}`, never
  name-to-value maps. Colour values are hex or plain colour functions, never
  `var()`, named colours or `color-mix()`. Put the Night theme (`dark`) first.
- Every token has a usage note naming where it is used. Text colours clear
  4.5:1 on the grounds their note names, in both themes.
- Each component has `components/<Name>/README.md` (the first sentence is the
  summary; then what the consumer provides, plus do's and don'ts) and
  `components/<Name>/preview.html` (line 1 is the
  `<!-- @dsCard group="…" height=N -->` marker). Adding a component also means
  adding it to the `@ds-bundle` header on line 1 of `bundle.js` and to
  `index.d.ts`.
- `bundle.js` is one classic script assigning `window.WKX`. It reads
  `window.React`; it has no imports, no network calls and no literal
  `</script`.

## Workflow

1. Branch (`feat/<slug>`), change `system/`, then
   `python3 scripts/wkx.py build`.
2. Run `python3 scripts/wkx.py check` and
   `python3 -m unittest discover -s tests`. Both must pass; CI runs the same.
3. Look at `index.html` in Chrome, in Night and Day, for any visual change.
   Serve it with `python3 -m http.server`.
4. When the user says "ff", fast-forward `main`, push, then publish. The
   publish is part of "ff", not a separate step to ask about.

## Publishing

Publish whenever `main` has `system/` commits newer than the
`artifact-published` tag. The project hook says so after a push from `main`
and at session start. Act on it without asking.

1. On `main`, run `python3 scripts/wkx.py publish-plan`. It stages the changed
   files from `HEAD` under `.publish/` (gitignored). It prints JSON with the
   Artifact call and any `uploads_first`. `"publish": false` means there is
   nothing to do.
2. If `uploads_first` lists files (images under `system/assets/`), upload each
   one to the artifact (Artifact publish with `url`, `file_path`,
   `asset: true`). Put the returned blob id, size and type in that file's
   record under `assetGroups` in `system/design-system.json`. Commit to `main`,
   push, and start again at step 1.
3. Read `project/design-system.json` from the artifact (Artifact read with a
   `path`). If anything other than `lastChange` differs from
   `system/design-system.json`, someone changed the artifact. Stop and tell the
   user. Do not overwrite it.
4. Make the Artifact call exactly as printed: `url`, `root`, `file_path` (the
   index, which goes last, in the same call) and `files` (`null` removes a
   file).
5. When the call succeeds, run `python3 scripts/wkx.py mark-published`. If it
   fails, do not move the tag. Report the error.
6. Tell the user what was published, including the version the Artifact tool
   returned.

Never publish from a branch. The artifact mirrors `main`.

## Conventions

- New Zealand English everywhere, including in `system/`.
- Python is stdlib only (3.10+). There is no build tooling, and none should be
  added without a reason.
- Keep README.md current when behaviour or layout changes.
