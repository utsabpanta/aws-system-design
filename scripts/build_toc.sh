#!/usr/bin/env bash
# Regenerate the table of contents in README.md from the docs/ tree.
# Pass --check to fail (exit 1) if the README is out of sync.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHON="${PYTHON:-python3}"
if [[ -x "$repo_root/.venv/bin/python3" ]]; then
  PYTHON="$repo_root/.venv/bin/python3"
fi

exec "$PYTHON" "$repo_root/scripts/build_toc.py" "$@"
