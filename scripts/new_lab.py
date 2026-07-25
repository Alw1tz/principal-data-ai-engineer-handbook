#!/usr/bin/env python3
"""Create a new lab under labs/<lab-dir>/ from templates/lab-template.md.

Auto-tagged with the lab-dir slug; pass --tags for extra cross-cutting tags.
Run scripts/build.py afterward to wire in breadcrumbs/TOC/cross-refs.

Usage:
    python3 scripts/new_lab.py <lab-dir> <lab-slug> [--title "Lab Title"] [--tags tag1,tag2]

Example:
    python3 scripts/new_lab.py snowflake time-travel-recovery --title "Time Travel Recovery"
"""
import argparse
import sys

from _lib import ROOT, write_new_page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab_dir", help="Lab directory slug under labs/, e.g. 'snowflake'")
    parser.add_argument("lab_slug", help="Slug for the new lab, e.g. 'time-travel-recovery'")
    parser.add_argument("--title", help="Lab title (defaults to a title-cased slug)")
    parser.add_argument("--tags", default="", help="Comma-separated extra tags, beyond the lab-dir slug")
    args = parser.parse_args()

    target_dir = ROOT / "labs" / args.lab_dir
    if not target_dir.exists():
        sys.exit(f"No such lab directory: labs/{args.lab_dir}/ (create it first)")

    title = args.title or args.lab_slug.replace("-", " ").title()
    tags = [args.lab_dir] + [t.strip() for t in args.tags.split(",") if t.strip()]
    target = write_new_page(
        target_dir, args.lab_slug, ROOT / "templates" / "lab-template.md", title, tags
    )
    print(f"Created {target.relative_to(ROOT)}")
    print("Run: python3 scripts/build.py   (to wire in breadcrumbs, TOC, cross-refs, tags index)")


if __name__ == "__main__":
    main()
