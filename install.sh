#!/usr/bin/env bash
# Copy skills into your Claude Code skills directory. Existing skills are kept
# unless you pass --force.
set -euo pipefail
FORCE=0; [ "${1:-}" = "--force" ] && FORCE=1
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
SRC="$(cd "$(dirname "$0")/skills" && pwd)"
mkdir -p "$DEST"
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  if [ -e "$DEST/$name" ] && [ "$FORCE" -eq 0 ]; then
    echo "skip       $name (already installed; --force to overwrite)"; continue
  fi
  rm -rf "${DEST:?}/$name"; cp -r "$dir" "$DEST/$name"
  echo "installed  $name"
done
echo; echo "Done. Restart Claude Code."
