#!/usr/bin/env python3
"""PreToolUse hook: detect whether a proposed edit introduces a new comment.

Never blocks the edit. If a new comment is found, a marker file is written
so the PostToolUse hook (post_tool_use.py) knows to request a review after
the edit succeeds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from comment_lexer import introduces_comment, marker_path, plugin_data_dir


def main() -> int:
    try:
        event = json.load(sys.stdin)
        tool_name = str(event.get("tool_name", ""))
        tool_input = event.get("tool_input", {})
        if not isinstance(tool_input, dict):
            return 0

        if not introduces_comment(tool_name, tool_input):
            return 0

        plugin_root = Path(__file__).resolve().parent.parent
        marker = marker_path(event, plugin_data_dir(plugin_root))
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
