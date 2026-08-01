#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_ROOT=$(dirname -- "$SCRIPT_DIR")
MARKETPLACE_NAME="commenter-plugins"
PLUGIN_NAME="commenter"
PLUGIN_ID="${PLUGIN_NAME}@${MARKETPLACE_NAME}"
CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_CACHE_DIR="${CONFIG_DIR}/plugins/cache/${MARKETPLACE_NAME}/${PLUGIN_NAME}"

command -v claude >/dev/null 2>&1 || {
    printf '%s\n' "Error: Claude Code is not installed or is not on PATH." >&2
    exit 1
}

is_installed() {
    claude plugin list --json | python3 -c \
        'import json, sys; target = sys.argv[1]; raise SystemExit(not any(item.get("id") == target and item.get("scope") == "user" for item in json.load(sys.stdin)))' \
        "$PLUGIN_ID"
}

marketplace_exists() {
    claude plugin marketplace list --json | python3 -c \
        'import json, sys; target = sys.argv[1]; raise SystemExit(not any(item.get("name") == target for item in json.load(sys.stdin)))' \
        "$MARKETPLACE_NAME"
}

if is_installed; then
    printf '%s\n' "Removing the existing ${PLUGIN_ID} installation..."
    claude plugin uninstall --scope user --keep-data "$PLUGIN_ID"
fi

if marketplace_exists; then
    printf '%s\n' "Refreshing the ${MARKETPLACE_NAME} marketplace source..."
    claude plugin marketplace remove "$MARKETPLACE_NAME"
fi

if [ -d "$PLUGIN_CACHE_DIR" ]; then
    # Cache dirs are keyed by source commit hash, so redeploying uncommitted
    # changes against the same commit reuses one; install only adds/overwrites
    # files there, never deletes ones removed from source. Purge first so
    # stale files from a prior layout can't survive alongside the new copy.
    printf '%s\n' "Clearing cached plugin versions at ${PLUGIN_CACHE_DIR}..."
    rm -rf -- "$PLUGIN_CACHE_DIR"
fi

claude plugin marketplace add --scope user "$PLUGIN_ROOT"
claude plugin install --scope user "$PLUGIN_ID"

printf '%s\n' "Installed ${PLUGIN_ID} from ${PLUGIN_ROOT}."
printf '%s\n' "Restart active Claude Code sessions to load the new copy."
