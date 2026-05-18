#!/usr/bin/env bash
# Scaffold a new markdown page from the canonical template.
#
# Usage:
#   scripts/new_page.sh <kind> <slug>
#
# <kind> is one of:
#   service   -> docs/01-services/<slug>.md       (slug includes category, e.g. compute/app-runner)
#   pattern   -> docs/02-patterns/<slug>.md
#   design    -> docs/03-interview-designs/<slug>.md
#   refarch   -> docs/04-reference-architectures/<slug>.md
#   pillar    -> docs/05-well-architected/<slug>.md
#
# Example:
#   scripts/new_page.sh service compute/app-runner
#   scripts/new_page.sh design real-time-leaderboard

set -euo pipefail

if [[ $# -ne 2 ]]; then
  sed -n '3,16p' "$0"
  exit 1
fi

kind="$1"
slug="$2"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

case "$kind" in
  service)  target="docs/01-services/${slug}.md" ;;
  pattern)  target="docs/02-patterns/${slug}.md" ;;
  design)   target="docs/03-interview-designs/${slug}.md" ;;
  refarch)  target="docs/04-reference-architectures/${slug}.md" ;;
  pillar)   target="docs/05-well-architected/${slug}.md" ;;
  *)
    echo "error: unknown kind '$kind'" >&2
    echo "       expected one of: service, pattern, design, refarch, pillar" >&2
    exit 1
    ;;
esac

if [[ -e "$target" ]]; then
  echo "error: $target already exists" >&2
  exit 1
fi

mkdir -p "$(dirname "$target")"

# Derive a Title-Case title from the slug's final segment.
base="$(basename "$slug")"
title="$(printf '%s' "$base" | tr '-_' '  ' | awk '{for(i=1;i<=NF;i++)$i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')"

if [[ "$kind" == "service" ]]; then
  cat > "$target" <<EOF
# ${title}

> **One-line summary.**

## TL;DR
- TODO
- TODO
- TODO

## When to use it
- TODO

## When NOT to use it
- TODO

## Key concepts
TODO

## Pricing model
TODO

## Quotas & limits
TODO — link to the official quotas page.

## Common pitfalls
- TODO

## Pairs well with
- TODO

## Further reading
- TODO
EOF
else
  cat > "$target" <<EOF
# ${title}

> **One-line summary.**

## TL;DR
- TODO
- TODO
- TODO

## When to use it / When NOT to use it
TODO — two short opinionated lists.

## Functional Requirements
TODO

## Non-Functional Requirements
TODO

## Capacity Estimates
TODO — DAU, QPS, storage growth, bandwidth.

## High-Level Architecture
TODO — Mermaid inline, or \`![](../../images/<category>/<name>.png)\`.

## Data Model
TODO — \`erDiagram\` plus per-table notes.

## API Design
TODO

## Deep Dives
### Hard Part #1
TODO

### Hard Part #2
TODO

### Hard Part #3
TODO

## AWS Services Used
- TODO

## Cost Notes
TODO

## Failure Modes & DR
TODO

## Trade-offs & Alternatives
TODO

## Further Reading
- TODO
EOF
fi

echo "created $target"

if [[ "$kind" == "design" || "$kind" == "refarch" ]]; then
  diag_dir="diagrams/python/$( [[ "$kind" == "design" ]] && echo interview-designs || echo reference-architectures )"
  py_name="$(printf '%s' "$base" | tr '-' '_').py"
  py_path="${diag_dir}/${py_name}"
  if [[ ! -e "$py_path" ]]; then
    mkdir -p "$diag_dir"
    cat > "$py_path" <<EOF
"""High-level architecture for ${title}.

Belongs to: ${target}
"""
import os
from diagrams import Diagram

OUT = os.environ.get("DIAGRAM_OUT_NAME", "${base}")

with Diagram("${title}", filename=OUT, show=False, direction="LR"):
    # TODO: model the system.
    pass
EOF
    echo "created $py_path"
  fi
fi
