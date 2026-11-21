#!/usr/bin/env python3
"""Build and check the WKX design system kept in system/.

    python3 scripts/wkx.py build   # write system/tokens.css from system/tokens.json
    python3 scripts/wkx.py check   # fail if tokens.css is stale or Namespace drifts

tokens.json is the one source for every token. tokens.css is generated from it,
laid out as the Claude Design System type compiles it, so the published artifact
and this repo agree. Namespace (index.html) keeps its own variable names; check
compares each one against the token it mirrors.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = ROOT / "system"
TOKENS_JSON = SYSTEM / "tokens.json"
TOKENS_CSS = SYSTEM / "tokens.css"
NAMESPACE_HTML = ROOT / "index.html"

# Namespace variable -> the WKX token it mirrors. Namespace keeps its own names
# (platform vocabulary: add / del / chg); the values must stay equal.
NAMESPACE_COLOURS = {
    "deep": "ground",
    "water": "surface",
    "hull": "surface-raised",
    "line": "line",
    "text": "ink",
    "fog": "ink-muted",
    "masthead": "ink-strong",
    "add": "accent",
    "add-hover": "accent-hover",
    "on-accent": "on-accent",
    "chg": "caution",
    "del": "danger",
    "del-tint": "danger-tint",
    "match": "highlight",
    "on-match": "on-highlight",
    "glow-add": "glow-accent-color",
    "glow-chg": "glow-caution-color",
    "glow-del": "glow-danger-color",
    "match-glow": "glow-highlight-color",
}
NAMESPACE_FONTS = {"sans": "sans", "sans-cond": "condensed", "mono": "mono"}

TYPE_PROPS = (
    ("fontSize", "font-size"),
    ("lineHeight", "line-height"),
    ("fontWeight", "font-weight"),
    ("letterSpacing", "letter-spacing"),
)


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


def _themed_families(tokens: dict) -> list[dict]:
    """Colour then shadow tokens: the families that vary by theme."""
    return tokens["color"]["tokens"] + tokens.get("shadow", {}).get("tokens", [])


def build_css(tokens: dict) -> str:
    """Compile tokens.json into tokens.css, as the Design System type lays it out."""
    themes = [t["id"] for t in tokens["color"]["themes"]]
    first = themes[0]
    themed = _themed_families(tokens)
    out = [f"/* {tokens['name']} — generated from tokens.json */", ""]

    out.append(f':root, [data-theme="{first}"] {{')
    out += [f"  --{t['name']}: {_css_value(_value(t, first, first))};" for t in themed]
    out += ["}", ""]

    for theme in themes[1:]:
        out.append(f'[data-theme="{theme}"] {{')
        for t in themed:
            value = _value(t, theme, first)
            if isinstance(t["value"], dict) and theme in t["value"]:
                out.append(f"  --{t['name']}: {_css_value(value)};")
        out += ["}", ""]

    out.append(":root {")
    for key, family in tokens.items():
        if key in ("name", "version", "meta", "color", "type", "shadow"):
            continue
        if isinstance(family, dict) and "tokens" in family:
            out += [f"  --{t['name']}: {_css_value(t['value'])};" for t in family["tokens"]]
    for key, stack in tokens["type"]["families"].items():
        out.append(f"  --font-{key}: {stack};")
    out += ["}", ""]

    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            family = style.get("family", group["family"])
            out.append(f".{style['name']} {{")
            out.append(f"  font-family: var(--font-{family});")
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


def _normalise(value: str) -> str:
    text = re.sub(r"\s+", "", value.strip().lower())
    return re.sub(r"(?<![0-9])\.(\d)", r"0.\1", text)


def _declarations(block: str) -> dict[str, str]:
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r"--([a-z0-9-]+)\s*:\s*([^;]+);", block)
    }


def _namespace_blocks(html: str) -> dict[str, list[dict[str, str]]]:
    """Namespace's dark :root block and its two light blocks (media query and override)."""
    dark = re.search(r":root\s*\{([^}]*)\}", html)
    light = [
        m.group(1)
        for m in re.finditer(
            r"(?::root:not\(\[data-theme=\"dark\"\]\)|:root\[data-theme=\"light\"\])\s*\{([^}]*)\}",
            html,
        )
    ]
    return {
        "dark": [_declarations(dark.group(1))] if dark else [],
        "light": [_declarations(b) for b in light],
    }


def namespace_drift(html: str, tokens: dict) -> list[str]:
    """Each place Namespace's values differ from the tokens they mirror."""
    by_name = {t["name"]: t for t in tokens["color"]["tokens"]}
    first = tokens["color"]["themes"][0]["id"]
    blocks = _namespace_blocks(html)
    problems = []
    for theme, theme_blocks in blocks.items():
        if not theme_blocks:
            problems.append(f"index.html: no {theme} variable block found")
        for i, decls in enumerate(theme_blocks):
            for var, token in NAMESPACE_COLOURS.items():
                want = _value(by_name[token], theme, first)
                got = decls.get(var)
                if got is None:
                    problems.append(f"index.html {theme}[{i}]: --{var} missing (mirrors {token})")
                elif _normalise(got) != _normalise(want):
                    problems.append(
                        f"index.html {theme}[{i}]: --{var} is {got.strip()}, token {token} is {want}"
                    )
    dark = blocks["dark"][0] if blocks["dark"] else {}
    for var, family in NAMESPACE_FONTS.items():
        want = tokens["type"]["families"][family]
        got = dark.get(var)
        if got is None or _normalise(got) != _normalise(want):
            problems.append(f"index.html: --{var} does not match type family {family}")
    return problems


def build() -> int:
    css = build_css(load_tokens())
    TOKENS_CSS.write_text(css, encoding="utf-8")
    print(f"wrote {TOKENS_CSS.relative_to(ROOT)} ({len(css.splitlines())} lines)")
    return 0


def check() -> int:
    tokens = load_tokens()
    problems = []
    if not TOKENS_CSS.exists() or TOKENS_CSS.read_text(encoding="utf-8") != build_css(tokens):
        problems.append("system/tokens.css is stale: run python3 scripts/wkx.py build")
    problems += namespace_drift(NAMESPACE_HTML.read_text(encoding="utf-8"), tokens)
    for problem in problems:
        print(f"FAIL {problem}", file=sys.stderr)
    if not problems:
        print("ok: tokens.css is current and Namespace matches tokens.json")
    return 1 if problems else 0


def main(argv: list[str]) -> int:
    commands = {"build": build, "check": check}
    if len(argv) != 2 or argv[1] not in commands:
        print(__doc__, file=sys.stderr)
        return 2
    return commands[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
