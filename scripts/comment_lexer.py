#!/usr/bin/env python3
"""Shared lexical comment-detection helpers used by the pre/post tool-use hooks."""

from __future__ import annotations

import hashlib
import os
from collections import Counter
from pathlib import Path
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

Syntax = tuple[tuple[str, ...], tuple[tuple[str, str], ...]]


def syntax_for(path: str) -> Syntax | None:
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


def extract_comments(text: str, syntax: Syntax) -> list[str]:
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


def plugin_data_dir(plugin_root: Path) -> Path:
    return Path(os.environ.get("CLAUDE_PLUGIN_DATA", plugin_root / ".commenter-data"))


def marker_path(event: dict[str, Any], plugin_data: Path) -> Path:
    tool_use_id = str(event.get("tool_use_id", "unknown-tool-use"))
    digest = hashlib.sha256(tool_use_id.encode("utf-8")).hexdigest()
    return plugin_data / "pending-comment-reviews" / digest
