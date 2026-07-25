# Templates

The four canonical page shapes. Everything under `topics/`, `labs/`, `projects/`, and interview-question pages is generated from one of these — never hand-write a new page's structure from scratch.

| Template | Used by | Target |
|---|---|---|
| `chapter-template.md` | `scripts/new_chapter.py` | `topics/<topic>/<NN>-<slug>.md` |
| `lab-template.md` | `scripts/new_lab.py` | `labs/<lab-dir>/<NN>-<slug>.md` |
| `project-template.md` | `scripts/new_project.py` | `projects/<slug>/README.md` |
| `interview-question-template.md` | `scripts/new_interview_page.py` | `topics/mock-interviews/questions/<NN>-<slug>.md` |

## Convention: templates render verbatim

`scripts/_lib.py`'s `render_template()` only ever substitutes `{{TITLE}}` — everything else in a template file is copied byte-for-byte into the generated page. **Don't put editorial comments, instructions, or HTML comment blocks inside these files** — they will show up in every generated page. Explain conventions (like this one) in this README or in [`../CONTRIBUTING.md`](../CONTRIBUTING.md) instead.

Every section header gets a single `_TODO_` placeholder line under it, so a freshly generated page and an unfilled existing page look identical — that consistency is what `scripts/check_links.py`-style tooling (and future automation, e.g. "find all sections still marked _TODO_") depends on.

## Changing a template

Editing one of these files only affects **future** pages generated from it — it does not retroactively update already-generated pages. If you change the section list, decide explicitly whether to backfill existing pages (and say so in the commit message) or leave them as a mixed generation.
