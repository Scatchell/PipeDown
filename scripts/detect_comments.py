#!/usr/bin/env python3
"""Challenge Claude Code once when an edit introduces comment tokens."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


HASH_EXTENSIONS = {
    ".conf", ".ini", ".pl", ".pm", ".py", ".r", ".rb", ".sh", ".toml", ".yaml", ".yml",
}
SLASH_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".css", ".dart", ".go", ".h", ".hpp", ".java", ".js",
    ".jsx", ".kt", ".kts", ".less", ".m", ".mm", ".php", ".rs", ".sass", ".scss", ".sol",
    ".swift", ".ts", ".tsx", ".vue",
}
SQL_EXTENSIONS = {".sql"}
LUA_EXTENSIONS = {".lua"}
MARKUP_EXTENSIONS = {".astro", ".htm", ".html", ".md", ".mdx", ".svelte", ".xml"}


def syntax_for(path: str) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]] | None:
    extension = Path(path).suffix.lower()
    name = Path(path).name.lower()
    if extension in HASH_EXTENSIONS or name in {"dockerfile", "makefile", "rakefile"}:
        return (("#",), ())
    if extension in SLASH_EXTENSIONS:
        return (("//",), (("/*", "*/"),))
    if extension in SQL_EXTENSIONS:
        return (("--",), (("/*", "*/"),))
    if extension in LUA_EXTENSIONS:
        return (("--",), (("--[[", "]]"),))
    if extension in MARKUP_EXTENSIONS:
        return ((), (("<!--", "-->"),))
    return None


def extract_comments(text: str, syntax: tuple[tuple[str, ...], tuple[tuple[str, str], ...]]) -> list[str]:
    line_markers, block_markers = syntax
    comments: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if text.startswith(quote, index):
                quote_length = len(quote)
                quote = None
                index += quote_length
                continue
            index += 1
            continue
        opening_quote = next((item for item in ("'''", '\"\"\"', "'", '"', "`") if text.startswith(item, index)), None)
        if opening_quote:
            quote = opening_quote
            index += len(opening_quote)
            continue

        block = next(((start, end) for start, end in block_markers if text.startswith(start, index)), None)
        if block:
            start, end = block
            end_index = text.find(end, index + len(start))
            end_index = len(text) if end_index < 0 else end_index + len(end)
            comments.append(text[index:end_index].strip())
            index = end_index
            continue

        marker = next((item for item in line_markers if text.startswith(item, index)), None)
        if marker:
            end_index = text.find("\n", index)
            end_index = len(text) if end_index < 0 else end_index
            comment = text[index:end_index].strip()
            if not (marker == "#" and comment.startswith("#!") and index == 0):
                comments.append(comment)
            index = end_index
            continue
        index += 1
    return comments


def read_existing(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def proposed_changes(tool_name: str, tool_input: dict[str, Any]) -> list[tuple[str, str, str]]:
    path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if tool_name == "Write":
        return [(path, read_existing(path), str(tool_input.get("content", "")))]
    if tool_name == "Edit":
        return [(path, str(tool_input.get("old_string", "")), str(tool_input.get("new_string", "")))]
    if tool_name == "MultiEdit":
        return [
            (path, str(edit.get("old_string", "")), str(edit.get("new_string", "")))
            for edit in tool_input.get("edits", [])
            if isinstance(edit, dict)
        ]
    if tool_name == "NotebookEdit":
        old = str(tool_input.get("old_source", tool_input.get("old_string", "")))
        new = str(tool_input.get("new_source", tool_input.get("new_string", "")))
        return [(path, old, new)]
    return []


def introduces_comment(tool_name: str, tool_input: dict[str, Any]) -> bool:
    for path, before, after in proposed_changes(tool_name, tool_input):
        syntax = syntax_for(path)
        if syntax is None:
            continue
        old_comments = Counter(extract_comments(before, syntax))
        new_comments = Counter(extract_comments(after, syntax))
        if new_comments - old_comments:
            return True
    return False


def was_already_challenged(event: dict[str, Any], plugin_data: Path) -> bool:
    """Record a proposed edit without storing its source text."""
    identity = {
        "session_id": event.get("session_id", "unknown-session"),
        "tool_name": event.get("tool_name", ""),
        "tool_input": event.get("tool_input", {}),
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    state_path = plugin_data / "challenged-edits.json"
    try:
        challenged = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(challenged, list):
            challenged = []
    except (OSError, UnicodeError, json.JSONDecodeError):
        challenged = []
    if digest in challenged:
        return True
    plugin_data.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps((challenged + [digest])[-1000:]), encoding="utf-8")
    return False


def main() -> int:
    try:
        event = json.load(sys.stdin)
        tool_name = str(event.get("tool_name", ""))
        tool_input = event.get("tool_input", {})
        if not isinstance(tool_input, dict) or not introduces_comment(tool_name, tool_input):
            return 0

        plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
        plugin_data = Path(os.environ.get("CLAUDE_PLUGIN_DATA", plugin_root / ".commenter-data"))
        if was_already_challenged(event, plugin_data):
            return 0
        prompt = (plugin_root / "prompt.md").read_text(encoding="utf-8").strip()
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": prompt,
            }
        }
        json.dump(output, sys.stdout)
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
