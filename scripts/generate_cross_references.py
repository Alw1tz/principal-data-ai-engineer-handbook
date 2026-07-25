#!/usr/bin/env python3
"""Regenerate the "Related" section at the bottom of every content page,
between `<!-- RELATED:START -->` / `<!-- RELATED:END -->` markers.

A page is "related" to another if they share at least one tag. Ranked by
number of shared tags (most first), capped at 5 so this stays useful as the
tag graph grows dense — a wall of 40 links isn't cross-referencing, it's
noise.

Usage:
    python3 scripts/generate_cross_references.py
"""
import os

from _lib import ROOT, all_content_pages, inject, parse_metadata, title_from_file

START = "<!-- RELATED:START -->"
END = "<!-- RELATED:END -->"
MAX_RELATED = 5


def link(from_dir, target_path, text) -> str:
    rel = os.path.relpath(target_path, start=from_dir)
    return f"[{text}]({rel})"


def main() -> None:
    pages = all_content_pages()
    tagged = {page: set(parse_metadata(page)["tags"]) for page in pages}

    changed = []
    for page in pages:
        my_tags = tagged[page]
        scored = []
        if my_tags:
            for other in pages:
                if other == page:
                    continue
                shared = my_tags & tagged[other]
                if shared:
                    scored.append((len(shared), title_from_file(other), other, shared))

        scored.sort(key=lambda t: (-t[0], t[1]))
        top = scored[:MAX_RELATED]

        if not top:
            body = "_No related pages yet — add shared tags to connect this page to others._"
        else:
            lines = []
            for _, title, other, shared in top:
                tag_str = ", ".join(sorted(shared))
                lines.append(f"- {link(page.parent, other, title)} _({tag_str})_")
            body = "\n".join(lines)

        if inject(page, START, END, body):
            changed.append(str(page.relative_to(ROOT)))

    if changed:
        print("Regenerated Related section in:")
        for c in changed:
            print(f"  {c}")
    else:
        print("All Related sections already up to date.")


if __name__ == "__main__":
    main()
