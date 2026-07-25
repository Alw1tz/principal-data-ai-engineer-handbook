#!/usr/bin/env python3
"""Regenerate the table of contents in README.md from the current directory tree.

Scans topics/, projects/, prompts/, labs/ and writes a nested list of links
between the `<!-- TOC:START -->` / `<!-- TOC:END -->` markers in README.md.
Run this after adding/removing chapters, labs, or projects.

Usage:
    python3 scripts/generate_toc.py
"""
from pathlib import Path

from _lib import ROOT

SECTIONS = ["topics", "projects", "prompts", "labs"]
START = "<!-- TOC:START -->"
END = "<!-- TOC:END -->"


def title_from_readme(dir_path: Path) -> str:
    readme = dir_path / "README.md"
    if readme.exists():
        for line in readme.read_text().splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return dir_path.name.replace("-", " ").title()


def build_toc() -> str:
    lines = []
    for section in SECTIONS:
        section_dir = ROOT / section
        if not section_dir.is_dir():
            continue
        lines.append(f"- **[{section.title()}]({section}/README.md)**")
        for sub in sorted(p for p in section_dir.iterdir() if p.is_dir()):
            title = title_from_readme(sub)
            lines.append(f"  - [{title}]({section}/{sub.name}/README.md)")
    return "\n".join(lines)


def main() -> None:
    readme_path = ROOT / "README.md"
    content = readme_path.read_text()
    if START not in content or END not in content:
        raise SystemExit(f"README.md is missing {START}/{END} markers")

    before, rest = content.split(START, 1)
    _, after = rest.split(END, 1)
    new_content = f"{before}{START}\n{build_toc()}\n{END}{after}"

    if new_content == content:
        print("TOC already up to date.")
        return

    readme_path.write_text(new_content)
    print("TOC regenerated in README.md")


if __name__ == "__main__":
    main()
