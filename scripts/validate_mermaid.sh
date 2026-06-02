#!/usr/bin/env bash
# Extract every ```mermaid block from the markdown files passed as arguments
# and validate each one with mermaid-cli (mmdc).
#
# Usage:
#   scripts/validate_mermaid.sh path/to/file.md [more.md ...]
#
# Requires: mmdc on PATH (`npm install -g @mermaid-js/mermaid-cli`).

set -euo pipefail

if [[ $# -eq 0 ]]; then
  exit 0
fi

if ! command -v mmdc >/dev/null 2>&1; then
  echo "error: mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

# Headless Chrome can't use its sandbox in most CI containers; point mmdc at a
# puppeteer config that launches with --no-sandbox. Repo-local file wins, but a
# caller can override with PUPPETEER_CONFIG.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
puppeteer_config="${PUPPETEER_CONFIG:-$repo_root/.puppeteer.json}"
mmdc_args=()
if [[ -f "$puppeteer_config" ]]; then
  mmdc_args+=(--puppeteerConfigFile "$puppeteer_config")
fi

fail=0
for md in "$@"; do
  [[ -f "$md" ]] || continue
  # Skip files that have no mermaid blocks.
  grep -q '^```mermaid' "$md" || continue

  safe_src="${md//\//_}"
  awk -v out="$tmp_dir" -v safe="$safe_src" '
    /^```mermaid/ { in_block=1; block_idx++; file=sprintf("%s/%s.%d.mmd", out, safe, block_idx); next }
    /^```/ && in_block { in_block=0; next }
    in_block { print > file }
  ' "$md"

  for mmd in "$tmp_dir/$(printf '%s' "$md" | sed 's,/,_,g')".*.mmd; do
    [[ -f "$mmd" ]] || continue
    if ! err="$(mmdc "${mmdc_args[@]}" --input "$mmd" --output "${mmd%.mmd}.svg" --quiet 2>&1)"; then
      echo "::error file=$md::Mermaid block failed to render. Re-run locally with: mmdc -i $mmd -o out.svg" >&2
      echo "$err" >&2
      fail=1
    fi
  done
done

exit "$fail"
