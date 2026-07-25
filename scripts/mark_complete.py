#!/usr/bin/env python3
"""Mark a page's chapter-completion status, then refresh PROGRESS.md and
every topic README's progress line automatically.

Usage:
    python3 scripts/mark_complete.py <path> [--status not-started|in-progress|complete]

Defaults to --status complete. Path is relative to the repo root or absolute.

Example:
    python3 scripts/mark_complete.py topics/spark/01-introduction.md
    python3 scripts/mark_complete.py topics/spark/02-shuffle-internals.md --status in-progress
"""
import argparse
import subprocess
import sys
from pathlib import Path

from _lib import ROOT, STATUSES, has_metadata, set_metadata_field, today


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Page to update, e.g. topics/spark/01-introduction.md")
    parser.add_argument("--status", choices=STATUSES, default="complete")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        sys.exit(f"No such file: {path}")
    if not has_metadata(path):
        sys.exit(f"{path.relative_to(ROOT)} has no metadata block — run scripts/ensure_frontmatter.py first")

    set_metadata_field(path, "status", args.status)
    set_metadata_field(path, "updated", today())
    print(f"{path.relative_to(ROOT)} -> status: {args.status}")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "update_progress.py")], check=True)


if __name__ == "__main__":
    main()
