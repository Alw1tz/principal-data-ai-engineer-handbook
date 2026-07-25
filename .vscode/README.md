# VS Code workspace

Open this repo's root folder in VS Code and it's fully configured out of the box — install the recommended extensions when prompted (or `Extensions: Show Recommended Extensions` from the Command Palette) and everything below just works.

## What's here

| File | Purpose |
|---|---|
| `extensions.json` | Recommended extensions (prompted automatically on open) |
| `settings.json` | Editor/markdown/spell-check/formatter config, scoped per language |
| `tasks.json` | Every `scripts/*.py` wired up as a task, with input prompts instead of remembering CLI args |
| `launch.json` | Debug configs for the scripts (breakpoints, step-through) |
| `handbook.code-snippets` | Mermaid/PlantUML/callout/metadata-block snippets |

Related config that lives at the repo root (not `.vscode/`, since these tools look there by convention): `.markdownlint.jsonc`, `cspell.json`, `.prettierrc.json`, `.prettierignore`, `.editorconfig`.

## Tasks (Cmd/Ctrl+Shift+P → "Run Task")

The default build task (**Cmd/Ctrl+Shift+B**) is `python3 scripts/build.py` — same as CI runs. The rest map 1:1 to `scripts/README.md`, with VS Code prompting for the arguments (topic slug, title, tags, ...) instead of you typing a full command line. "Mark current file complete/in-progress" uses `${relativeFile}`, so it acts on whatever chapter you have open.

## Design decision: Prettier does not touch Markdown

This is the one non-obvious choice in this setup, worth understanding before you fight it:

Every `.md` file in this repo is partly generated — `scripts/build.py` owns the TOC, breadcrumb, tags, cross-reference, progress, and stats blocks between their `<!-- MARKER -->` comments, and CI fails if `build.py`'s output doesn't exactly match what's committed. If Prettier reformatted Markdown on save, any drift between Prettier's formatting and what the Python scripts emit would produce exactly the kind of diff CI is designed to catch — turning a docs tool into a source of false CI failures.

So: `.prettierignore` excludes `*.md` entirely, and `settings.json` disables `editor.formatOnSave` for the `markdown` language specifically. Prettier is still installed/recommended and handles `.json`/`.yaml` (config files `build.py` never touches, zero risk). Markdown formatting is instead enforced by `markdownlint` (style) and `scripts/check_links.py` + CI (correctness) — the same tools the rest of this repo's automation already uses.

If you want to run Prettier on a markdown file anyway (e.g. a brand-new page with no generated content yet), that's fine — just do it manually (`Shift+Alt+F` / "Format Document"), then run `python3 scripts/build.py` afterward and check `git diff` before committing.

## Why not Markdown Preview Enhanced

`shd101wyy.markdown-preview-enhanced` is a common alternative that also supports Mermaid/PlantUML — deliberately not recommended here (see `unwantedRecommendations` in `extensions.json`). It renders in its *own* preview pane with its own styling, which would diverge from how this repo is actually read (on GitHub). Instead: `bierner.markdown-preview-github-styles` makes VS Code's **built-in** preview (Ctrl+Shift+V) match GitHub's real rendering, and `bierner.markdown-mermaid` adds Mermaid support to that same built-in preview — so what you see in the editor is what you'll see on GitHub.

## PlantUML

Configured to use the public PlantUML server (`plantuml.render: PlantUMLServer`) — no Java/Graphviz install required, works immediately. The tradeoff: diagrams are rendered by a third-party server, and **GitHub does not render PlantUML inline the way it does Mermaid** — export finished diagrams to `assets/diagrams/` or `assets/architecture/` as PNG/SVG and embed those. See [`../assets/README.md`](../assets/README.md).

## Spell checking

`cspell.json` at the repo root carries the domain word list (every topic slug, AWS/Kubernetes/AI-engineering vocabulary, this repo's own tooling names). If cSpell flags a real technical term that's missing, add it there — not by disabling the checker.
