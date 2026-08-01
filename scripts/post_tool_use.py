#!/usr/bin/env python3
"""PostToolUse / PostToolUseFailure hook: consume the marker written by
pre_tool_use.py and, on success, force a one-time review of the new comment.

The review prompt is written to stderr with exit code 2 rather than emitted
as passive additionalContext. PostToolUse hooks that exit 2 have their
stderr surfaced to Claude as feedback tied directly to that tool call, which
Claude must respond to -- unlike additionalContext, which is just appended
context and easy to skim past under a long transcript. The edit itself is
never undone or blocked; this only shapes how forcefully the follow-up
review is presented.

The marker is deleted before the prompt is emitted, so this fires exactly
once per comment-introducing edit. If Claude decides the comment is
justified, nothing repeats it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from comment_lexer import marker_path, plugin_data_dir


def main() -> int:
    try:
        event = json.load(sys.stdin)
        event_name = str(event.get("hook_event_name", ""))

        plugin_root = Path(__file__).resolve().parent.parent
        marker = marker_path(event, plugin_data_dir(plugin_root))

        if event_name == "PostToolUseFailure":
            marker.unlink(missing_ok=True)
            return 0

        if event_name != "PostToolUse" or not marker.exists():
            return 0
        marker.unlink()

        prompt = (plugin_root / "prompt.md").read_text(encoding="utf-8").strip()
        print(prompt, file=sys.stderr)
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
