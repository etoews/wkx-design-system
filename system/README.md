WKX is the shared look and feel of every WKX app: a calm console. A deep-navy night ground, hairline structure, condensed uppercase signage and mono data, with colour spent only on signal. Day is an equal light scheme, not an afterthought. The system fixes how things look; each app brings its own words.

## Principles

- **Colour is signal.** Neutrals carry the page. `accent`, `caution` and `danger` appear only where something has a state or an action. `highlight` marks what the reader is looking for: cross-referenced terms and filter matches.
- **Hairlines, not shadows.** Structure is 1px `line` borders and dividers on flat `surface` panels. The only shadows are the glows on status lights and highlighted terms.
- **Three voices of type.** Condensed uppercase for signage (labels, buttons, column heads), sans for prose, mono for anything a machine would recognise: identifiers, paths, numbers, times, commands.
- **Fluid, not boxed.** The page takes the whole screen. Panels share rows as the screen widens, but prose stays capped inside them (`prose-max`).
- **Night and day.** Follow the system setting, with an auto / light / dark override (`ThemeToggle`). Design every screen in both.

## Colour

| Role | Token | Use it for |
| --- | --- | --- |
| Ground | `ground` | Page background; the inset well behind logs and inputs |
| Surface | `surface`, `surface-raised` | Panels; one step up for button fills and meter tracks |
| Structure | `line` | Every border and divider |
| Text | `ink`, `ink-muted`, `ink-strong` | Body; labels and metadata; the headline and big figures only |
| Accent and good | `accent`, `accent-hover`, `on-accent` | Primary buttons, links, healthy states, meter fills |
| Caution | `caution` | Attention without action; the focus ring |
| Danger | `danger`, `danger-tint` | Failure and destructive actions |
| Highlight | `highlight`, `on-highlight` | Cross-reference highlighting, filter matches and the hint chip |

- Put text in `ink` on `ground`, `surface` or `surface-raised`, and in `ink-muted` on any of them.
- Use `ink-strong` sparingly: one headline per page, plus the big figures.
- Spend `accent` once per view on a fill (the primary button). It can appear any number of times as a small status mark.
- Never encode state by colour alone. Every status carries a word in the app's vocabulary beside its light or tone. Green and red differ mainly by hue, so the word does the work for colour-blind readers.
- Show a source system's raw state verbatim beside your reading of it, e.g. "Source: ALARM. Status: settling". Don't soften it.
- **Contrast:** every text token clears 4.5:1 on `ground` and `surface` in both themes, and `ink-muted` also on `surface-raised`. Keep `accent`, `caution` and `danger` text off `surface-raised` unless it is 19px bold or larger.

## Type

- **Families:** `--font-condensed` (Avenir Next Condensed), `--font-sans` (Avenir Next), `--font-mono` (Menlo / SF Mono). These are macOS system faces with standard fallbacks; no web fonts are loaded.
- **Signage:** `headline`, `title`, `section-label`, `button-label`, `column-head` and `stat-key` are condensed, always UPPERCASE, and tracked from 0.1em to 0.24em. The smaller the label, the wider the tracking.
- **Prose:** `body` (15px / 1.5) and `note` in `ink`; `lede` and `caption` in `ink-muted`. Bold words in a muted line step up to `ink`, weight 600.
- **Data:** `figure`, `data`, `data-sm`, `meta` and `log` are mono. Use `font-variant-numeric: tabular-nums` wherever digits line up.
- **Writing:** NZ English, sentence case for prose and buttons (buttons are uppercased by style). Put a space between a number and its unit (`6 %`, `1.7 / 3.8 GiB`, `4 h 38 m`). Join metadata with ` · `. Use `→` for a change from one value to another. Write dates as `18 Jul 14:32` and give the time zone once, in the page head.

## Layout and spacing

- **Gutter:** fluid, `clamp(1.5rem, 2.5vw, 4rem)` each side, with 5rem at the foot of the page.
- **Panel:** `space-4` padding on top and `space-5` on the sides and bottom. Grid gap `space-6`; between major sections `space-7`.
- **Inside rows:** `space-1` from label to control, `space-2` for tight pairs, `space-3` between columns.
- **Grid:** two columns, stacking below `breakpoint-stack` (860px). From `breakpoint-wide` (1500px), half panels share a six-column row; from 2100px, small panels go three-up.
- **Radii:** `radius-lg` for panels and legends, `radius-md` for controls and wells, `radius-sm` for meters, `radius-xs` for highlighted terms and filter matches, `radius-pill` for pill controls (the table filter and columns menu), and `radius-full` only for status lights. A panel with a top rule (`border-rule`) keeps its top corners square.

## Page anatomy

1. **Page chrome:** a mono strip with the app name on the left and `ThemeToggle` on the right.
2. **Head:** the `headline` (`ink-strong`; an optional second word at weight 500 in `ink-muted`), a mono timestamp right-aligned, a `lede` under it, then a `Legend` if the page shows status.
3. **Groups:** ruled `Panel`s, one per top-level grouping (place, environment, account), each a list of `ListRow`s. A group with nothing in it says so plainly with an off light.
4. **Console:** a `.wkx-grid` of panels, each opening with a `SectionLabel`, holding `Gauge`s, `DataTable`s, `LogView`s and finally a panel of actions (`Button`, `Field`).

## States, motion and focus

- **Status lights:** good and caution lights breathe on a 3.2 s cycle; danger holds still; off is an empty ring. All motion stops under `prefers-reduced-motion`.
- **Hover:** control borders step from `line` to `ink-muted`. The primary button moves to `accent-hover`, and the danger button gains `danger-tint`.
- **Focus:** every focusable thing gets a 2px solid `caution` ring at a 2px offset, which clears 3:1 on every surface in both themes. Never remove it.
- **Empty states:** state what is missing and when it is expected, in a `note`, beside an off light.

## Iconography

State is shown with status lights and words, and structure with hairlines and signage. The only mark is `assets/Logos/wkx-mark.svg`, which is also the favicon.
