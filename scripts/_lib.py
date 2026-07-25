"""Shared helpers for the handbook's scaffolding scripts. Not a script itself."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def next_index(dir_path: Path) -> str:
    """Next zero-padded two-digit prefix for a numbered page in dir_path."""
    dir_path.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in dir_path.glob("[0-9][0-9]-*.md")]
    numbers = [int(name[:2]) for name in existing if name[:2].isdigit()]
    return f"{(max(numbers) + 1) if numbers else 1:02d}"


def render_template(template_path: Path, title: str) -> str:
    content = template_path.read_text()
    return content.replace("{{TITLE}}", title)


def write_new_page(dir_path: Path, slug: str, template_path: Path, title: str, numbered: bool = True) -> Path:
    slug = slugify(slug)
    filename = f"{next_index(dir_path)}-{slug}.md" if numbered else f"{slug}.md"
    target = dir_path / filename
    if target.exists():
        raise FileExistsError(f"{target} already exists")
    target.write_text(render_template(template_path, title))
    return target
