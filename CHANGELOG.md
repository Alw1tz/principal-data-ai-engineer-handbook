# Changelog

Notable changes to the handbook's structure/tooling (not content — chapters have no content yet). Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## 2026-07-25 — VS Code workspace

A complete, opinionated editor setup — open the repo root in VS Code and everything below is already wired up, no manual configuration.

### Added

- **`.vscode/extensions.json`** — recommended extensions: markdownlint, Prettier, Code Spell Checker, Mermaid + GitHub-style preview, Markdown All in One + emoji, PlantUML, Ruff (Python), YAML, GitHub Actions, GitLens. `unwantedRecommendations` explicitly excludes Markdown Preview Enhanced (see rationale below).
- **`.vscode/tasks.json`** — every `scripts/*.py` as a task with input prompts (topic slug, title, tags, ...) instead of typing full CLI commands. Default build task (Cmd/Ctrl+Shift+B) runs `scripts/build.py` — the same command CI runs.
- **`.vscode/launch.json`** — debug configs for the scripts (breakpoints, step-through), including one bound to `${relativeFile}` so debugging `mark_complete.py` against whatever chapter is open needs no setup.
- **`.vscode/handbook.code-snippets`** — Mermaid flowchart/sequence, PlantUML component diagram (with an inline reminder that GitHub won't render it inline), the metadata/breadcrumb/related marker blocks, GitHub-flavored collapsible `<details>` and `[!NOTE]`/`[!WARNING]`/`[!TIP]` callouts, a table skeleton.
- **`.markdownlint.jsonc`** — GitHub-style markdown linting, tuned to this repo's actual conventions rather than generic defaults: `MD025`/`MD041` disabled (every template section is deliberately its own H1, and pages open with an HTML-comment metadata block, not the title), `MD033` allows exactly the HTML this repo uses (`details`/`summary`/`div`/`br`/`img`), `MD013` (line length) and `MD034` (bare URLs) off to match the "don't wrap, paste references quickly" writing style already in place.
- **`cspell.json`** — spell-check word list covering every topic slug plus AWS/Kubernetes/AI-engineering vocabulary and this repo's own tooling names, so writing about real infrastructure doesn't mean fighting red squiggles on every second word.
- **`.prettierrc.json`** / **`.prettierignore`** — Prettier handles `.json`/`.yaml`; Markdown is explicitly excluded (see below).
- **`assets/plantuml/`** — source location for `.puml` files, documented in `assets/README.md` alongside the existing `mermaid/` convention.
- **`.vscode/README.md`** — explains all of the above, including the two decisions worth understanding before fighting them (next section).

### Design decisions worth recording

- **Prettier never touches Markdown.** Every `.md` page in this repo is partly owned by `scripts/build.py` (TOC/breadcrumb/tags/cross-reference/progress/stats blocks between HTML-comment markers), and CI fails if `build.py`'s output doesn't exactly match what's committed. Auto-reformatting Markdown on save risks Prettier's output disagreeing with what the Python scripts emit — turning an editor convenience into a source of false CI failures. `.prettierignore` excludes `*.md`, `settings.json` disables `editor.formatOnSave` for the `markdown` language specifically; Markdown style is enforced by `markdownlint` instead, which reads structure without rewriting files.
- **`markdown.validate.enabled` (VS Code's built-in link checker) is turned on explicitly.** It's a free, zero-extension complement to `scripts/check_links.py` — the difference being it flags a broken relative link live, in the editor, while `check_links.py` only catches it when you run `build.py` or push. Same guarantee, faster feedback loop.
- **Markdown Preview Enhanced was considered and rejected** in favor of `bierner.markdown-preview-github-styles` + `bierner.markdown-mermaid`. MPE has its own preview pane with its own styling; the Bierner extensions instead make VS Code's *built-in* preview (Ctrl+Shift+V) match GitHub's actual rendering — since this repo is explicitly designed to be read on GitHub, what you see while writing should be what a reader sees.
- **PlantUML uses the public PlantUML server**, not a local Java/Graphviz install — zero setup cost to preview a diagram. The real tradeoff, documented in both `.vscode/README.md` and `assets/README.md`: unlike Mermaid, GitHub does not render PlantUML inline in Markdown, so finished diagrams need exporting to PNG/SVG.

## 2026-07-24 — Production-ready polish

Everything below is backed by something real running, not decoration — every badge, diagram, and template change ties to an actual file/workflow that exists in this commit.

### Added

- **`LICENSE`** (MIT) — was missing entirely; a public repo with no license technically reserves all rights, which isn't the intent here.
- **`.github/workflows/ci.yml`** — GitHub Actions CI: runs `scripts/build.py` on every push/PR (regenerates all derived content, validates links), then fails the build if that produced any uncommitted diff. This means it's no longer possible to merge a stale TOC, a broken link, or a page that's out of sync with its own tags/breadcrumbs — the badge in the README reports this truthfully because it's wired to a real check.
- **`.github/ISSUE_TEMPLATE/`** (content suggestion, tooling bug) and **`.github/PULL_REQUEST_TEMPLATE.md`** — scoped to what this repo actually is (a personal handbook taking outside suggestions), not a generic open-source community kit that would overstate what it is.
- **`.editorconfig`** — consistent indentation/line-ending rules across the Python scripts and markdown content.
- **`scripts/generate_readme_stats.py`** — real, computed counts (topics/pages/completion-%/tags/etc.) injected into the README, wired into `scripts/build.py`. Not hand-typed numbers that go stale.
- **Mermaid architecture diagram** in the README — the actual `build.py` pipeline (`ensure_frontmatter → breadcrumbs → toc → cross-refs → tags → progress → stats → check_links`), not a generic/decorative system diagram. GitHub renders Mermaid natively, no extra tooling needed.

### Changed

- **README** — badges (CI status, license, tooling, docs style — each backed by a real file/workflow, not aspirational), a directory table with one icon per top-level folder, and the giant flat table of contents moved inside a collapsible `<details>` block so the page doesn't read as a wall of links before you've even seen what the project is.
- **Fixed a real template bug**: `templates/*.md`'s auto-generated "Related" section (added last session) had no heading above it — the cross-reference links just floated after the Checklist section's `_TODO_` with no label. Added `# Related` (`# Related Pages` for interview questions, to avoid clashing with the existing manual "Related Chapters" section there). Backfilled onto all 38 existing pages via an extended `ensure_frontmatter.py`, which now also detects and fixes missing headings above existing marker blocks — not just missing blocks entirely.
- **Fixed a tagging inconsistency**: `new_project.py` was auto-tagging every new project with a generic shared `"projects"` tag, while the 9 pre-existing projects (backfilled last session) each got their own slug as the tag. A shared tag would have cross-referenced every project against every other one regardless of actual relevance. `new_project.py` now tags with the project's own slug, matching how topics/labs already worked.
- **`ROADMAP.md`** already lost its redundant status checkboxes last session; this pass didn't touch that further — mentioned here only because it's part of why `PROGRESS.md` could be trusted as the single source for the new stats line.

### Explicitly not added (and why)

- **No coverage/build-artifact badges** — there's no code being compiled or tested in the traditional sense; a badge implying otherwise would be decorative, not real.
- **No CODE_OF_CONDUCT.md / community-scale contribution process** — this is a personal handbook accepting suggestions, not a project soliciting a contributor base; a full open-source governance kit would misrepresent what it is.
- **No in-page section TOC, no markdown linter** — both already considered and rejected last session (GitHub's native per-file outline covers the first; a JS-based linter would break the stdlib-only-Python tooling constraint for the second).

## 2026-07-24 — Professional documentation system

Converted the handbook from "well-organized markdown" into a documentation system with real machine-readable structure. Everything below is driven by one new mechanism: three HTML-comment metadata lines (`tags`, `status`, `updated`) at the top of every content page — invisible on GitHub, read/written by scripts.

### Added

- **Tagging** — every chapter/lab/project/interview-question page carries `<!-- tags: ... -->`. New pages auto-tag with their parent topic/lab slug; `--tags` adds more. [`TAGS.md`](TAGS.md) (new) indexes every tag with links to every page carrying it, generated by `scripts/generate_tags_index.py`.
- **Cross-references** — `scripts/generate_cross_references.py` builds a "Related" section on every content page from shared tags (ranked by number of shared tags, capped at 5 to stay useful as the tag graph grows). Deliberately appended after the fixed section list rather than inserted into it, so the "every chapter has identical sections" invariant from the previous pass stays intact.
- **Breadcrumbs** — `scripts/generate_breadcrumbs.py` computes `Home / Topics / Spark / Shuffle Internals` from each page's actual file path and injects it right below the metadata block. Scoped to content pages; index README.md files already have adequate navigation via their chapter listings.
- **Chapter completion / reading progress** — `status` (`not-started` / `in-progress` / `complete`) plus `python3 scripts/mark_complete.py <path>`, which flips it and cascades a `PROGRESS.md` + topic-README refresh automatically. Every directory listing now shows ⬜/🟡/✅ inline (`generate_toc.py`), and each topic's own README shows a "Progress: X/N chapters complete" line — reading progress is visible exactly where you're browsing, not just in a root tracker.
- **Study tracking** — `scripts/log_study.py <topic> <hours> [--notes ...]` appends a session row to a new "Study Log" section in `STUDY_PLAN.md`. Separate from the existing weekly-plan table (forward-looking) — this is a session-grained, append-only log (backward-looking).
- **`scripts/ensure_frontmatter.py`** — backfills metadata/breadcrumb/related blocks on any page that predates this system (used once, for migration; kept as an ongoing safety net for hand-created pages).
- **`scripts/build.py`** — orchestrates all of the above (`ensure_frontmatter` → `generate_breadcrumbs` → `generate_toc` → `generate_cross_references` → `generate_tags_index` → `update_progress` → `check_links`) in the one order that actually works, and stops on the first failure. This is now *the* command to run after touching any page.

### Changed

- **`PROGRESS.md`** — was a hand-maintained table defaulting every row to `not-started` forever (nothing updated it automatically). Now fully computed from chapter status, grouped by the same 6-category taxonomy as `topics/README.md`/`ROADMAP.md`, with a chapters-complete fraction per topic instead of a single word.
- **`ROADMAP.md`** — dropped the per-topic checkboxes. They were a second, hand-maintained "is this done" signal that could disagree with the real one; `PROGRESS.md` is now the only source of truth for completion, `ROADMAP.md` stays purely a phase-ordering/planning document.
- **`generate_toc.py`** — directory listings now show a status emoji per entry; also de-duplicated its `inject()`/`title_from_file()` helpers into `_lib.py` (they'd been copy-pasted when this script was first written, before `_lib.py` had a generic marker-injection helper).
- **All 4 `new_*.py` generators** — now write the metadata block and auto-tag new pages; `README.md`, `CONTRIBUTING.md`, `templates/README.md`, `scripts/README.md` updated to describe the new workflow end to end.

### Design decisions worth recording

- **HTML comments over YAML frontmatter** for metadata — this repo is read directly on GitHub with no static-site-generator build step, and GitHub renders literal `---` frontmatter blocks as visible text (it doesn't strip them the way Jekyll/MkDocs would). HTML comments are invisible on GitHub while remaining just as machine-parseable.
- **No in-page section table-of-contents** — every chapter already has the exact same 22 sections in the exact same order (the whole point of the template), so a "Contents" list repeating those 22 headings on every single page would be pure boilerplate. GitHub's own markdown renderer already provides a native per-page outline/jump-to-heading control, making a hand-built one redundant on the platform this repo is actually read on.
- **Backfilled all 38 pre-existing pages** (29 chapters + 9 project READMEs) with the new metadata/breadcrumb/related blocks via `ensure_frontmatter.py`, rather than leaving them as a second, older page shape — the whole point of the earlier "reduce duplication / template drift" pass was one canonical page shape, and silently exempting the first 38 pages from a new structural requirement would have reintroduced exactly that problem.

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
