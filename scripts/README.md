# Scripts

Stdlib-only Python — no venv, no dependencies. Run any of these from the repo root as `python3 scripts/<name>.py ...`.

| Script | Purpose |
|---|---|
| `new_chapter.py` | New chapter under `topics/<topic>/`, from `templates/chapter-template.md` |
| `new_lab.py` | New lab under `labs/<lab-dir>/`, from `templates/lab-template.md` |
| `new_project.py` | New project under `projects/<slug>/`, from `templates/project-template.md` |
| `new_interview_page.py` | New question page under `topics/mock-interviews/questions/`, from `templates/interview-question-template.md` |
| `generate_toc.py` | Rebuilds every auto-generated listing (root README + every topic/lab/prompt/project index) from what's actually on disk |
| `check_links.py` | Fails (exit 1) if any relative markdown link points to a file that doesn't exist |
| `_lib.py` | Shared helpers (not a script — importing it does nothing on its own) |

Run `generate_toc.py` after adding or removing any page, and `check_links.py` before committing. Both are safe to run repeatedly — they're idempotent (`generate_toc.py` only writes a file if its content actually changed).
