# Commenter

Commenter is a Claude Code plugin that reviews newly added code comments after successful file edits. It uses a deterministic, dependency-free lexer; no model call is used for detection.

When a supported edit introduces a comment, the hook sends the contents of [`prompt.md`](prompt.md) to Claude as non-blocking additional context. The edit is never rejected. Claude reviews the completed change and can remove an unnecessary comment, improve the surrounding code, or retain a justified comment unchanged.

## Requirements

- Claude Code with plugin support
- Python 3.9 or newer available as `python3`

## Install

Run the deployment script from anywhere:

```sh
./scripts/deploy.sh
```

The script determines the plugin root from its own location, registers this checkout as a user-level marketplace, and installs the plugin into Claude Code's plugin cache. The installation is permanent across Claude Code sessions; you do not need to run the script again unless you want to deploy a changed version.

Restart active Claude Code sessions after deployment so they load the installed copy.

## Update Or Reinstall

Run the same command after changing or pulling the source:

```sh
./scripts/deploy.sh
```

Deployment preserves the plugin's persistent data, removes the previous installed copy, refreshes the marketplace path, and installs the current source. Replacing the installation rather than using version-based updates ensures uncommitted local changes are deployed too.

To test directly from source without installing, run this from the repository's parent directory:

```sh
claude --plugin-dir ./commenter
```

## Install From GitHub

A public repository is not required for local use. For easy installation on other machines, push this directory to a GitHub repository, then use:

```text
/plugin marketplace add OWNER/REPOSITORY
/plugin install commenter@commenter-plugins
```

To update after changes are pushed, either run `./scripts/deploy.sh` from a checkout or use Claude's marketplace update commands:

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

For accurate `Write` detection, a silent pre-edit hook records a temporary marker keyed by Claude's tool-use ID. After a successful edit, the marker is consumed and the review guidance is injected. Source text and comment text are never stored.

## Test

```sh
python3 -m unittest discover -s tests -v
```
