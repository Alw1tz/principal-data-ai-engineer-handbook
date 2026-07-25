#!/usr/bin/env python3
"""Create a new interview-question page under topics/mock-interviews/questions/,
from templates/interview-question-template.md.

Kept in its own `questions/` subdirectory, separate from the narrative
chapters that live directly under topics/mock-interviews/ — two different
page shapes (chapter-template vs. interview-question-template) should never
share a flat numbered namespace.

Usage:
    python3 scripts/new_interview_page.py <slug> [--title "Question Title"] [--tags tag1,tag2]

Example:
    python3 scripts/new_interview_page.py design-a-rate-limiter --title "Design a Rate Limiter" --tags system-design
"""
import argparse

from _lib import ROOT, write_new_page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Slug for the new interview page")
    parser.add_argument("--title", help="Page title (defaults to a title-cased slug)")
    parser.add_argument("--tags", default="", help="Comma-separated extra tags")
    args = parser.parse_args()

    target_dir = ROOT / "topics" / "mock-interviews" / "questions"
    title = args.title or args.slug.replace("-", " ").title()
    tags = ["mock-interviews"] + [t.strip() for t in args.tags.split(",") if t.strip()]
    target = write_new_page(
        target_dir, args.slug, ROOT / "templates" / "interview-question-template.md", title, tags
    )
    print(f"Created {target.relative_to(ROOT)}")
    print("Run: python3 scripts/build.py   (to wire in breadcrumbs, TOC, cross-refs, tags index)")


if __name__ == "__main__":
    main()
