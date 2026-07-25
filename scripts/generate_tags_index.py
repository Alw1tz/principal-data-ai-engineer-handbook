#!/usr/bin/env python3
"""Regenerate TAGS.md — every tag in use, with links to every page carrying
it, between `<!-- TOC:START -->` / `<!-- TOC:END -->` markers.

Usage:
    python3 scripts/generate_tags_index.py
"""
import os
from collections import defaultdict

from _lib import ROOT, all_content_pages, inject, parse_metadata, title_from_file

START = "<!-- TOC:START -->"
END = "<!-- TOC:END -->"


def link(from_dir, target_path, text) -> str:
    rel = os.path.relpath(target_path, start=from_dir)
    return f"[{text}]({rel})"


def main() -> None:
    by_tag = defaultdict(list)
    for page in all_content_pages():
        tags = parse_metadata(page)["tags"]
        for tag in tags:
            by_tag[tag].append(page)

    if not by_tag:
        body = "_No tags yet._"
    else:
        lines = []
        for tag in sorted(by_tag):
            pages = sorted(by_tag[tag], key=title_from_file)
            lines.append(f"### {tag} ({len(pages)})")
            lines.append("")
            for page in pages:
                lines.append(f"- {link(ROOT, page, title_from_file(page))}")
            lines.append("")
        body = "\n".join(lines).rstrip()

    target = ROOT / "TAGS.md"
    if inject(target, START, END, body):
        print("TAGS.md regenerated.")
    else:
        print("TAGS.md already up to date.")


if __name__ == "__main__":
    main()
