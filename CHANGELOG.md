# Changelog

Notable changes to the handbook's structure/tooling (not content — chapters have no content yet). Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## 2026-07-12 — Staff-level structural review

A full review of the initial scaffold for inconsistencies, duplication, naming, navigation, and scalability. Findings and fixes below, grouped by what a reader/contributor actually experiences.

### Fixed — templates didn't match what they were supposed to produce

- **`templates/*.md` leaked editorial comments into generated pages.** Each template had an HTML comment block at the top explaining the template's purpose — harmless in the template file itself, but `scripts/_lib.py`'s renderer copies templates byte-for-byte (only substituting `{{TITLE}}`), so every chapter/lab/project/interview page generated going forward would have had that comment baked into its content. Removed the comments from all four templates; that guidance now lives in `templates/README.md` and `CONTRIBUTING.md` instead.
- **Templates were missing the `_TODO_` placeholder** that the already-scaffolded pages (e.g. `topics/spark/01-introduction.md`) use under every heading. Two different code paths (the one-off initial scaffold script vs. the checked-in `templates/` + `scripts/new_*.py`) had silently drifted apart — a chapter generated today would have looked structurally different from one of the original 29. Templates now match the established format exactly; `templates/` is documented as the single source of truth going forward.

### Fixed — two documents disagreed on how topics are categorized

`topics/README.md` grouped the 29 topics into 4 categories; `ROADMAP.md` grouped the same 29 topics into 6 phases — and the groupings didn't agree (e.g. AWS was "Data Engineering Core" in one, "Cloud & Platform" in the other; System Design was "Platform & Systems" in one, "Systems & Leadership" in the other). Picked ROADMAP.md's 6-category taxonomy as canonical (Foundations / Data Engineering / Cloud & Platform / AI Engineering / Systems & Leadership / Interview & Career) and made `topics/README.md` and `PROGRESS.md` use the identical grouping and order. All three files now say the same thing about where a topic belongs.

### Fixed — per-directory chapter/lab/prompt listings couldn't scale

Every `topics/<topic>/README.md` hardcoded a single line — `- [01 - Introduction](01-introduction.md)` — with no mechanism to update it. Add a second chapter and the index silently goes stale forever. Same gap existed for `labs/<dir>/README.md` (no listing at all) and `prompts/<dir>/README.md` (no listing at all). Given the repo's stated end-state is "hundreds of documents," a manually-maintained index was never going to hold up.

Fixed by extending `scripts/generate_toc.py` from "regenerates the root README's TOC" to "regenerates every `<!-- TOC:START -->`/`<!-- TOC:END -->` block in the repo" — every topic README, every lab-directory README, every prompt-directory README, and `projects/README.md` now list their actual contents, rebuilt from the filesystem. Added the marker pair to all of those files. This is the single biggest scalability fix in this pass: the listing is now a build artifact, not something anyone has to remember to hand-edit.

### Fixed — interview-question pages collided with topic chapters

`scripts/new_interview_page.py` wrote into `topics/mock-interviews/` using the same `NN-slug.md` numbering as ordinary chapters (which use `chapter-template.md`, 22 sections) — but interview-question pages use a completely different template (`interview-question-template.md`, 8 sections). A file named `topics/mock-interviews/05-something.md` gave no indication which shape it was. Moved interview-question generation to `topics/mock-interviews/questions/`, a dedicated subdirectory with its own README/TOC — the narrative chapters and the individual Q&A pages no longer share a namespace.

### Fixed — real bug in `check_links.py`

The link checker didn't skip fenced code blocks or inline code spans, so an example markdown-link snippet shown as documentation inside an inline code span in `assets/README.md` was flagged as a broken link. Now strips code spans/blocks before scanning for links.

### Fixed — acronym casing

`topics/ai-engineering/README.md`, `topics/langgraph/README.md`, and `prompts/chatgpt-prompts/README.md` had auto-titlecased headers ("Ai Engineering", "Langgraph", "Chatgpt Prompts") because the slug-to-title logic used a plain `.title()` call without a lookup table for domain acronyms. Fixed to "AI Engineering", "LangGraph", "ChatGPT Prompts" — and because `scripts/generate_toc.py` reads each page's actual H1 (not a hardcoded string) when building the root README's TOC, this was a real, propagating inconsistency, not just a cosmetic typo in one place.

### Fixed — inconsistent naming

`salesforce-interview-prep` was the only abbreviated slug in the entire `topics/` tree (everything else — `distributed-systems`, `knowledge-graphs`, `vector-databases`, `mock-interviews` — spells the full word). Renamed to `salesforce-interview-preparation` and updated all references (`topics/README.md`, `INTERVIEW_TRACKER.md`, the topic's own README).

### Reduced duplication

- **`PROJECTS.md` vs. `projects/README.md`**: both hand-maintained the same list of 9 projects. `projects/README.md`'s listing is now auto-generated (via the `generate_toc.py` extension above) and its intro text now explicitly explains the split: `projects/README.md` = "what exists" (derived from the filesystem), `PROJECTS.md` = "what state is it in" (a judgment call that can't be derived, so it stays manual). Same content is no longer maintained by hand in two places.
- **Chapter-generation logic**: previously lived in two independent places (a one-off scaffold script and the checked-in `templates/` + `scripts/_lib.py`) that had already drifted apart (see the templates fix above). `templates/README.md` now states explicitly that `templates/*.md` is the only source of truth.

### Added

- `scripts/new_project.py` — projects/ had a template (`project-template.md`) but no generator script, unlike chapters/labs/interview-questions. Closed the gap for consistency.
- `templates/README.md` — which template maps to which script/target, and the "templates render verbatim, keep them clean" convention.
- `scripts/README.md` — one-table reference for all 6 scripts.
- `assets/README.md` — what each subfolder (`images/`, `diagrams/`, `architecture/`, `mermaid/`, `pdfs/`) is for. Every other top-level directory already had a README; these two didn't.
- `topics/mock-interviews/questions/README.md` — index for the new subdirectory.

### Changed

- `README.md`, `CONTRIBUTING.md` — updated to mention `new_project.py` and the extended `generate_toc.py` behavior.
