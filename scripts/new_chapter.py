#!/usr/bin/env python3
"""Create a new chapter under topics/<topic>/ from templates/chapter-template.md.

Usage:
    python3 scripts/new_chapter.py <topic-slug> <chapter-slug> [--title "Chapter Title"]

Example:
    python3 scripts/new_chapter.py spark shuffle-internals --title "Shuffle Internals"
"""
import argparse
import sys

from _lib import ROOT, write_new_page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", help="Topic directory slug under topics/, e.g. 'spark'")
    parser.add_argument("chapter_slug", help="Slug for the new chapter, e.g. 'shuffle-internals'")
    parser.add_argument("--title", help="Chapter title (defaults to a title-cased slug)")
    args = parser.parse_args()

    topic_dir = ROOT / "topics" / args.topic
    if not topic_dir.exists():
        sys.exit(f"No such topic: topics/{args.topic}/ (create the directory first)")

    title = args.title or args.chapter_slug.replace("-", " ").title()
    target = write_new_page(
        topic_dir, args.chapter_slug, ROOT / "templates" / "chapter-template.md", title
    )
    print(f"Created {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
