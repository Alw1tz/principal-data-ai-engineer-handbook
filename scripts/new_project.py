#!/usr/bin/env python3
"""Create a new project placeholder under projects/<slug>/, from
templates/project-template.md.

Usage:
    python3 scripts/new_project.py <slug> [--title "Project Title"] [--tags tag1,tag2]

Example:
    python3 scripts/new_project.py real-time-feature-store --title "Real-Time Feature Store" --tags spark,streaming

After running this: add a status row for the project in PROJECTS.md, and run
scripts/build.py to wire in breadcrumbs/TOC/cross-refs.
"""
import argparse

from _lib import ROOT, render_template, slugify


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Slug for the new project")
    parser.add_argument("--title", help="Project title (defaults to a title-cased slug)")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    args = parser.parse_args()

    slug = slugify(args.slug)
    target_dir = ROOT / "projects" / slug
    target = target_dir / "README.md"
    if target.exists():
        raise SystemExit(f"{target} already exists")

    title = args.title or args.slug.replace("-", " ").title()
    # Tag with the project's own slug (matches how topics/labs default-tag) —
    # a shared generic "projects" tag would cross-reference every project
    # against every other one regardless of whether they're actually related.
    tags = [slug] + [t.strip() for t in args.tags.split(",") if t.strip()]
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(render_template(ROOT / "templates" / "project-template.md", title, tags))
    print(f"Created {target.relative_to(ROOT)}")
    print("Don't forget to: add a status row for it in PROJECTS.md, then run scripts/build.py")


if __name__ == "__main__":
    main()
