"""Build the table of contents for README.md from the docs/ tree.

Walks docs/, reads the first H1 of each markdown file, and emits a nested
list grouped by section (top-level docs/ subdirectory) and, for services,
by category (next-level subdirectory).

The script rewrites README.md between the markers:

    <!-- TOC START -->
    ...
    <!-- TOC END -->

Run with no args to write the TOC. Run with --check to fail if the README
is out of sync (used in CI).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
README = REPO_ROOT / "README.md"

TOC_START = "<!-- TOC START -->"
TOC_END = "<!-- TOC END -->"

# Display labels for top-level sections. Falls back to a derived label if absent.
SECTION_LABELS = {
    "00-getting-started": "00 — Getting started",
    "01-services": "01 — Services",
    "02-patterns": "02 — Patterns",
    "03-interview-designs": "03 — Interview designs",
    "04-reference-architectures": "04 — Reference architectures",
    "05-well-architected": "05 — Well-Architected",
}

# Display labels for service subcategories (docs/01-services/<dir>/).
SERVICE_CATEGORY_LABELS = {
    "analytics": "Analytics",
    "compute": "Compute",
    "database": "Database",
    "devops": "DevOps",
    "edge": "Edge",
    "integration-messaging": "Integration & Messaging",
    "migration-transfer": "Migration & Transfer",
    "ml-ai": "ML / AI",
    "networking": "Networking",
    "observability": "Observability",
    "security-identity": "Security & Identity",
    "storage": "Storage",
}

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def extract_title(path: Path) -> str:
    """Return the first H1 of a markdown file, or the filename if none found."""
    text = path.read_text(encoding="utf-8")
    match = H1_RE.search(text)
    if match:
        return match.group(1).strip()
    return path.stem


def section_label(name: str) -> str:
    return SECTION_LABELS.get(name, name.replace("-", " ").title())


def service_label(name: str) -> str:
    return SERVICE_CATEGORY_LABELS.get(name, name.replace("-", " ").title())


def rel_link(path: Path) -> str:
    """POSIX-style path relative to the repo root, for Markdown links."""
    return path.relative_to(REPO_ROOT).as_posix()


def build_toc() -> str:
    lines: list[str] = [TOC_START, ""]

    sections = sorted(p for p in DOCS_DIR.iterdir() if p.is_dir())
    for section in sections:
        lines.append(f"### {section_label(section.name)}")
        lines.append("")

        # 01-services has a category layer; everything else is flat.
        has_subcategories = any(child.is_dir() for child in section.iterdir())

        if has_subcategories:
            categories = sorted(c for c in section.iterdir() if c.is_dir())
            for cat in categories:
                lines.append(f"#### {service_label(cat.name)}")
                lines.append("")
                pages = sorted(cat.glob("*.md"))
                for page in pages:
                    title = extract_title(page)
                    lines.append(f"- [{title}]({rel_link(page)})")
                lines.append("")
        else:
            pages = sorted(section.glob("*.md"))
            for page in pages:
                title = extract_title(page)
                lines.append(f"- [{title}]({rel_link(page)})")
            lines.append("")

    lines.append(TOC_END)
    return "\n".join(lines)


def splice_toc(readme: str, new_toc: str) -> str:
    """Replace the existing TOC region in README with new_toc.

    The README must contain both TOC_START and TOC_END markers, in order.
    """
    if TOC_START not in readme or TOC_END not in readme:
        raise SystemExit(
            f"README.md is missing TOC markers ({TOC_START} / {TOC_END}). "
            "Add the markers around the section you want auto-generated."
        )
    start = readme.index(TOC_START)
    end = readme.index(TOC_END) + len(TOC_END)
    return readme[:start] + new_toc + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if README.md is out of sync with the generated TOC.",
    )
    args = parser.parse_args()

    readme = README.read_text(encoding="utf-8")
    new_readme = splice_toc(readme, build_toc())

    if args.check:
        if readme != new_readme:
            print("README.md TOC is out of date. Run `scripts/build_toc.py`.", file=sys.stderr)
            return 1
        return 0

    if readme != new_readme:
        README.write_text(new_readme, encoding="utf-8")
        print(f"Updated {README.relative_to(REPO_ROOT)}")
    else:
        print("README.md TOC already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
