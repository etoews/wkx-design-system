#!/usr/bin/env python3
"""Build and check the WKX design system kept in system/.

    python3 scripts/wkx.py build           # write system/tokens.css and index.html from system/
    python3 scripts/wkx.py check           # fail if either generated file is stale
    python3 scripts/wkx.py publish-plan    # stage unpublished system/ changes; print the Artifact calls
    python3 scripts/wkx.py verify-live     # fail if the artifact's copies differ from the last publish
    python3 scripts/wkx.py mark-published  # after the publish succeeds: tag HEAD as published
    python3 scripts/wkx.py hook            # Claude Code hook: remind Claude to publish

system/tokens.json is the one source for every token. tokens.css is generated
from it, laid out as the Claude Design System type compiles it, so the
published artifact and this repo agree. index.html is a local copy of the
artifact: the brand book, every token, and a live preview of every component,
generated from the same files.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = ROOT / "system"
TOKENS_JSON = SYSTEM / "tokens.json"
TOKENS_CSS = SYSTEM / "tokens.css"
INDEX_HTML = ROOT / "index.html"
ARTIFACT_URL = "https://claude.ai/artifact/MMMcptPJx2svx85wF4FKXH"

# React 18 UMD builds, pinned: the bundle reads window.React and window.ReactDOM,
# as the artifact's previews do.
REACT_URLS = (
    "https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js",
    "https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js",
)

TYPE_PROPS = (
    ("fontSize", "font-size"),
    ("lineHeight", "line-height"),
    ("fontWeight", "font-weight"),
    ("letterSpacing", "letter-spacing"),
)
PLAIN_FAMILIES_SKIP = ("name", "version", "meta", "color", "type", "shadow")


# --- tokens.css -------------------------------------------------------------


def load_tokens(path: Path = TOKENS_JSON) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _value(token: dict, theme: str, first: str) -> str:
    value = token["value"]
    if isinstance(value, str):
        return value if theme == first else ""
    return value.get(theme, value.get(first, ""))


def _css_value(value) -> str:
    text = str(value)
    if re.fullmatch(r"#[0-9A-Fa-f]{3,8}", text):
        return text.lower()
    alias = re.fullmatch(r"\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}", text)
    return f"var(--{alias.group(1)})" if alias else text


def _themed_tokens(tokens: dict) -> list[dict]:
    """Colour then shadow tokens: the families that vary by theme."""
    return tokens["color"]["tokens"] + tokens.get("shadow", {}).get("tokens", [])


def _plain_families(tokens: dict) -> list[tuple[str, dict]]:
    """Spacing, radius and every other {"tokens": [...]} family that does not vary by theme."""
    return [
        (key, family)
        for key, family in tokens.items()
        if key not in PLAIN_FAMILIES_SKIP and isinstance(family, dict) and "tokens" in family
    ]


def build_css(tokens: dict) -> str:
    """Compile tokens.json into tokens.css, as the Design System type lays it out."""
    themes = [t["id"] for t in tokens["color"]["themes"]]
    first = themes[0]
    themed = _themed_tokens(tokens)
    out = [f"/* {tokens['name']} — generated from tokens.json */", ""]

    out.append(f':root, [data-theme="{first}"] {{')
    out += [f"  --{t['name']}: {_css_value(_value(t, first, first))};" for t in themed]
    out += ["}", ""]

    for theme in themes[1:]:
        out.append(f'[data-theme="{theme}"] {{')
        for t in themed:
            if isinstance(t["value"], dict) and theme in t["value"]:
                out.append(f"  --{t['name']}: {_css_value(t['value'][theme])};")
        out += ["}", ""]

    out.append(":root {")
    for _, family in _plain_families(tokens):
        out += [f"  --{t['name']}: {_css_value(t['value'])};" for t in family["tokens"]]
    for key, stack in tokens["type"]["families"].items():
        out.append(f"  --font-{key}: {stack};")
    out += ["}", ""]

    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            out.append(f".{style['name']} {{")
            out.append(f"  font-family: var(--font-{style.get('family', group['family'])});")
            for key, prop in TYPE_PROPS:
                if key in style:
                    out.append(f"  {prop}: {style[key]};")
            out += ["}", ""]

    for font in tokens["type"].get("fonts", []):
        out.append("@font-face {")
        out.append(f"  font-family: \"{font['family']}\";")
        out.append(f"  src: url(\"{font['file']}\");")
        out.append(f"  font-weight: {font.get('weight', '400')};")
        out.append(f"  font-style: {font.get('style', 'normal')};")
        out += ["}", ""]

    return "\n".join(out).rstrip() + "\n"


# --- Markdown (the subset the brand book and component guidelines use) -------


def _inline(text: str) -> str:
    """Escape, then render `code`, **bold** and [links](url)."""
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = html.escape(re.sub(r"`([^`]+)`", stash, text), quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
        text,
    )
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def _table(rows: list[str]) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]
    out = ['<div class="ds-scroll"><table class="ds-table"><thead><tr>']
    out += [f"<th>{_inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown(text: str, shift: int = 0, drop_h1: bool = False) -> str:
    """Render Markdown to HTML. Headings move down by `shift` levels."""
    lines = text.splitlines()
    out: list[str] = []
    para: list[str] = []
    i = 0

    def flush() -> None:
        if para:
            out.append(f"<p>{_inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        heading = re.match(r"(#{1,6})\s+(.*)", stripped)
        if not stripped:
            flush()
            i += 1
        elif heading:
            flush()
            level = len(heading.group(1))
            if not (drop_h1 and level == 1):
                level = min(level + shift, 6)
                out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            i += 1
        elif stripped.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(_table(rows))
        elif re.match(r"(-|\d+\.)\s", stripped):
            flush()
            tag = "ul" if stripped.startswith("-") else "ol"
            items: list[str] = []
            while i < len(lines) and lines[i].strip():
                item = re.match(r"\s*(?:-|\d+\.)\s+(.*)", lines[i])
                if item:
                    items.append(item.group(1))
                elif items:
                    items[-1] += " " + lines[i].strip()
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            para.append(stripped)
            i += 1
    flush()
    return "\n".join(out)


# --- index.html: the local copy of the artifact ------------------------------

PREVIEW_HEAD = (
    '<link rel="stylesheet" href="system/tokens.css">'
    '<link rel="stylesheet" href="system/components/bundle.css">'
    + "".join(f'<script src="{u}" crossorigin="anonymous"></script>' for u in REACT_URLS)
    + '<script src="system/components/bundle.js"></script>'
    # The page sends the theme in; the preview sends its height out.
    "<script>addEventListener('message',function(e){if(e.source===parent&&e.data&&e.data.wkxTheme)"
    "{document.documentElement.setAttribute('data-theme',e.data.wkxTheme);}});"
    "addEventListener('load',function(){var r=function(){parent.postMessage({wkxHeight:"
    "document.documentElement.scrollHeight},'*');};r();if(window.ResizeObserver)"
    "{new ResizeObserver(r).observe(document.body);}});</script>"
)


def _card_marker(preview: str) -> dict[str, str]:
    """The attributes on a preview's first-line @dsCard marker: group, height, ..."""
    marker = re.match(r"\s*<!--\s*@dsCard(.*?)-->", preview)
    if not marker:
        return {}
    return {k: quoted or bare for k, quoted, bare in re.findall(r'(\w+)=(?:"([^"]*)"|(\S+))', marker.group(1))}


def preview_srcdoc(preview: str, theme: str) -> str:
    """A preview.html as the artifact frames it: tokens, bundle and React loaded first."""
    body = re.sub(r"^\s*<!--\s*@dsCard.*?-->\s*", "", preview, count=1)
    body = re.sub(r"<html([^>]*)>", rf'<html\1 data-theme="{theme}">', body, count=1)
    return re.sub(r"<head([^>]*)>", lambda m: f"<head{m.group(1)}>{PREVIEW_HEAD}", body, count=1)


def _component_order() -> list[str]:
    bundle = (SYSTEM / "components" / "bundle.js").read_text(encoding="utf-8")
    header = re.match(r"/\* @ds-bundle: (\{.*?\}) \*/", bundle)
    named = [c["name"] for c in json.loads(header.group(1))["components"]] if header else []
    folders = sorted(p.name for p in (SYSTEM / "components").iterdir() if p.is_dir())
    return [n for n in named if n in folders] + [n for n in folders if n not in named and n != "Cover"]


def _frame(name: str, preview: str, theme: str) -> str:
    height = _card_marker(preview).get("height", "120")
    return (
        f'<iframe class="ds-frame" title="{html.escape(name)} preview" loading="lazy" '
        f'style="height:{int(height)}px" srcdoc="{html.escape(preview_srcdoc(preview, theme))}"></iframe>'
    )


def _swatch(value: str) -> str:
    return f'<span class="ds-chip" style="background:{html.escape(value)}"></span><code>{html.escape(value)}</code>'


def _colour_section(tokens: dict) -> str:
    themes = tokens["color"]["themes"]
    first = themes[0]["id"]
    head = "".join(f"<th>{html.escape(t['name'])}</th>" for t in themes)
    rows = []
    for t in tokens["color"]["tokens"]:
        cells = "".join(f"<td>{_swatch(_value(t, th['id'], first))}</td>" for th in themes)
        rows.append(
            f"<tr><td><code>{t['name']}</code></td>{cells}<td>{_inline(t.get('usage', ''))}</td></tr>"
        )
    return (
        '<div class="ds-scroll"><table class="ds-table ds-tokens"><thead><tr><th>Token</th>'
        f"{head}<th>Use</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def _type_section(tokens: dict) -> str:
    out = []
    families = tokens["type"]["families"]
    out.append('<div class="ds-scroll"><table class="ds-table"><thead><tr><th>Family</th><th>Stack</th></tr></thead><tbody>')
    out += [f"<tr><td><code>--font-{k}</code></td><td><code>{html.escape(v)}</code></td></tr>" for k, v in families.items()]
    out.append("</tbody></table></div>")
    for group in tokens["type"]["groups"]:
        out.append(f"<h3>{html.escape(group['name'])}</h3>")
        for style in group["styles"]:
            spec = " · ".join(str(style[k]) for k, _ in TYPE_PROPS if k in style)
            out.append(
                '<div class="ds-type">'
                f'<div class="ds-type-key"><code>.{style["name"]}</code><span>{html.escape(spec)}</span></div>'
                f'<div class="{style["name"]}">{html.escape(style.get("sample", style["name"]))}</div>'
                f'<p class="ds-usage">{_inline(style.get("usage", ""))}</p></div>'
            )
    return "\n".join(out)


def _scale_section(tokens: dict) -> str:
    out = []
    families = _plain_families(tokens)
    if "shadow" in tokens:
        families.append(("shadow", tokens["shadow"]))
    for key, family in families:
        out.append(f"<h3>{html.escape(key.capitalize())}</h3>")
        if family.get("note"):
            out.append(f'<p class="ds-usage">{_inline(family["note"])}</p>')
        rows = []
        for t in family["tokens"]:
            name = t["name"]
            if key == "spacing":
                sample = f'<span class="ds-bar" style="width:var(--{name})"></span>'
            elif key == "radius":
                sample = f'<span class="ds-radius" style="border-radius:var(--{name})"></span>'
            elif key == "shadow":
                sample = f'<span class="ds-glow" style="box-shadow:var(--{name})"></span>'
            else:
                sample = ""
            value = t["value"] if isinstance(t["value"], str) else " / ".join(t["value"].values())
            rows.append(
                f"<tr><td><code>{name}</code></td><td><code>{html.escape(value)}</code></td>"
                f"<td>{sample}</td><td>{_inline(t.get('usage', ''))}</td></tr>"
            )
        out.append(
            '<div class="ds-scroll"><table class="ds-table ds-tokens"><thead><tr><th>Token</th><th>Value</th>'
            f"<th></th><th>Use</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
        )
    return "\n".join(out)


def _components_section(theme: str) -> str:
    cards = []
    for name in _component_order():
        folder = SYSTEM / "components" / name
        readme = folder / "README.md"
        preview = folder / "preview.html"
        group = _card_marker(preview.read_text(encoding="utf-8")).get("group", "") if preview.exists() else ""
        frame = _frame(name, preview.read_text(encoding="utf-8"), theme) if preview.exists() else ""
        guide = markdown(readme.read_text(encoding="utf-8"), shift=2, drop_h1=True) if readme.exists() else ""
        cards.append(
            f'<article class="ds-card" id="c-{name}"><header class="ds-card-head"><h3>{name}</h3>'
            f'<span class="ds-group">{html.escape(group)}</span></header>{frame}'
            f'<div class="ds-guide">{guide}</div></article>'
        )
    return '<div class="ds-cards">' + "\n".join(cards) + "</div>"


def _assets_section() -> str:
    out = []
    for group in sorted(p for p in (SYSTEM / "assets").iterdir() if p.is_dir()):
        out.append(f"<h3>{html.escape(group.name)}</h3><div class=\"ds-assets\">")
        for f in sorted(group.iterdir()):
            if f.suffix.lower() in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"):
                rel = f.relative_to(ROOT).as_posix()
                out.append(
                    f'<figure class="ds-asset"><img src="{rel}" alt="{html.escape(f.stem)}" width="96" height="96">'
                    f"<figcaption><code>{html.escape(f.name)}</code></figcaption></figure>"
                )
        out.append("</div>")
        readme = group / "README.md"
        if readme.exists():
            out.append(markdown(readme.read_text(encoding="utf-8"), shift=2, drop_h1=True))
    return "\n".join(out)


PAGE_CSS = """
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--ground); color: var(--ink); font-family: var(--font-sans); font-size: 15px; line-height: 1.5; }
a { color: var(--accent); }
:focus-visible { outline: var(--border-focus) solid var(--caution); outline-offset: 2px; }
code { font-family: var(--font-mono); font-size: .86em; }
.ds-chrome { display: flex; justify-content: space-between; align-items: center; gap: var(--space-3); flex-wrap: wrap;
  padding: var(--space-2) var(--ds-gutter); border-bottom: var(--border-hairline) solid var(--line);
  font-family: var(--font-mono); font-size: .74rem; color: var(--ink-muted); }
.ds-toggle { display: inline-flex; gap: var(--space-1); }
.ds-toggle button { font-family: var(--font-condensed); font-size: .68rem; font-weight: 600; letter-spacing: .14em;
  text-transform: uppercase; color: var(--ink); background: var(--surface-raised); border: var(--border-hairline) solid var(--line);
  border-radius: var(--radius-md); padding: .3rem .6rem; cursor: pointer; }
.ds-toggle button:hover { border-color: var(--ink-muted); }
.ds-toggle button[aria-pressed="true"] { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
:root { --ds-gutter: clamp(1rem, 2.5vw, 4rem); }
main { padding: 0 var(--ds-gutter) 5rem; }
.ds-head { padding: var(--space-7) 0 var(--space-5); }
.ds-head h1 { margin: 0; font-family: var(--font-condensed); font-size: clamp(1.9rem, 5vw, 2.9rem); line-height: 1.2;
  font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-strong); }
.ds-head h1 span { font-weight: 500; color: var(--ink-muted); }
.ds-head p { max-width: 44rem; color: var(--ink-muted); margin: var(--space-2) 0 0; }
.ds-head p strong { color: var(--ink); font-weight: 600; }
.ds-nav { display: flex; flex-wrap: wrap; gap: var(--space-2) var(--space-4); margin-top: var(--space-4);
  font-family: var(--font-condensed); font-size: .72rem; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; }
.ds-nav a { color: var(--ink-muted); text-decoration: none; }
.ds-nav a:hover { color: var(--ink); }
section { margin-top: var(--space-7); }
section > h2 { display: flex; align-items: center; gap: var(--space-3); margin: 0 0 var(--space-5);
  font-family: var(--font-condensed); font-size: .72rem; font-weight: 600; letter-spacing: .24em; text-transform: uppercase; color: var(--ink-muted); }
section > h2::after { content: ""; flex: 1; border-top: var(--border-hairline) solid var(--line); }
h3 { font-family: var(--font-condensed); font-size: .84rem; font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
  color: var(--ink); margin: var(--space-6) 0 var(--space-3); }
h4, h5 { font-size: .9rem; margin: var(--space-4) 0 var(--space-2); color: var(--ink); }
.ds-book { max-width: 52rem; }
.ds-book p, .ds-book li { max-width: var(--prose-max); }
.ds-scroll { overflow-x: auto; }
.ds-table { border-collapse: collapse; width: 100%; font-size: .88rem; }
.ds-table th { text-align: left; font-family: var(--font-condensed); font-size: .68rem; font-weight: 600; letter-spacing: .18em;
  text-transform: uppercase; color: var(--ink-muted); padding: var(--space-2) var(--space-3) var(--space-2) 0;
  border-bottom: var(--border-hairline) solid var(--line); }
.ds-table td { padding: var(--space-2) var(--space-3) var(--space-2) 0; border-bottom: var(--border-hairline) solid var(--line); vertical-align: top; }
.ds-tokens td:last-child { color: var(--ink-muted); min-width: 16rem; }
.ds-chip { display: inline-block; width: 1.4rem; height: 1.4rem; border-radius: var(--radius-md); border: var(--border-hairline) solid var(--line);
  vertical-align: middle; margin-right: var(--space-2); }
.ds-bar { display: inline-block; height: .6rem; background: var(--accent); border-radius: var(--radius-sm); }
.ds-radius { display: inline-block; width: 2rem; height: 2rem; border: 2px solid var(--ink-muted); }
.ds-glow { display: inline-block; width: var(--light-size); height: var(--light-size); border-radius: var(--radius-full); background: var(--surface-raised); }
.ds-type { padding: var(--space-3) 0; border-bottom: var(--border-hairline) solid var(--line); }
.ds-type-key { display: flex; gap: var(--space-3); flex-wrap: wrap; font-family: var(--font-mono); font-size: .72rem; color: var(--ink-muted); margin-bottom: var(--space-1); }
.ds-type-key code { color: var(--ink); }
.ds-usage { color: var(--ink-muted); font-size: .84rem; margin: var(--space-1) 0 0; max-width: var(--prose-max); }
.ds-cover { width: 100%; height: 288px; border: var(--border-hairline) solid var(--line); border-radius: var(--radius-lg); display: block; }
.ds-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 32rem), 1fr)); gap: var(--space-6); }
.ds-card { background: var(--surface); border: var(--border-hairline) solid var(--line); border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5) var(--space-5); min-width: 0; }
.ds-card-head { display: flex; justify-content: space-between; align-items: baseline; gap: var(--space-3); }
.ds-card-head h3 { margin: 0 0 var(--space-3); }
.ds-group { font-family: var(--font-mono); font-size: .72rem; color: var(--ink-muted); }
.ds-frame { display: block; width: 100%; border: var(--border-hairline) solid var(--line); border-radius: var(--radius-md); background: var(--ground); }
.ds-guide { font-size: .88rem; }
.ds-guide p { margin: var(--space-3) 0 0; }
.ds-assets { display: flex; gap: var(--space-5); flex-wrap: wrap; }
.ds-asset { margin: 0; }
.ds-asset figcaption { font-size: .72rem; color: var(--ink-muted); margin-top: var(--space-1); }
footer { margin-top: var(--space-7); font-family: var(--font-mono); font-size: .72rem; color: var(--ink-muted); }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
"""

PAGE_JS = """
(function () {
  var KEY = 'wkx-design-system-theme';
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;
  var choice = 'auto';
  try { choice = localStorage.getItem(KEY) || 'auto'; } catch (e) {}
  function resolved() { return choice === 'auto' ? (media && media.matches ? 'light' : 'dark') : choice; }
  function frames() { return Array.prototype.slice.call(document.querySelectorAll('iframe')); }
  function apply() {
    var theme = resolved();
    document.documentElement.setAttribute('data-theme', theme);
    frames().forEach(function (f) { if (f.contentWindow) f.contentWindow.postMessage({ wkxTheme: theme }, '*'); });
    document.querySelectorAll('.ds-toggle button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.theme === choice));
    });
  }
  document.querySelectorAll('.ds-toggle button').forEach(function (b) {
    b.addEventListener('click', function () {
      choice = b.dataset.theme;
      try { localStorage.setItem(KEY, choice); } catch (e) {}
      apply();
    });
  });
  if (media && media.addEventListener) media.addEventListener('change', apply);
  frames().forEach(function (f) { f.addEventListener('load', function () { f.contentWindow.postMessage({ wkxTheme: resolved() }, '*'); }); });
  window.addEventListener('message', function (e) {
    if (!e.data || typeof e.data.wkxHeight !== 'number') return;
    frames().forEach(function (f) {
      if (f.contentWindow === e.source && !f.classList.contains('ds-cover')) {
        f.style.height = Math.min(Math.max(e.data.wkxHeight, 40), 4000) + 'px';
      }
    });
  });
  apply();
})();
"""


def build_index(tokens: dict) -> str:
    """The local copy of the WKX artifact, generated from system/."""
    first = tokens["color"]["themes"][0]["id"]
    readme = markdown((SYSTEM / "README.md").read_text(encoding="utf-8"), shift=1)
    cover = SYSTEM / "components" / "Cover" / "preview.html"
    cover_frame = (
        f'<iframe class="ds-cover" title="Cover" srcdoc="{html.escape(preview_srcdoc(cover.read_text(encoding="utf-8"), first))}"></iframe>'
        if cover.exists()
        else ""
    )
    sections = [
        ("overview", "Overview", f'{cover_frame}<div class="ds-book">{readme}</div>'),
        ("colour", "Colour", _colour_section(tokens)),
        ("type", "Type", _type_section(tokens)),
        ("scales", "Spacing, radii, borders, sizes, glows", _scale_section(tokens)),
        ("components", "Components", _components_section(first)),
        ("assets", "Assets", _assets_section()),
    ]
    nav = "".join(f'<a href="#{sid}">{html.escape(title)}</a>' for sid, title, _ in sections)
    body = "\n".join(
        f'<section id="{sid}" aria-labelledby="{sid}-h"><h2 id="{sid}-h">{html.escape(title)}</h2>\n{content}\n</section>'
        for sid, title, content in sections
    )
    name = html.escape(tokens["name"])
    return f"""<!doctype html>
<!-- Generated from system/ by scripts/wkx.py build. Do not edit: change system/ and rebuild. -->
<html lang="en-NZ" data-theme="{first}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} design system</title>
<meta name="description" content="The {name} design system: brand book, tokens and live component previews.">
<link rel="icon" href="system/assets/Logos/wkx-mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="system/tokens.css">
<style>{PAGE_CSS}</style>
</head>
<body>
<div class="ds-chrome"><span>{name.lower()} · design system</span>
<span class="ds-toggle" role="group" aria-label="Theme"><button type="button" data-theme="auto">Auto</button><button type="button" data-theme="dark">Night</button><button type="button" data-theme="light">Day</button></span></div>
<main>
<header class="ds-head">
<h1>{name} <span>design system</span></h1>
<p>A local copy of the <a href="{ARTIFACT_URL}">{name} Design System artifact</a> in Claude, generated from <strong>system/</strong>, the source of truth.</p>
<nav class="ds-nav" aria-label="Sections">{nav}</nav>
</header>
{body}
<footer>Generated from system/ by scripts/wkx.py build.</footer>
</main>
<script>{PAGE_JS}</script>
</body>
</html>
"""


# --- CLI ----------------------------------------------------------------------


def generated() -> dict[Path, str]:
    tokens = load_tokens()
    return {TOKENS_CSS: build_css(tokens), INDEX_HTML: build_index(tokens)}


def build() -> int:
    for path, text in generated().items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(text.splitlines())} lines)")
    return 0


def check() -> int:
    stale = [
        path for path, text in generated().items()
        if not path.exists() or path.read_text(encoding="utf-8") != text
    ]
    for path in stale:
        print(f"FAIL {path.relative_to(ROOT)} is stale: run python3 scripts/wkx.py build", file=sys.stderr)
    if not stale:
        print("ok: tokens.css and index.html are current with system/")
    return 1 if stale else 0


# --- Publishing to the artifact ------------------------------------------------
#
# Publishing runs inside Claude Code, through its Artifact tool: nothing outside
# Claude can write to the artifact. These commands do everything around that one
# call. The local tag PUBLISHED_TAG marks the commit the artifact was last
# published from; with no tag, everything in system/ is published.

PUBLISHED_TAG = "artifact-published"
STAGE = ROOT / ".publish"
# The artifact's current copies of the files a publish touches, read back
# before publishing. The Artifact tool refuses to overwrite a file this session
# has not read, and comparing them shows whether anyone edited the artifact.
LIVE = ROOT / ".publish-live"
INDEX = "project/design-system.json"
# Uploaded to the artifact's asset store, not published as files.
ASSET_SUFFIXES = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".webm", ".pdf"}
# Extensions the artifact serves by type. Any other text file (index.d.ts) must
# name its type, or the Artifact tool refuses the whole publish.
SERVED_SUFFIXES = {
    ".html", ".css", ".js", ".mjs", ".json", ".map", ".txt", ".md", ".csv", ".xml",
    ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".woff", ".woff2", ".ttf", ".otf",
}


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _published_ref() -> str | None:
    try:
        return _git("rev-parse", "--verify", "--quiet", f"refs/tags/{PUBLISHED_TAG}^{{commit}}")
    except subprocess.CalledProcessError:
        return None


def pending_changes() -> dict[str, str]:
    """system/ paths changed on HEAD since the last publish: path -> 'changed' or 'deleted'."""
    base = _published_ref()
    if base is None:
        return {p: "changed" for p in _git("ls-files", "system").splitlines() if p}
    out = {}
    for line in _git("diff", "--name-status", "--no-renames", base, "HEAD", "--", "system").splitlines():
        status, path = line.split("\t", 1)
        out[path] = "deleted" if status.startswith("D") else "changed"
    return out


def _served(path: str) -> str:
    return "project/" + path.removeprefix("system/")


def _is_upload(path: str) -> bool:
    rel = path.removeprefix("system/")
    return rel.startswith("assets/") and Path(rel).suffix.lower() in ASSET_SUFFIXES


def read_first(pending: dict[str, str]) -> list[str]:
    """Artifact paths the publish replaces or removes: each must be read before it."""
    return sorted({_served(p) for p in pending if not _is_upload(p)} | {INDEX})


def _published_bytes(base: str | None, path: str) -> bytes | None:
    if base is None:
        return None
    out = subprocess.run(["git", "show", f"{base}:{path}"], cwd=ROOT, capture_output=True)
    return out.stdout if out.returncode == 0 else None


def _without_last_change(raw: bytes) -> dict:
    index = json.loads(raw)
    index.pop("lastChange", None)
    return index


def verify_live() -> int:
    """Compare the artifact's copies under LIVE with what was last published from here.

    A difference means someone changed the artifact outside this repo; publishing
    would overwrite their work. The index is compared without lastChange.
    """
    base = _published_ref()
    problems = []
    for served in read_first(pending_changes()):
        path = "system/" + served.removeprefix("project/")
        expected = _published_bytes(base, path)
        live = LIVE / served
        if expected is None:
            if live.exists():
                problems.append(f"{served}: on the artifact but never published from here")
            continue
        if not live.exists():
            problems.append(f"{served}: not read into {LIVE.name}/, or missing from the artifact")
        elif served == INDEX:
            if _without_last_change(live.read_bytes()) != _without_last_change(expected):
                problems.append(f"{served}: differs (beyond lastChange) from the last publish")
        elif live.read_bytes() != expected:
            problems.append(f"{served}: differs from the last publish")
    for line in problems:
        print(f"FAIL {line}", file=sys.stderr)
    if problems:
        print("The artifact was changed outside this repo. Do not publish; tell the user.", file=sys.stderr)
        return 1
    print("ok: the artifact matches the last publish")
    return 0


def publish_plan() -> int:
    """Stage what changed since the last publish and print the Artifact call to make."""
    if _git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        print("FAIL publish from main only: the artifact mirrors main", file=sys.stderr)
        return 1
    pending = pending_changes()
    if not pending:
        print(json.dumps({"publish": False, "reason": "system/ is unchanged since the last publish"}))
        return 0

    for folder in (STAGE, LIVE):
        if folder.exists():
            shutil.rmtree(folder)
    head = _git("rev-parse", "--short", "HEAD")
    files: dict[str, str | dict | None] = {}
    uploads = []
    for path, state in sorted(pending.items()):
        rel = path.removeprefix("system/")
        served = _served(path)
        if served == INDEX:
            continue  # always sent below, last
        if state == "deleted":
            files[served] = None
        elif _is_upload(path):
            uploads.append(str(ROOT / path))
        else:
            target = STAGE / served
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.run(
                ["git", "show", f"HEAD:{path}"], cwd=ROOT, check=True, capture_output=True
            ).stdout)
            if Path(rel).suffix.lower() in SERVED_SUFFIXES:
                files[served] = served
            else:
                files[served] = {"from": served, "contentType": "text/plain"}

    # The index, from HEAD, with lastChange naming this publish.
    index = json.loads(_git("show", "HEAD:system/design-system.json"))
    base = _published_ref()
    span = f"{base}..HEAD" if base else "HEAD"
    index["lastChange"] = {
        "by": _git("config", "user.name") or "Claude",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "via": f"Claude Code · etoews/wkx-design-system@{head}",
        "note": _git("log", "-1", "--format=%s", span, "--", "system")[:280],
    }
    index_path = STAGE / "project" / "design-system.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files.pop("project/design-system.json", None)

    print(json.dumps({
        "publish": True,
        "commit": head,
        "artifact": {
            "action": "publish",
            "url": ARTIFACT_URL,
            "root": str(STAGE),
            "file_path": str(index_path),
            "files": files,
        },
        "uploads_first": uploads,
        "read_first": {
            "action": "read",
            "url": ARTIFACT_URL,
            "paths": read_first(pending),
            "out_dir": str(LIVE),
        },
    }, indent=2, ensure_ascii=False))
    return 0


def mark_published() -> int:
    """Move the published tag to HEAD, once the Artifact call has succeeded."""
    _git("tag", "-f", PUBLISHED_TAG, "HEAD")
    for folder in (STAGE, LIVE):
        if folder.exists():
            shutil.rmtree(folder)
    print(f"{PUBLISHED_TAG} -> {_git('rev-parse', '--short', 'HEAD')}")
    return 0


def hook() -> int:
    """Claude Code hook: after a push from main, or at session start, ask for a publish.

    Never fails the tool call: any error means no reminder, not a broken session.
    """
    try:
        event = json.loads(sys.stdin.read() or "{}")
        name = event.get("hook_event_name", "")
        command = (event.get("tool_input") or {}).get("command", "")
        if name == "PostToolUse" and not re.search(r"\bgit\s+push\b", command):
            return 0
        if _git("rev-parse", "--abbrev-ref", "HEAD") != "main":
            return 0
        pending = pending_changes()
        if not pending:
            return 0
        message = (
            f"system/ on main has {len(pending)} file(s) not yet published to the WKX artifact. "
            "Publish now, without asking: follow 'Publishing' in CLAUDE.md "
            "(python3 scripts/wkx.py publish-plan, the read it prints, "
            "python3 scripts/wkx.py verify-live, the publish it prints, then "
            "python3 scripts/wkx.py mark-published)."
        )
        print(json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": message}}))
    except Exception:  # noqa: BLE001 - a hook must never break the session
        return 0
    return 0


def main(argv: list[str]) -> int:
    commands = {
        "build": build,
        "check": check,
        "publish-plan": publish_plan,
        "verify-live": verify_live,
        "mark-published": mark_published,
        "hook": hook,
    }
    if len(argv) != 2 or argv[1] not in commands:
        print(__doc__, file=sys.stderr)
        return 2
    return commands[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
