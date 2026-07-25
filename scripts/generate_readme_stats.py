#!/usr/bin/env python3
"""Regenerate the stats line in README.md between `<!-- STATS:START -->` /
`<!-- STATS:END -->` — real counts from the filesystem + metadata, not
hand-typed numbers that go stale.

Usage:
    python3 scripts/generate_readme_stats.py
"""
from _lib import ROOT, all_content_pages, inject, parse_metadata

START = "<!-- STATS:START -->"
END = "<!-- STATS:END -->"


def main() -> None:
    topics = [p for p in (ROOT / "topics").iterdir() if p.is_dir()]
    labs = [p for p in (ROOT / "labs").iterdir() if p.is_dir()]
    projects = [p for p in (ROOT / "projects").iterdir() if p.is_dir()]
    prompts = sum(
        len([f for f in d.glob("*.md") if f.name != "README.md"])
        for d in (ROOT / "prompts").iterdir() if d.is_dir()
    )

    pages = all_content_pages()
    statuses = [parse_metadata(p)["status"] for p in pages]
    complete = statuses.count("complete")
    tags = {t for p in pages for t in parse_metadata(p)["tags"]}

    pct = round(100 * complete / len(pages)) if pages else 0

    body = (
        f"**{len(topics)}** topics · **{len(pages)}** pages · **{complete}/{len(pages)}** "
        f"complete ({pct}%) · **{len(labs)}** lab categories · **{len(projects)}** projects · "
        f"**{prompts}** prompts · **{len(tags)}** tags"
    )

    if inject(ROOT / "README.md", START, END, body):
        print("README stats updated.")
    else:
        print("README stats already up to date.")


if __name__ == "__main__":
    main()
