# Scripts

Stdlib-only Python — no venv, no dependencies. Run any of these from the repo root as `python3 scripts/<name>.py ...`.

## Creating pages

| Script | Purpose |
|---|---|
| `new_chapter.py` | New chapter under `topics/<topic>/`, from `templates/chapter-template.md`. Auto-tagged with the topic slug. |
| `new_lab.py` | New lab under `labs/<lab-dir>/`, from `templates/lab-template.md`. Auto-tagged with the lab-dir slug. |
| `new_project.py` | New project under `projects/<slug>/`, from `templates/project-template.md`. |
| `new_interview_page.py` | New question page under `topics/mock-interviews/questions/`, from `templates/interview-question-template.md`. |

All four accept `--tags tag1,tag2` for extra tags beyond the automatic default.

## Regenerating derived content

| Script | Rebuilds |
|---|---|
| `generate_toc.py` | Every directory listing (root README + every topic/lab/prompt/project index), with ⬜/🟡/✅ status indicators |
| `generate_breadcrumbs.py` | The breadcrumb trail on every content page |
| `generate_cross_references.py` | The "Related" section on every content page, from shared tags |
| `generate_tags_index.py` | `TAGS.md` |
| `update_progress.py` | `PROGRESS.md` and each topic's "chapters complete" line |
| `build.py` | **Runs all of the above in the right order, then `check_links.py`.** This is the one command to run after touching any page. |

All are idempotent — safe to run repeatedly, they only write a file if its content actually changed.

## Tracking progress

| Script | Purpose |
|---|---|
| `mark_complete.py <path> [--status ...]` | Set a page's completion status (default `complete`); automatically refreshes `PROGRESS.md` afterward |
| `log_study.py <topic> <hours> [--notes ...]` | Append a session to the Study Log in `STUDY_PLAN.md` |

## Validation

| Script | Purpose |
|---|---|
| `check_links.py` | Fails (exit 1) if any relative markdown link points to a file that doesn't exist. Skips code spans/blocks. |
| `ensure_frontmatter.py` | Backfills the metadata/breadcrumb/related blocks on any content page that's missing them (new pages already have them; this is a safety net for hand-created pages or future template changes) |

## Shared

`_lib.py` — not a script, importing it does nothing on its own. Holds the metadata read/write functions, the marker-injection helper (`inject()`), the canonical topic taxonomy (`CATEGORIES`), and page-discovery helpers used by everything above.

## Typical workflow

```bash
python3 scripts/new_chapter.py spark shuffle-internals --title "Shuffle Internals"
# ... fill in the sections ...
python3 scripts/mark_complete.py topics/spark/02-shuffle-internals.md
python3 scripts/build.py
```
