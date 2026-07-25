#!/usr/bin/env python3
"""Create a new chapter under topics/<topic>/ from templates/chapter-template.md.

Auto-tagged with the topic slug; pass --tags for extra cross-cutting tags.
Run scripts/build.py afterward to wire in breadcrumbs/TOC/cross-refs.

Usage:
    python3 scripts/new_chapter.py <topic-slug> <chapter-slug> [--title "Chapter Title"] [--tags tag1,tag2]

Example:
    python3 scripts/new_chapter.py spark shuffle-internals --title "Shuffle Internals" --tags performance
"""
import argparse
import sys

from _lib import ROOT, write_new_page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", help="Topic directory slug under topics/, e.g. 'spark'")
    parser.add_argument("chapter_slug", help="Slug for the new chapter, e.g. 'shuffle-internals'")
    parser.add_argument("--title", help="Chapter title (defaults to a title-cased slug)")
    parser.add_argument("--tags", default="", help="Comma-separated extra tags, beyond the topic slug")
    args = parser.parse_args()

    topic_dir = ROOT / "topics" / args.topic
    if not topic_dir.exists():
        sys.exit(f"No such topic: topics/{args.topic}/ (create the directory first)")

    title = args.title or args.chapter_slug.replace("-", " ").title()
    tags = [args.topic] + [t.strip() for t in args.tags.split(",") if t.strip()]
    target = write_new_page(
        topic_dir, args.chapter_slug, ROOT / "templates" / "chapter-template.md", title, tags
    )
    print(f"Created {target.relative_to(ROOT)}")
    print("Run: python3 scripts/build.py   (to wire in breadcrumbs, TOC, cross-refs, tags index)")


if __name__ == "__main__":
    main()
