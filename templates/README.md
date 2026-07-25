# Templates

The four canonical page shapes. Everything under `topics/`, `labs/`, `projects/`, and interview-question pages is generated from one of these — never hand-write a new page's structure from scratch.

| Template | Used by | Target |
|---|---|---|
| `chapter-template.md` | `scripts/new_chapter.py` | `topics/<topic>/<NN>-<slug>.md` |
| `lab-template.md` | `scripts/new_lab.py` | `labs/<lab-dir>/<NN>-<slug>.md` |
| `project-template.md` | `scripts/new_project.py` | `projects/<slug>/README.md` |
| `interview-question-template.md` | `scripts/new_interview_page.py` | `topics/mock-interviews/questions/<NN>-<slug>.md` |

## Convention: templates render verbatim

`scripts/_lib.py`'s `render_template()` substitutes `{{TITLE}}` and `{{METADATA}}` — everything else in a template file is copied byte-for-byte into the generated page. **Don't put editorial comments, instructions, or HTML comment blocks inside these files** — they will show up in every generated page. Explain conventions (like this one) in this README or in [`../CONTRIBUTING.md`](../CONTRIBUTING.md) instead.

Every section header gets a single `_TODO_` placeholder line under it, so a freshly generated page and an unfilled existing page look identical.

## Every content page has three infrastructure blocks

All four templates share this shape, in order:

1. **Metadata** — `{{METADATA}}` expands to three HTML comment lines (`tags`, `status`, `updated`), invisible on GitHub. This is the source of truth for tagging, chapter-completion tracking, and cross-references. See [`../scripts/README.md`](../scripts/README.md) for the full mechanism.
2. **Breadcrumb** — `<!-- BREADCRUMB:START -->`/`<!-- BREADCRUMB:END -->`, right before the `# {{TITLE}}` heading. Left empty at creation time; `scripts/generate_breadcrumbs.py` computes and fills it in based on the page's actual file path.
3. **Related** — `<!-- RELATED:START -->`/`<!-- RELATED:END -->`, appended after the last section. Populated by `scripts/generate_cross_references.py` from shared tags. Deliberately placed *after* the fixed section list rather than inserted into it — the point of the fixed template is that every chapter has the exact same sections in the exact same order; a metadata/navigation feature shouldn't perturb that.

All three are filled in by `scripts/build.py` (never by hand) — run it after creating or editing any page.

## Changing a template

Editing one of these files only affects **future** pages generated from it — it does not retroactively update already-generated pages. If you change the section list, decide explicitly whether to backfill existing pages (and say so in the commit message) or leave them as a mixed generation.
