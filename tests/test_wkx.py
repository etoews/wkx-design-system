import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

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


class MarkdownTest(unittest.TestCase):
    def test_headings_shift_and_h1_can_drop(self):
        self.assertEqual(wkx.markdown("## Colour", shift=1), "<h3>Colour</h3>")
        self.assertEqual(wkx.markdown("# Button\n\nBody.", drop_h1=True), "<p>Body.</p>")

    def test_inline_code_bold_and_links(self):
        out = wkx.markdown("Use **`ink`** on [ground](#g).")
        self.assertEqual(out, '<p>Use <strong><code>ink</code></strong> on <a href="#g">ground</a>.</p>')

    def test_html_is_escaped_outside_and_inside_code(self):
        out = wkx.markdown("a <b> `<i>`")
        self.assertEqual(out, "<p>a &lt;b&gt; <code>&lt;i&gt;</code></p>")

    def test_lists_and_tables(self):
        self.assertEqual(wkx.markdown("- one\n- two"), "<ul><li>one</li><li>two</li></ul>")
        self.assertEqual(wkx.markdown("1. one\n2. two"), "<ol><li>one</li><li>two</li></ol>")
        table = wkx.markdown("| A | B |\n| --- | --- |\n| `x` | y |")
        self.assertIn("<th>A</th><th>B</th>", table)
        self.assertIn("<td><code>x</code></td><td>y</td>", table)


class PreviewTest(unittest.TestCase):
    PREVIEW = '<!-- @dsCard group="Data" height=130 -->\n<!doctype html>\n<html lang="en-NZ">\n<head><meta charset="utf-8"></head><body></body></html>'

    def test_marker_attributes(self):
        self.assertEqual(wkx._card_marker(self.PREVIEW), {"group": "Data", "height": "130"})

    def test_srcdoc_loads_the_system_before_the_preview(self):
        doc = wkx.preview_srcdoc(self.PREVIEW, "dark")
        self.assertTrue(doc.startswith("<!doctype html>"))
        self.assertIn('<html lang="en-NZ" data-theme="dark">', doc)
        head = doc.split("<head>")[1]
        self.assertLess(head.index("system/tokens.css"), head.index("system/components/bundle.js"))
        self.assertLess(head.index("react-dom@18.3.1"), head.index("system/components/bundle.js"))
        self.assertLess(head.index("bundle.js"), head.index('<meta charset="utf-8">'))


class PublishTest(unittest.TestCase):
    """publish-plan, mark-published and the hook, against a throwaway git repo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.patches = [
            mock.patch.object(wkx, "ROOT", self.root),
            mock.patch.object(wkx, "STAGE", self.root / ".publish"),
        ]
        for p in self.patches:
            p.start()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / "system" / "assets" / "Logos").mkdir(parents=True)
        self.write("system/design-system.json", '{"v": 3, "title": "WKX"}')
        self.write("system/tokens.json", "{}")
        self.write("system/README.md", "Book.")
        self.write("system/assets/Logos/mark.svg", "<svg/>")
        self.commit("first")

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def write(self, rel, text):
        (self.root / rel).write_text(text, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def plan(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(wkx.publish_plan(), 0)
        return json.loads(out.getvalue())

    def run_hook(self, event):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            wkx.hook()
        return out.getvalue()

    def test_first_publish_sends_everything_with_the_index_last(self):
        plan = self.plan()
        call = plan["artifact"]
        self.assertEqual(call["url"], wkx.ARTIFACT_URL)
        self.assertTrue(call["file_path"].endswith("project/design-system.json"))
        self.assertEqual(set(call["files"]), {"project/tokens.json", "project/README.md"})
        self.assertEqual(plan["uploads_first"], [str(self.root / "system/assets/Logos/mark.svg")])
        index = json.loads(Path(call["file_path"]).read_text())
        self.assertEqual(index["title"], "WKX")
        self.assertEqual(index["lastChange"]["note"], "first")
        self.assertTrue((self.root / ".publish/project/README.md").exists())

    def test_after_mark_published_only_changes_and_deletions_go(self):
        self.plan()
        with redirect_stdout(io.StringIO()):
            wkx.mark_published()
        self.assertFalse((self.root / ".publish").exists())
        self.assertFalse(self.plan()["publish"])
        self.write("system/README.md", "Book, revised.")
        (self.root / "system/tokens.json").unlink()
        self.commit("revise the book")
        files = self.plan()["artifact"]["files"]
        self.assertEqual(files, {"project/README.md": "project/README.md", "project/tokens.json": None})

    def test_unserved_extensions_name_their_type(self):
        (self.root / "system" / "components").mkdir()
        self.write("system/components/index.d.ts", "export {};")
        self.commit("types")
        files = self.plan()["artifact"]["files"]
        self.assertEqual(
            files["project/components/index.d.ts"],
            {"from": "project/components/index.d.ts", "contentType": "text/plain"},
        )
        self.assertEqual(files["project/README.md"], "project/README.md")

    def test_uncommitted_edits_are_not_published(self):
        self.write("system/README.md", "Not committed.")
        staged = self.root / ".publish/project/README.md"
        self.plan()
        self.assertEqual(staged.read_text(), "Book.")

    def test_publishes_from_main_only(self):
        self.git("switch", "-q", "-c", "feat/x")
        with redirect_stdout(io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(wkx.publish_plan(), 1)

    def test_hook_asks_after_a_push_from_main(self):
        out = self.run_hook({"hook_event_name": "PostToolUse", "tool_input": {"command": "git switch main && git merge --ff-only feat/x && git push"}})
        context = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "PostToolUse")
        self.assertIn("not yet published", context["additionalContext"])

    def test_hook_is_silent_otherwise(self):
        self.assertEqual(self.run_hook({"hook_event_name": "PostToolUse", "tool_input": {"command": "git status"}}), "")
        with redirect_stdout(io.StringIO()):
            wkx.mark_published()
        self.assertEqual(self.run_hook({"hook_event_name": "SessionStart"}), "")

    def test_hook_never_raises(self):
        with mock.patch.object(wkx, "_git", side_effect=RuntimeError("boom")):
            self.assertEqual(self.run_hook({"hook_event_name": "SessionStart"}), "")


class RepoTest(unittest.TestCase):
    def test_generated_files_are_current(self):
        for path, text in wkx.generated().items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_index_shows_every_component(self):
        page = wkx.INDEX_HTML.read_text(encoding="utf-8")
        for name in wkx._component_order():
            with self.subTest(component=name):
                self.assertIn(f'id="c-{name}"', page)
        self.assertEqual(len(wkx._component_order()), 13)


if __name__ == "__main__":
    unittest.main()
