---
description: Sweep the current diff and recent edits, intentionally trying to remove as many comments as feasible
---

Find every code comment currently in scope and try to eliminate it by refactoring or outright deletion. Use this when comments have accumulated and you want a deliberate pass to remove them wherever feasible, not just the lighter check PipeDown's hook does on a single new comment.

## 1. Build the scope

Collect comments from both sources:

- Files this session has edited (via `Edit`, `Write`, `MultiEdit`, or `NotebookEdit`), whether or not the hook already reviewed them.
- The current diff: run `git diff` and `git diff --cached`. If the repository has no changes yet, or this isn't a git repository, fall back to whatever files were touched this session.

Include every comment in that scope, not only ones added in this conversation — a comment that predates this session but sits inside a changed hunk is fair game too.

## 2. Review and apply

Read `${CLAUDE_PLUGIN_ROOT}/uncomment_prompt.md` and follow it for every comment in scope, applying the edits directly as you go.
