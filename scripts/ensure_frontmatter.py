#!/usr/bin/env python3
"""Backfill the metadata block, breadcrumb markers, and related-section
markers on any content page that predates this tooling (or was hand-created
without them). Safe to run repeatedly — every step is a no-op if already
present.

Default tag: the page's parent directory slug (same rule new_*.py scripts
use), so old and new pages end up tagged consistently.

Usage:
    python3 scripts/ensure_frontmatter.py
"""
from _lib import ROOT, all_content_pages, has_metadata, metadata_block

BREADCRUMB_BLOCK = "<!-- BREADCRUMB:START -->\n<!-- BREADCRUMB:END -->\n"
RELATED_BLOCK = "<!-- RELATED:START -->\n<!-- RELATED:END -->\n"


def default_tag_for(page) -> str:
    parts = page.relative_to(ROOT).parts
    # topics/mock-interviews/questions/01-x.md -> "mock-interviews", not "questions"
    if parts[0] == "topics" and len(parts) > 3 and parts[2] == "questions":
        return parts[1]
    return parts[1]  # topics/<slug>/..., labs/<slug>/..., projects/<slug>/...


def main() -> None:
    touched = []

    for page in all_content_pages():
        text = page.read_text()
        original = text

        if not has_metadata(page):
            text = metadata_block([default_tag_for(page)]) + "\n" + text

        if "<!-- BREADCRUMB:START -->" not in text:
            # Insert right before the first H1 heading.
            lines = text.splitlines(keepends=True)
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    lines.insert(i, BREADCRUMB_BLOCK + "\n")
                    break
            text = "".join(lines)

        if "<!-- RELATED:START -->" not in text:
            text = text.rstrip("\n") + "\n\n# Related\n\n" + RELATED_BLOCK
        else:
            # Older pages may have the markers without a heading above them.
            lines = text.splitlines()
            idx = next(i for i, line in enumerate(lines) if "<!-- RELATED:START -->" in line)
            preceding = next((l for l in reversed(lines[:idx]) if l.strip()), "")
            if not preceding.startswith("#"):
                lines.insert(idx, "")
                lines.insert(idx, "# Related")
                text = "\n".join(lines) + "\n"

        if text != original:
            page.write_text(text)
            touched.append(str(page.relative_to(ROOT)))

    if touched:
        print("Backfilled:")
        for t in touched:
            print(f"  {t}")
        print("\nRun scripts/build.py to populate the new markers.")
    else:
        print("All content pages already have metadata/breadcrumb/related markers.")


if __name__ == "__main__":
    main()
