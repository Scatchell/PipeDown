# Commenter

Commenter is a Claude Code plugin that intercepts file edits and challenges newly added code comments before they are written. It uses a deterministic, dependency-free lexer; no model call is used for detection.

When a supported edit introduces a comment, the hook pauses that distinct edit once and sends the contents of [`prompt.md`](prompt.md) to Claude as the reason. Claude can then retry with clearer code or retain a genuinely useful comment after reconsidering it. An unchanged retry is allowed, so the plugin does not prohibit comments.

## Requirements

- Claude Code with plugin support
- Python 3.9 or newer available as `python3`

## Try From Source

From the parent of this directory, start Claude Code with:

```sh
claude --plugin-dir ./commenter
```

Run `/reload-plugins` after changing the plugin during development.

## Install Locally

Inside Claude Code, add this checkout as a local marketplace and install the plugin:

```text
/plugin marketplace add /absolute/path/to/commenter
/plugin install commenter@commenter-plugins
```

To update a local installation after pulling source changes:

```text
/plugin marketplace update commenter-plugins
/plugin update commenter@commenter-plugins
```

Restart Claude Code or run `/reload-plugins` after installation or update.

## Install From GitHub

A public repository is not required for local use. For easy installation on other machines, push this directory to a GitHub repository, then use:

```text
/plugin marketplace add OWNER/REPOSITORY
/plugin install commenter@commenter-plugins
```

To update after changes are pushed:

```text
/plugin marketplace update commenter-plugins
/plugin update commenter@commenter-plugins
```

The manifest intentionally has no fixed version, so each new Git commit can be detected as a new plugin version.

## Customize The Challenge

Edit [`prompt.md`](prompt.md). The complete file is returned to Claude whenever a new comment is found. Run `/reload-plugins` when testing directly from source. Installed copies must be updated through their marketplace after the source changes.

## Detection Scope

The hook watches `Edit`, `Write`, `MultiEdit`, and `NotebookEdit`. It recognizes common comment forms in Python, Ruby, shell, Perl, R, YAML, TOML, C-family languages, JavaScript/TypeScript, CSS, SQL, Lua, HTML/XML, and related file extensions.

Existing unchanged comments, comment delimiters inside ordinary quoted strings, and shebang lines do not trigger the hook. Unknown file extensions and malformed hook input fail open. Detection is lexical rather than parser-based, so unusual language constructs can produce false positives or false negatives.

The plugin stores only hashes of the last 1,000 challenged edits in Claude's plugin data directory. Source text and comment text are not stored. A distinct revised edit is challenged again; an identical retry is not.

## Test

```sh
python3 -m unittest discover -s tests -v
```
