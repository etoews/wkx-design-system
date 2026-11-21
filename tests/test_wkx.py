import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import wkx  # noqa: E402

TOKENS = {
    "name": "Demo",
    "version": 1,
    "color": {
        "themes": [{"id": "dark", "name": "Night"}, {"id": "light", "name": "Day"}],
        "tokens": [
            {"name": "ground", "value": {"dark": "#0A141E", "light": "#eef3f6"}},
            {"name": "same", "value": "#ffffff"},
            {"name": "alias", "value": "{ground}"},
        ],
    },
    "type": {
        "fonts": [],
        "families": {"sans": "Avenir, sans-serif"},
        "groups": [
            {
                "name": "Text",
                "family": "sans",
                "styles": [{"name": "body", "fontSize": "15px", "lineHeight": 1.5}],
            }
        ],
    },
    "spacing": {"tokens": [{"name": "space-1", "value": "0.3rem"}]},
    "shadow": {"tokens": [{"name": "glow", "value": {"dark": "0 0 1px #000", "light": "none"}}]},
}


class BuildCssTest(unittest.TestCase):
    def setUp(self):
        self.css = wkx.build_css(TOKENS)

    def test_first_line_marks_it_generated(self):
        self.assertEqual(self.css.splitlines()[0], "/* Demo — generated from tokens.json */")

    def test_first_theme_is_root_and_hex_is_lowercased(self):
        self.assertIn(':root, [data-theme="dark"] {\n  --ground: #0a141e;', self.css)

    def test_later_theme_overrides_only_what_it_sets(self):
        light = self.css.split('[data-theme="light"] {')[1].split("}")[0]
        self.assertIn("--ground: #eef3f6;", light)
        self.assertIn("--glow: none;", light)
        self.assertNotIn("--same", light)

    def test_alias_becomes_var(self):
        self.assertIn("--alias: var(--ground);", self.css)

    def test_plain_families_and_type_styles(self):
        self.assertIn("--space-1: 0.3rem;", self.css)
        self.assertIn("--font-sans: Avenir, sans-serif;", self.css)
        self.assertIn(".body {\n  font-family: var(--font-sans);\n  font-size: 15px;\n  line-height: 1.5;\n}", self.css)


class NamespaceDriftTest(unittest.TestCase):
    def setUp(self):
        self.tokens = wkx.load_tokens()
        self.html = wkx.NAMESPACE_HTML.read_text(encoding="utf-8")

    def test_repo_namespace_matches_tokens(self):
        self.assertEqual(wkx.namespace_drift(self.html, self.tokens), [])

    def test_a_changed_colour_is_reported(self):
        drifted = self.html.replace("--add: #3DDC97;", "--add: #00FF00;", 1)
        problems = wkx.namespace_drift(drifted, self.tokens)
        self.assertEqual(len(problems), 1)
        self.assertIn("--add is #00FF00, token accent is #3ddc97", problems[0])

    def test_a_missing_light_block_is_reported(self):
        stripped = self.html.replace(':root[data-theme="light"]', ".gone", 1)
        stripped = stripped.replace(':root:not([data-theme="dark"])', ".gone", 1)
        self.assertIn("index.html: no light variable block found", wkx.namespace_drift(stripped, self.tokens))


class RepoTest(unittest.TestCase):
    def test_committed_tokens_css_is_current(self):
        self.assertEqual(wkx.TOKENS_CSS.read_text(encoding="utf-8"), wkx.build_css(wkx.load_tokens()))


if __name__ == "__main__":
    unittest.main()
