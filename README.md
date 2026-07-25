# Principal Data & AI Engineer Handbook

A long-term, continuously growing engineering handbook — Data Engineering, AI Engineering, distributed systems, platform/infra, and career growth toward a Principal-level role. Structured like production documentation (Stripe/AWS/Google-style): every topic follows the same template, so once you know the shape of one chapter you know all of them.

This is not a notes dump. Every chapter in `topics/` is meant to eventually answer, for its subject: how it works internally, how it's run in production, what breaks, what a senior engineer knows that a mid-level one doesn't, and what a principal engineer knows that a senior one doesn't.

## How it's organized

```
topics/      One directory per subject (Spark, AWS, LLMs, System Design, Leadership, ...).
             Each chapter follows templates/chapter-template.md — identical sections
             everywhere, so navigation and depth are predictable.

projects/    Design-doc placeholders for larger production-style builds
             (Metadata Platform, Streaming Platform, MCP Server, ...). A project
             that gets built for real gets its own repo under ~/Documents/dev/,
             linked back from its page here.

prompts/     Reusable prompts — Claude, ChatGPT, interview prep, architecture,
             coding, system design — one .md file per prompt.

labs/        Standalone, runnable hands-on exercises (separate from the
             narrative chapters), grouped by tool.

templates/   The canonical templates (chapter, lab, project, interview
             question) that everything else is generated from.

scripts/     Automation: scaffold new chapters/labs/projects/interview pages,
             regenerate every directory's table of contents, check for
             broken relative links. See scripts/README.md for the full list.

assets/      Images, diagrams, architecture exports, mermaid sources, PDFs.
```

## Root documents

- [ROADMAP.md](ROADMAP.md) — phased plan of what gets written, in what order
- [STUDY_PLAN.md](STUDY_PLAN.md) — weekly study cadence
- [PROGRESS.md](PROGRESS.md) — per-topic completion tracker
- [BOOKS.md](BOOKS.md) — reading list
- [PAPERS.md](PAPERS.md) — research papers queue
- [RESOURCES.md](RESOURCES.md) — curated external links
- [PROJECTS.md](PROJECTS.md) — status tracker for everything in `projects/`
- [INTERVIEW_TRACKER.md](INTERVIEW_TRACKER.md) — interview prep tracker (incl. Salesforce)
- [TAGS.md](TAGS.md) — every tag in use, with links to every page carrying it
- [CHANGELOG.md](CHANGELOG.md) — notable structural/tooling changes
- [CONTRIBUTING.md](CONTRIBUTING.md) — conventions for adding new content

## Documentation system

Every content page (chapter, lab, project, interview question) carries three HTML-comment metadata lines (`tags`, `status`, `updated`) — invisible when rendered on GitHub, machine-readable by everything below. That one mechanism drives:

- **Tags & cross-references** — pages sharing a tag auto-link each other in a "Related" section. New pages are auto-tagged with their parent topic/lab slug; add more with `--tags`. Full tag index: [TAGS.md](TAGS.md).
- **Breadcrumbs** — `Home / Topics / Spark / Shuffle Internals`, computed from the page's actual location, not hand-maintained.
- **Chapter completion / reading progress** — `status` is `not-started` / `in-progress` / `complete`. Every directory listing shows it as ⬜/🟡/✅, [PROGRESS.md](PROGRESS.md) rolls it up per topic ("3/6 chapters complete"), and each topic's own README shows the same line.
- **Automatic tables of contents** — every index page (root, topic, lab, prompt, project) lists its actual current contents, rebuilt from disk.

Nothing here is hand-maintained — running `python3 scripts/build.py` after any change regenerates all of it and fails loudly (via `check_links.py`) if something's broken.

## Adding content

```bash
# new chapter under an existing topic (auto-tagged with the topic slug)
python3 scripts/new_chapter.py spark shuffle-internals --title "Shuffle Internals"

# new hands-on lab
python3 scripts/new_lab.py snowflake time-travel-recovery --title "Time Travel Recovery"

# new interview-question page
python3 scripts/new_interview_page.py design-a-rate-limiter --title "Design a Rate Limiter"

# new project placeholder
python3 scripts/new_project.py real-time-feature-store --title "Real-Time Feature Store"

# ... fill in the sections, then:
python3 scripts/mark_complete.py topics/spark/02-shuffle-internals.md

# log a study session
python3 scripts/log_study.py spark 2.5 --notes "Read chapter 1, did the AWS lab"

# after touching any page — rebuilds TOC, breadcrumbs, cross-refs, tags index,
# progress, and validates links, all in one command:
python3 scripts/build.py
```

All scripts are stdlib-only Python — no venv or dependencies needed. Full reference: [scripts/README.md](scripts/README.md).

## Table of Contents

<!-- TOC:START -->
- **[Topics](topics/README.md)**
  - [AI Engineering](topics/ai-engineering/README.md)
  - [Airflow](topics/airflow/README.md)
  - [AWS](topics/aws/README.md)
  - [Data Governance](topics/data-governance/README.md)
  - [Data Modeling](topics/data-modeling/README.md)
  - [dbt](topics/dbt/README.md)
  - [Distributed Systems](topics/distributed-systems/README.md)
  - [Kafka](topics/kafka/README.md)
  - [Knowledge Graphs](topics/knowledge-graphs/README.md)
  - [Kubernetes](topics/kubernetes/README.md)
  - [Lakehouse](topics/lakehouse/README.md)
  - [LangGraph](topics/langgraph/README.md)
  - [Leadership](topics/leadership/README.md)
  - [LLMs](topics/llms/README.md)
  - [MCP](topics/mcp/README.md)
  - [Mock Interviews](topics/mock-interviews/README.md)
  - [Observability](topics/observability/README.md)
  - [Production Projects](topics/production-projects/README.md)
  - [Python](topics/python/README.md)
  - [RAG](topics/rag/README.md)
  - [Research Papers](topics/research-papers/README.md)
  - [Salesforce Interview Preparation](topics/salesforce-interview-preparation/README.md)
  - [Security](topics/security/README.md)
  - [Snowflake](topics/snowflake/README.md)
  - [Spark](topics/spark/README.md)
  - [SQL](topics/sql/README.md)
  - [System Design](topics/system-design/README.md)
  - [Terraform](topics/terraform/README.md)
  - [Vector Databases](topics/vector-databases/README.md)
- **[Projects](projects/README.md)**
  - [Agentic Data Platform](projects/agentic-data-platform/README.md)
  - [AI SQL Assistant](projects/ai-sql-assistant/README.md)
  - [Data Catalog](projects/data-catalog/README.md)
  - [Data Lineage Platform](projects/data-lineage-platform/README.md)
  - [Data Quality Platform](projects/data-quality-platform/README.md)
  - [Knowledge Graph](projects/knowledge-graph/README.md)
  - [MCP Server](projects/mcp-server/README.md)
  - [Metadata Platform](projects/metadata-platform/README.md)
  - [Streaming Platform](projects/streaming-platform/README.md)
- **[Prompts](prompts/README.md)**
  - [Architecture Prompts](prompts/architecture-prompts/README.md)
  - [ChatGPT Prompts](prompts/chatgpt-prompts/README.md)
  - [Claude Prompts](prompts/claude-prompts/README.md)
  - [Coding Prompts](prompts/coding-prompts/README.md)
  - [Interview Prompts](prompts/interview-prompts/README.md)
  - [System Design Prompts](prompts/system-design-prompts/README.md)
- **[Labs](labs/README.md)**
  - [AI Labs](labs/ai/README.md)
  - [Airflow Labs](labs/airflow/README.md)
  - [AWS Labs](labs/aws/README.md)
  - [dbt Labs](labs/dbt/README.md)
  - [Kafka Labs](labs/kafka/README.md)
  - [Python Labs](labs/python/README.md)
  - [Snowflake Labs](labs/snowflake/README.md)
  - [Spark Labs](labs/spark/README.md)
<!-- TOC:END -->
