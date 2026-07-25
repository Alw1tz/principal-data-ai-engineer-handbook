#!/usr/bin/env python3
"""Regenerate the breadcrumb trail on every content page (chapters, labs,
projects, interview questions) between their `<!-- BREADCRUMB:START -->` /
`<!-- BREADCRUMB:END -->` markers.

Scoped to content pages, not navigational index README.md files — an index
page's own chapter listing + intro text already covers "how did I get here."

Usage:
    python3 scripts/generate_breadcrumbs.py
"""
import os

from _lib import ROOT, all_content_pages, inject, title_from_file

START = "<!-- BREADCRUMB:START -->"
END = "<!-- BREADCRUMB:END -->"


def link(from_dir, target_path, text) -> str:
    rel = os.path.relpath(target_path, start=from_dir)
    return f"[{text}]({rel})"


def breadcrumb_for(page) -> str:
    rel_parts = page.relative_to(ROOT).parts
    dir_parts = rel_parts[:-1]  # directory chain, e.g. ("topics", "spark")
    is_index = page.name == "README.md"

    crumbs = [link(page.parent, ROOT / "README.md", "Home")]

    # Directory segments, except the last one when the page itself *is*
    # that directory's README.md (that segment becomes the final label).
    dir_count = len(dir_parts) - 1 if is_index else len(dir_parts)
    for i in range(dir_count):
        dir_path = ROOT.joinpath(*dir_parts[: i + 1])
        title = title_from_file(dir_path / "README.md") if (dir_path / "README.md").exists() else dir_parts[i].replace("-", " ").title()
        crumbs.append(link(page.parent, dir_path / "README.md", title))

    crumbs.append(title_from_file(page))  # current page, not a link
    return " / ".join(crumbs)


def main() -> None:
    changed = []
    for page in all_content_pages():
        if inject(page, START, END, breadcrumb_for(page)):
            changed.append(str(page.relative_to(ROOT)))

    if changed:
        print("Regenerated breadcrumbs in:")
        for c in changed:
            print(f"  {c}")
    else:
        print("All breadcrumbs already up to date.")


if __name__ == "__main__":
    main()
