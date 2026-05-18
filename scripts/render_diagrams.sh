#!/usr/bin/env bash
# Render every Python `diagrams` source under diagrams/python/ into images/.
# Idempotent: re-running produces byte-identical output if sources haven't changed.
#
# Requires: python3, the `diagrams` package, and graphviz installed.
#   pip install -r diagrams/python/requirements.txt
#   brew install graphviz   # or: apt-get install graphviz

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v dot >/dev/null 2>&1; then
  echo "error: graphviz 'dot' not found in PATH. Install graphviz first." >&2
  exit 1
fi

shopt -s globstar nullglob

count=0
for src in diagrams/python/**/*.py; do
  # Skip helper modules.
  case "$src" in
    diagrams/python/_shared/*) continue ;;
    */__init__.py) continue ;;
  esac

  # diagrams/python/<category>/<name>.py -> images/<category>/<name>.png
  rel="${src#diagrams/python/}"
  category="${rel%%/*}"
  name_py="${rel#*/}"
  name="${name_py%.py}"

  out_dir="images/${category}"
  out_path="${out_dir}/${name}.png"
  mkdir -p "$out_dir"

  echo "render: $src -> $out_path"

  # Run from a tmp dir so the `diagrams` library writes its file there, then move it.
  # This avoids `diagrams`' default behavior of writing the .png next to where it ran.
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' EXIT

  (
    cd "$tmp_dir"
    DIAGRAM_OUT_NAME="$name" python3 "$repo_root/$src"
  )

  # diagrams writes <Diagram name>.png — find the single new png and move it.
  produced="$(find "$tmp_dir" -maxdepth 1 -name '*.png' | head -n 1)"
  if [[ -z "$produced" ]]; then
    echo "  error: $src produced no .png" >&2
    exit 1
  fi
  mv "$produced" "$repo_root/$out_path"
  rm -rf "$tmp_dir"
  trap - EXIT

  count=$((count + 1))
done

echo "rendered $count diagram(s)"
