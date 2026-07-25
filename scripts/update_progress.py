#!/usr/bin/env python3
"""Recompute chapter-completion stats from every page's `status` metadata and
write them into:

  - PROGRESS.md (grouped table, between `<!-- TOC:START -->`/`<!-- TOC:END -->`)
  - each topics/<topic>/README.md (a "Progress: X/N chapters complete" line,
    between `<!-- PROGRESS:START -->`/`<!-- PROGRESS:END -->`)

This is the reading-progress / chapter-completion tracker — status itself is
set by hand (via scripts/mark_complete.py, or editing the `<!-- status: -->`
line directly); this script only aggregates what's already there.

Usage:
    python3 scripts/update_progress.py
"""
from _lib import ROOT, CATEGORIES, STATUS_EMOJI, inject, parse_metadata

PROGRESS_START = "<!-- PROGRESS:START -->"
PROGRESS_END = "<!-- PROGRESS:END -->"
TABLE_START = "<!-- TOC:START -->"
TABLE_END = "<!-- TOC:END -->"


def topic_stats(slug: str) -> dict:
    topic_dir = ROOT / "topics" / slug
    chapters = sorted(topic_dir.glob("[0-9][0-9]-*.md")) if topic_dir.is_dir() else []
    statuses = [parse_metadata(c)["status"] for c in chapters]
    updated_dates = [parse_metadata(c)["updated"] for c in chapters if parse_metadata(c)["updated"]]

    total = len(chapters)
    complete = statuses.count("complete")
    in_progress = statuses.count("in-progress")

    if total == 0:
        overall = "not-started"
    elif complete == total:
        overall = "complete"
    elif complete > 0 or in_progress > 0:
        overall = "in-progress"
    else:
        overall = "not-started"

    return {
        "total": total,
        "complete": complete,
        "overall": overall,
        "last_updated": max(updated_dates) if updated_dates else "",
    }


def main() -> None:
    changed = []

    table_lines = []
    for category, slugs in CATEGORIES.items():
        table_lines.append(f"### {category}")
        table_lines.append("")
        table_lines.append("| Topic | Chapters | Status | Last Updated |")
        table_lines.append("|---|---|---|---|")
        for slug in slugs:
            stats = topic_stats(slug)
            title = slug.replace("-", " ").title()
            readme = ROOT / "topics" / slug / "README.md"
            if readme.exists():
                for line in readme.read_text().splitlines():
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
            link = f"[{title}](topics/{slug}/README.md)"
            emoji = STATUS_EMOJI[stats["overall"]]
            table_lines.append(
                f"| {link} | {stats['complete']}/{stats['total']} | {emoji} {stats['overall']} | {stats['last_updated']} |"
            )
        table_lines.append("")

    if inject(ROOT / "PROGRESS.md", TABLE_START, TABLE_END, "\n".join(table_lines).rstrip()):
        changed.append("PROGRESS.md")

    for slugs in CATEGORIES.values():
        for slug in slugs:
            readme = ROOT / "topics" / slug / "README.md"
            if not readme.exists():
                continue
            stats = topic_stats(slug)
            body = f"**Progress: {stats['complete']}/{stats['total']} chapters complete** {STATUS_EMOJI[stats['overall']]}"
            if inject(readme, PROGRESS_START, PROGRESS_END, body):
                changed.append(str(readme.relative_to(ROOT)))

    if changed:
        print("Updated progress in:")
        for c in changed:
            print(f"  {c}")
    else:
        print("Progress already up to date.")


if __name__ == "__main__":
    main()
