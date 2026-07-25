# Topics

One directory per subject. Every chapter inside follows [`../templates/chapter-template.md`](../templates/chapter-template.md) — identical sections everywhere.

Grouped below by the same 6 categories used in [ROADMAP.md](../ROADMAP.md) and [PROGRESS.md](../PROGRESS.md) — those three files intentionally share one taxonomy, so a topic's category means the same thing everywhere in this repo.

## Foundations

- [Python](python/README.md)
- [SQL](sql/README.md)
- [Data Modeling](data-modeling/README.md)
- [Distributed Systems](distributed-systems/README.md)

## Data Engineering

- [Spark](spark/README.md)
- [Airflow](airflow/README.md)
- [Kafka](kafka/README.md)
- [dbt](dbt/README.md)
- [Snowflake](snowflake/README.md)
- [Lakehouse](lakehouse/README.md)
- [Data Governance](data-governance/README.md)

## Cloud & Platform

- [AWS](aws/README.md)
- [Kubernetes](kubernetes/README.md)
- [Terraform](terraform/README.md)
- [Security](security/README.md)
- [Observability](observability/README.md)

## AI Engineering

- [AI Engineering](ai-engineering/README.md)
- [LLMs](llms/README.md)
- [RAG](rag/README.md)
- [Vector Databases](vector-databases/README.md)
- [Knowledge Graphs](knowledge-graphs/README.md)
- [MCP](mcp/README.md)
- [LangGraph](langgraph/README.md)

## Systems & Leadership

- [System Design](system-design/README.md)
- [Leadership](leadership/README.md)
- [Production Projects](production-projects/README.md)

## Interview & Career

- [Research Papers](research-papers/README.md)
- [Mock Interviews](mock-interviews/README.md)
- [Salesforce Interview Preparation](salesforce-interview-preparation/README.md)

Add a new topic by creating `topics/<slug>/README.md` (copy an existing one, and add it to the category above that matches ROADMAP.md/PROGRESS.md) plus a first chapter:

```bash
python3 scripts/new_chapter.py <slug> introduction --title "<Title> - Introduction"
```
