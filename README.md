# Commenter

Commenter is a Claude Code plugin that reviews newly added code comments after successful file edits. It uses a deterministic, dependency-free lexer; no model call is used for detection.

When a supported edit introduces a comment, the PostToolUse hook forces the contents of [`prompt.md`](prompt.md) onto Claude by exiting with status `2` and writing the prompt to stderr. Edits with comments are never rejected, but the review is surfaced as feedback Claude must respond to (not as easily-skipped or forgotten ambient context). Claude reviews the completed change once and can remove an unnecessary comment, improve the surrounding code, or retain a justified comment unchanged. The review fires exactly once per comment-introducing edit; if Claude judges the comment justified, nothing repeats or re-checks it.

Note: When claude changes a comment (e.g. to tighten or summarize a long comment) this plugin DOES execute again and recheck the tightened comment. This is unnecessary but not dangerous.

## How It Works

```
Agent calls Edit/Write/MultiEdit/NotebookEdit
        |
        v
hooks.json -> PreToolUse matcher fires
        |
        v
scripts/pre_tool_use.py runs
   - diffs old vs new content with comment_lexer.py
   - new comment found? -> write a marker file keyed by tool_use_id
   - no new comment?     -> exit 0, no marker
   - always exits 0 / allows the edit through either way
        |
        v
   [ tool actually executes ]
        |
        v
hooks.json -> PostToolUse or PostToolUseFailure matcher fires
        |
        v
scripts/post_tool_use.py runs
   - event == PostToolUseFailure -> delete marker if present, exit 0
   - event == PostToolUse:
        - marker missing -> exit 0 (no comment was introduced)
        - marker present -> delete marker (one-shot), write prompt.md
          to stderr, exit 2
                -> Claude sees prompt.md content as required feedback
                   on that tool call, reviews the comment(s) once,
                   decides keep or remove, moves on
                -> marker is gone, this exact edit will never nag again
```

`scripts/comment_lexer.py` is a shared library, not a hook entry point — it holds the comment-syntax detection logic used by both `pre_tool_use.py` and `post_tool_use.py` so it isn't duplicated between them. Only `pre_tool_use.py` and `post_tool_use.py` are registered in [`hooks/hooks.json`](hooks/hooks.json).

## Requirements

- Claude Code with plugin support
- Python 3.9 or newer available as `python3`


## Install From GitHub

A public repository is not required for local use. For easy installation on other machines, push this directory to a GitHub repository, then use:

```text
/plugin marketplace add Scatchell/commenter
/plugin install commenter@commenter-plugins
```

To update after new changes are pushed to this repo, use Claude's marketplace update commands:

```text
/plugin marketplace update commenter-plugins
/plugin update commenter@commenter-plugins
```

The manifest intentionally has no fixed version, so each new Git commit can be detected as a new plugin version for GitHub marketplace installations.

## Customize The Challenge

Edit [`prompt.md`](prompt.md). The complete file is returned to Claude whenever a new comment is found. Run `/reload-plugins` when testing directly from source, or rerun `./scripts/deploy.sh` to replace the permanent installation.

## Detection Scope

The hook watches `Edit`, `Write`, `MultiEdit`, and `NotebookEdit`. It recognizes common comment forms in Python, Ruby, shell, Perl, R, YAML, TOML, C-family languages, JavaScript/TypeScript, CSS, SQL, Lua, HTML/XML, and related file extensions.

Existing unchanged comments, comment delimiters inside ordinary quoted strings, and shebang lines do not trigger the hook. Unknown file extensions and malformed hook input fail open. Detection is lexical rather than parser-based, so unusual language constructs can produce false positives or false negatives.

For accurate `Write` detection, the pre-edit hook records a temporary marker keyed by Claude's tool-use ID. After a successful edit, the marker is consumed and the review is forced via stderr and exit code `2` (see [How It Works](#how-it-works)). Source text and comment text are never stored.

## Developer local install

Run the deployment script from anywhere:

```sh
./scripts/deploy.sh
```

The script determines the plugin root from its own location, registers this checkout as a user-level marketplace, and installs the plugin into Claude Code's plugin cache. The installation is permanent across Claude Code sessions; you do not need to run the script again unless you want to deploy a changed version.

Restart active Claude Code sessions after deployment so they load the installed copy.

Run the test suite before deploying local changes:

```sh
python3 -m unittest discover -s tests -v
```

### Update Or Reinstall Locally

Run the same command after changing or pulling the source:

```sh
./scripts/deploy.sh
```

Deployment preserves the plugin's persistent data, removes the previous installed copy, refreshes the marketplace path, and installs the current source. Replacing the installation rather than using version-based updates ensures uncommitted local changes are deployed too.

To test directly from source without installing, run this from the repository's parent directory:

```sh
claude --plugin-dir ./commenter
```


### Run Tests

```sh
python3 -m unittest discover -s tests -v
```
