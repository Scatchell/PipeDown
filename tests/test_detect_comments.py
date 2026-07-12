import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("detect_comments", ROOT / "scripts/detect_comments.py")
assert SPEC is not None
detector = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(detector)


class CommentDetectionTests(unittest.TestCase):
    def test_detects_new_line_comment(self):
        self.assertTrue(detector.introduces_comment("Edit", {
            "file_path": "app.ts",
            "old_string": "const total = amount;",
            "new_string": "// Preserve the invoiced amount\nconst total = amount;",
        }))

    def test_detects_new_block_comment(self):
        self.assertTrue(detector.introduces_comment("Edit", {
            "file_path": "main.css",
            "old_string": ".item { color: red; }",
            "new_string": "/* Required by the legacy theme */\n.item { color: red; }",
        }))

    def test_ignores_comment_markers_in_strings(self):
        self.assertFalse(detector.introduces_comment("Edit", {
            "file_path": "app.js",
            "old_string": "const path = '';",
            "new_string": "const path = 'https://example.test/a';",
        }))

    def test_ignores_unchanged_comment(self):
        self.assertFalse(detector.introduces_comment("Edit", {
            "file_path": "app.py",
            "old_string": "# Explain why\nvalue = 1",
            "new_string": "# Explain why\nvalue = 2",
        }))

    def test_handles_python_triple_quoted_strings(self):
        self.assertTrue(detector.introduces_comment("Edit", {
            "file_path": "app.py",
            "old_string": 'text = """not # a comment"""',
            "new_string": 'text = """not # a comment"""\n# Actual comment',
        }))

    def test_ignores_shebang(self):
        self.assertFalse(detector.introduces_comment("Write", {
            "file_path": "/tmp/new-script.sh",
            "content": "#!/bin/sh\nprintf '%s\\n' hello\n",
        }))

    def test_unknown_extension_fails_open(self):
        self.assertFalse(detector.introduces_comment("Edit", {
            "file_path": "data.unknown",
            "old_string": "value",
            "new_string": "# value",
        }))

    def test_cli_returns_denial_with_prompt(self):
        event = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "main.go",
                "old_string": "package main",
                "new_string": "// Package main runs the app.\npackage main",
            },
        }
        with tempfile.TemporaryDirectory() as plugin_data:
            environment = {"CLAUDE_PLUGIN_DATA": plugin_data}
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/detect_comments.py")],
                input=json.dumps(event), text=True, capture_output=True, check=True, env=environment,
            )
            output = json.loads(result.stdout)
            decision = output["hookSpecificOutput"]
            self.assertEqual(decision["permissionDecision"], "deny")
            self.assertIn("A new code comment was detected", decision["permissionDecisionReason"])

            retry = subprocess.run(
                [sys.executable, str(ROOT / "scripts/detect_comments.py")],
                input=json.dumps(event), text=True, capture_output=True, check=True, env=environment,
            )
            self.assertEqual(retry.stdout, "")


if __name__ == "__main__":
    unittest.main()
