#!/usr/bin/env python3
"""Regenerate every auto-generated table-of-contents block in the repo.

Every README.md that has a `<!-- TOC:START -->` / `<!-- TOC:END -->` marker
pair gets its listing rebuilt from what's actually on disk:

  - README.md (root)                        -> one level: topics/projects/prompts/labs
  - projects/README.md                       -> project subdirectories
  - topics/<topic>/README.md                 -> that topic's numbered chapters
  - topics/mock-interviews/questions/README.md -> numbered interview-question pages
  - labs/<lab-dir>/README.md                 -> that lab dir's numbered labs
  - prompts/<prompt-dir>/README.md           -> that dir's free-form prompt files

This is the single source of truth for "what pages exist" — never hand-edit
a listing between these markers, it will be overwritten.

Usage:
    python3 scripts/generate_toc.py
"""
from pathlib import Path

from _lib import ROOT

START = "<!-- TOC:START -->"
END = "<!-- TOC:END -->"


def inject(path: Path, body: str) -> bool:
    content = path.read_text()
    if START not in content or END not in content:
        raise SystemExit(f"{path.relative_to(ROOT)} is missing {START}/{END} markers")
    before, rest = content.split(START, 1)
    _, after = rest.split(END, 1)
    new_content = f"{before}{START}\n{body}\n{END}{after}"
    if new_content == content:
        return False
    path.write_text(new_content)
    return True


def title_from_file(md_path: Path) -> str:
    for line in md_path.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem.replace("-", " ").title()


def title_from_readme(dir_path: Path) -> str:
    readme = dir_path / "README.md"
    return title_from_file(readme) if readme.exists() else dir_path.name.replace("-", " ").title()


def numbered_pages_list(dir_path: Path, empty_msg: str) -> str:
    pages = sorted(dir_path.glob("[0-9][0-9]-*.md"))
    if not pages:
        return f"_{empty_msg}_"
    return "\n".join(f"- [{title_from_file(p)}]({p.name})" for p in pages)


def free_form_pages_list(dir_path: Path) -> str:
    pages = sorted(p for p in dir_path.glob("*.md") if p.name != "README.md")
    if not pages:
        return "_No prompts yet._"
    return "\n".join(f"- [{title_from_file(p)}]({p.name})" for p in pages)


def subdirs_list(dir_path: Path) -> str:
    subs = sorted(p for p in dir_path.iterdir() if p.is_dir())
    if not subs:
        return "_Nothing yet._"
    return "\n".join(f"- [{title_from_readme(sub)}]({sub.name}/README.md)" for sub in subs)


def root_toc() -> str:
    lines = []
    for section in ["topics", "projects", "prompts", "labs"]:
        section_dir = ROOT / section
        if not section_dir.is_dir():
            continue
        lines.append(f"- **[{section.title()}]({section}/README.md)**")
        for sub in sorted(p for p in section_dir.iterdir() if p.is_dir()):
            lines.append(f"  - [{title_from_readme(sub)}]({section}/{sub.name}/README.md)")
    return "\n".join(lines)


def main() -> None:
    changed = []

    def maybe(path: Path, body: str) -> None:
        if path.exists() and inject(path, body):
            changed.append(str(path.relative_to(ROOT)))

    maybe(ROOT / "README.md", root_toc())
    maybe(ROOT / "projects" / "README.md", subdirs_list(ROOT / "projects"))

    for topic_dir in sorted((ROOT / "topics").iterdir()):
        if topic_dir.is_dir():
            maybe(topic_dir / "README.md", numbered_pages_list(topic_dir, "No chapters yet"))

    questions_dir = ROOT / "topics" / "mock-interviews" / "questions"
    maybe(questions_dir / "README.md", numbered_pages_list(questions_dir, "No questions yet"))

    for lab_dir in sorted((ROOT / "labs").iterdir()):
        if lab_dir.is_dir():
            maybe(lab_dir / "README.md", numbered_pages_list(lab_dir, "No labs yet"))

    for prompt_dir in sorted((ROOT / "prompts").iterdir()):
        if prompt_dir.is_dir():
            maybe(prompt_dir / "README.md", free_form_pages_list(prompt_dir))

    if changed:
        print("Regenerated TOC in:")
        for c in changed:
            print(f"  {c}")
    else:
        print("All TOCs already up to date.")


if __name__ == "__main__":
    main()
