#!/usr/bin/env python3
"""Verify that relative markdown links across the repo point to real files.

Skips external links (http/https/mailto) and in-page anchors (#foo).
Exits non-zero if any broken link is found — safe to wire into a pre-commit
hook or CI.

Usage:
    python3 scripts/check_links.py
"""
import re
import sys
from pathlib import Path

from _lib import ROOT

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def is_external_or_anchor(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "#"))


def main() -> None:
    broken = []
    md_files = sorted(ROOT.rglob("*.md"))

    for md_file in md_files:
        text = md_file.read_text(errors="ignore")
        for match in LINK_RE.finditer(text):
            link = match.group(1).split("#", 1)[0]  # strip in-file anchor
            if not link or is_external_or_anchor(match.group(1)):
                continue
            target = (md_file.parent / link).resolve()
            if not target.exists():
                broken.append((md_file.relative_to(ROOT), match.group(1)))

    if broken:
        print(f"Found {len(broken)} broken link(s):\n")
        for source, link in broken:
            print(f"  {source} -> {link}")
        sys.exit(1)

    print(f"Checked {len(md_files)} markdown files — no broken relative links.")


if __name__ == "__main__":
    main()
