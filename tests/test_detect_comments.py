import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _load(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


lexer = _load("comment_lexer", "comment_lexer.py")


def run_hook(script: str, event: dict, plugin_data: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        env={"CLAUDE_PLUGIN_DATA": plugin_data},
    )


class CommentDetectionTests(unittest.TestCase):
    def test_detects_new_line_comment(self):
        self.assertTrue(lexer.introduces_comment("Edit", {
            "file_path": "app.ts",
            "old_string": "const total = amount;",
            "new_string": "// Preserve the invoiced amount\nconst total = amount;",
        }))

    def test_detects_new_block_comment(self):
        self.assertTrue(lexer.introduces_comment("Edit", {
            "file_path": "main.css",
            "old_string": ".item { color: red; }",
            "new_string": "/* Required by the legacy theme */\n.item { color: red; }",
        }))

    def test_ignores_comment_markers_in_strings(self):
        self.assertFalse(lexer.introduces_comment("Edit", {
            "file_path": "app.js",
            "old_string": "const path = '';",
            "new_string": "const path = 'https://example.test/a';",
        }))

    def test_ignores_unchanged_comment(self):
        self.assertFalse(lexer.introduces_comment("Edit", {
            "file_path": "app.py",
            "old_string": "# Explain why\nvalue = 1",
            "new_string": "# Explain why\nvalue = 2",
        }))

    def test_handles_python_triple_quoted_strings(self):
        self.assertTrue(lexer.introduces_comment("Edit", {
            "file_path": "app.py",
            "old_string": 'text = """not # a comment"""',
            "new_string": 'text = """not # a comment"""\n# Actual comment',
        }))

    def test_ignores_shebang(self):
        self.assertFalse(lexer.introduces_comment("Write", {
            "file_path": "/tmp/new-script.sh",
            "content": "#!/bin/sh\nprintf '%s\\n' hello\n",
        }))

    def test_unknown_extension_fails_open(self):
        self.assertFalse(lexer.introduces_comment("Edit", {
            "file_path": "data.unknown",
            "old_string": "value",
            "new_string": "# value",
        }))


class HookScriptTests(unittest.TestCase):
    def test_forces_review_after_successful_edit_with_new_comment(self):
        pre_event = {
            "hook_event_name": "PreToolUse",
            "tool_use_id": "toolu_test",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "main.go",
                "old_string": "package main",
                "new_string": "// Package main runs the app.\npackage main",
            },
        }
        with tempfile.TemporaryDirectory() as plugin_data:
            pre_result = run_hook("pre_tool_use.py", pre_event, plugin_data)
            self.assertEqual(pre_result.returncode, 0)
            self.assertEqual(pre_result.stdout, "")

            post_event = {**pre_event, "hook_event_name": "PostToolUse", "tool_response": {"success": True}}
            post_result = run_hook("post_tool_use.py", post_event, plugin_data)
            self.assertEqual(post_result.returncode, 2)
            self.assertEqual(post_result.stdout, "")
            self.assertIn("A new code comment was detected", post_result.stderr)

            repeated_post = run_hook("post_tool_use.py", post_event, plugin_data)
            self.assertEqual(repeated_post.returncode, 0)
            self.assertEqual(repeated_post.stderr, "")

    def test_no_marker_written_without_a_new_comment(self):
        pre_event = {
            "hook_event_name": "PreToolUse",
            "tool_use_id": "toolu_no_comment",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "main.go",
                "old_string": "package main",
                "new_string": "package main\n\nfunc main() {}",
            },
        }
        with tempfile.TemporaryDirectory() as plugin_data:
            pre_result = run_hook("pre_tool_use.py", pre_event, plugin_data)
            self.assertEqual(pre_result.returncode, 0)

            post_event = {**pre_event, "hook_event_name": "PostToolUse", "tool_response": {"success": True}}
            post_result = run_hook("post_tool_use.py", post_event, plugin_data)
            self.assertEqual(post_result.returncode, 0)
            self.assertEqual(post_result.stderr, "")

    def test_failure_clears_marker_without_review(self):
        pre_event = {
            "hook_event_name": "PreToolUse",
            "tool_use_id": "toolu_failure",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "main.go",
                "old_string": "package main",
                "new_string": "// Package main runs the app.\npackage main",
            },
        }
        with tempfile.TemporaryDirectory() as plugin_data:
            run_hook("pre_tool_use.py", pre_event, plugin_data)

            failure_event = {**pre_event, "hook_event_name": "PostToolUseFailure"}
            failure_result = run_hook("post_tool_use.py", failure_event, plugin_data)
            self.assertEqual(failure_result.returncode, 0)

            post_event = {**pre_event, "hook_event_name": "PostToolUse", "tool_response": {"success": True}}
            post_result = run_hook("post_tool_use.py", post_event, plugin_data)
            self.assertEqual(post_result.returncode, 0)
            self.assertEqual(post_result.stderr, "")


if __name__ == "__main__":
    unittest.main()
