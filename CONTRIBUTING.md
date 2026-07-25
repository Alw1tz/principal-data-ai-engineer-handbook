# Contributing

This is a personal handbook, but it's kept to the same bar as a shared team doc — mainly so future-you can trust it.

## Adding a chapter

Never hand-create a chapter file — use the script so numbering and the section template stay consistent:

```bash
python3 scripts/new_chapter.py <topic> <chapter-slug> --title "Chapter Title"
```

If the topic doesn't exist yet, add it to `topics/` with a `README.md` (see any existing topic for the pattern) before scaffolding chapters into it.

## Filling in a chapter

- Don't skip sections — if one genuinely doesn't apply, write one line saying why instead of deleting the heading. Consistency across chapters is the entire value of the template.
- **Senior Engineer Notes** vs **Principal Engineer Notes**: the first is "what you need to know to do the job well," the second is "what you need to know to make the call when the textbook answer doesn't fit" — tradeoffs, org-level consequences, when to break the rule.
- **AWS Lab** / **Snowflake Lab**: link out to `labs/aws/` or `labs/snowflake/` rather than inlining a full lab here — keep the chapter narrative, the lab hands-on.

## Adding a lab

```bash
python3 scripts/new_lab.py <lab-dir> <lab-slug> --title "Lab Title"
```

A lab should be completable end-to-end by following its **Steps** section alone — no missing context assumed from the parent chapter.

## Adding a project

```bash
python3 scripts/new_project.py <slug> --title "Project Title"
```

Then add a status row for it in [`PROJECTS.md`](PROJECTS.md) — that file can't be auto-generated since status is a judgment call, not a filesystem fact.

## Adding an interview question

```bash
python3 scripts/new_interview_page.py <slug> --title "Question Title"
```

Goes into `topics/mock-interviews/questions/`, not directly into `topics/mock-interviews/` — that directory's top level is for narrative chapters (chapter-template) only, so the two page types never collide in the same numbered namespace.

## Before committing

```bash
python3 scripts/generate_toc.py     # if you added/removed topics, projects, prompts, or labs
python3 scripts/check_links.py      # catch broken relative links
```

## Style

- Google developer documentation style: second person, active voice, short sentences, no filler ("simply", "just", "obviously").
- Headers exactly as defined in `templates/chapter-template.md` — same casing, same order.
- One topic per PR/commit where practical — makes `PROGRESS.md` updates traceable to a single change.
