#!/usr/bin/env python3
"""Regenerate everything derived from the filesystem/metadata, in the right
order, then validate. Run this after adding/editing any page — it's the
one command that leaves the whole repo internally consistent.

Order matters: frontmatter must exist before breadcrumbs/cross-refs/tags/
progress can read it; check_links runs last as a final validation gate.

Usage:
    python3 scripts/build.py
"""
import subprocess
import sys

from _lib import ROOT

STEPS = [
    "ensure_frontmatter.py",
    "generate_breadcrumbs.py",
    "generate_toc.py",
    "generate_cross_references.py",
    "generate_tags_index.py",
    "update_progress.py",
    "check_links.py",
]


def main() -> None:
    for step in STEPS:
        print(f"\n== {step} ==")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / step)])
        if result.returncode != 0:
            sys.exit(f"\nbuild.py stopped: {step} exited {result.returncode}")

    print("\nBuild complete — repo is internally consistent.")


if __name__ == "__main__":
    main()
