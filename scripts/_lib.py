"""Shared helpers for the handbook's scripts. Not a script itself.

Metadata format: three HTML comment lines at the very top of every content
page (chapters, labs, projects, interview questions) — invisible when the
page renders on GitHub, machine-readable by every script here.

    <!-- tags: spark, distributed-systems -->
    <!-- status: not-started -->
    <!-- updated: 2026-07-13 -->

`status` is one of STATUSES. `tags` is a comma-separated list, free-form
beyond that a new page's generator auto-tags it with its parent directory's
slug. `updated` is an ISO date, bumped whenever `status` changes.
"""
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATUSES = ["not-started", "in-progress", "complete"]
STATUS_EMOJI = {"not-started": "⬜", "in-progress": "🟡", "complete": "✅"}

# Canonical topic taxonomy — also reflected as prose in topics/README.md and
# ROADMAP.md. If you change the grouping, update all three in the same commit.
CATEGORIES = {
    "Foundations": ["python", "sql", "data-modeling", "distributed-systems"],
    "Data Engineering": ["spark", "airflow", "kafka", "dbt", "snowflake", "lakehouse", "data-governance"],
    "Cloud & Platform": ["aws", "kubernetes", "terraform", "security", "observability"],
    "AI Engineering": ["ai-engineering", "llms", "rag", "vector-databases", "knowledge-graphs", "mcp", "langgraph"],
    "Systems & Leadership": ["system-design", "leadership", "production-projects"],
    "Interview & Career": ["research-papers", "mock-interviews", "salesforce-interview-preparation"],
}

METADATA_RE = re.compile(r"<!--\s*(tags|status|updated):\s*(.*?)\s*-->")


def today() -> str:
    return date.today().isoformat()


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


# ---- metadata (tags / status / updated) ------------------------------------

def metadata_block(tags: list[str], status: str = "not-started", updated: str | None = None) -> str:
    updated = updated or today()
    tag_str = ", ".join(sorted(set(tags)))
    return (
        f"<!-- tags: {tag_str} -->\n"
        f"<!-- status: {status} -->\n"
        f"<!-- updated: {updated} -->\n"
    )


def parse_metadata(path: Path) -> dict:
    """Read tags/status/updated from a page's leading HTML comments.
    Returns sane defaults for any field not found (page has no metadata yet).
    """
    text = path.read_text()
    found = dict(METADATA_RE.findall(text[:500]))  # metadata is always near the top
    tags = [t.strip() for t in found.get("tags", "").split(",") if t.strip()]
    return {
        "tags": tags,
        "status": found.get("status", "not-started"),
        "updated": found.get("updated", ""),
    }


def has_metadata(path: Path) -> bool:
    return bool(METADATA_RE.search(path.read_text()[:500]))


def set_metadata_field(path: Path, key: str, value: str) -> None:
    """Update a single metadata field in place. Errors if the page has no
    metadata block yet — run ensure_frontmatter.py first."""
    if key not in ("tags", "status", "updated"):
        raise ValueError(f"Unknown metadata key: {key}")
    text = path.read_text()
    pattern = re.compile(rf"<!--\s*{key}:.*?-->")
    if not pattern.search(text):
        raise ValueError(f"{path} has no '{key}' metadata line — run ensure_frontmatter.py")
    new_line = f"<!-- {key}: {value} -->"
    path.write_text(pattern.sub(new_line, text, count=1))


# ---- marker-delimited block injection (TOC, breadcrumbs, related, etc.) ----

def inject(path: Path, start_marker: str, end_marker: str, body: str) -> bool:
    """Replace the content between start_marker/end_marker in path with body.
    Returns True if the file actually changed. Raises if markers are missing."""
    content = path.read_text()
    if start_marker not in content or end_marker not in content:
        raise SystemExit(f"{path.relative_to(ROOT)} is missing {start_marker}/{end_marker}")
    before, rest = content.split(start_marker, 1)
    _, after = rest.split(end_marker, 1)
    new_content = f"{before}{start_marker}\n{body}\n{end_marker}{after}"
    if new_content == content:
        return False
    path.write_text(new_content)
    return True


# ---- page templates ----------------------------------------------------

def render_template(template_path: Path, title: str, tags: list[str], status: str = "not-started") -> str:
    content = template_path.read_text()
    content = content.replace("{{TITLE}}", title)
    content = content.replace("{{METADATA}}", metadata_block(tags, status).rstrip("\n"))
    return content


def write_new_page(
    dir_path: Path, slug: str, template_path: Path, title: str, tags: list[str], numbered: bool = True
) -> Path:
    slug = slugify(slug)
    filename = f"{next_index(dir_path)}-{slug}.md" if numbered else f"{slug}.md"
    target = dir_path / filename
    if target.exists():
        raise FileExistsError(f"{target} already exists")
    target.write_text(render_template(template_path, title, tags))
    return target


# ---- content-page discovery (for cross-refs / tags index / progress) -------

def all_content_pages() -> list[Path]:
    """Every page that carries metadata: topic/lab/interview-question chapters
    (numbered .md files) and project READMEs. Excludes index README.md files
    (topics/<t>/README.md etc.) which are navigation, not content."""
    pages = []
    for topic_dir in (ROOT / "topics").iterdir():
        if not topic_dir.is_dir():
            continue
        pages.extend(sorted(topic_dir.glob("[0-9][0-9]-*.md")))
    questions_dir = ROOT / "topics" / "mock-interviews" / "questions"
    if questions_dir.is_dir():
        pages.extend(sorted(questions_dir.glob("[0-9][0-9]-*.md")))
    for lab_dir in (ROOT / "labs").iterdir():
        if lab_dir.is_dir():
            pages.extend(sorted(lab_dir.glob("[0-9][0-9]-*.md")))
    for project_dir in (ROOT / "projects").iterdir():
        if project_dir.is_dir() and (project_dir / "README.md").exists():
            pages.append(project_dir / "README.md")
    return sorted(set(pages))


def title_from_file(md_path: Path) -> str:
    for line in md_path.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem.replace("-", " ").title()
