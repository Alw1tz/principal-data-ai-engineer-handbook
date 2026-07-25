# Topics

One directory per subject. Every chapter inside follows [`templates/chapter-template.md`](../templates/chapter-template.md) — identical sections everywhere.

See [ROADMAP.md](../ROADMAP.md) for suggested order and [PROGRESS.md](../PROGRESS.md) for current status.

## Data Engineering Core

- [Python](python/README.md)
- [SQL](sql/README.md)
- [Spark](spark/README.md)
- [Snowflake](snowflake/README.md)
- [AWS](aws/README.md)
- [Airflow](airflow/README.md)
- [Kafka](kafka/README.md)
- [dbt](dbt/README.md)
- [Distributed Systems](distributed-systems/README.md)
- [Data Modeling](data-modeling/README.md)
- [Data Governance](data-governance/README.md)
- [Lakehouse](lakehouse/README.md)

## Platform & Systems

- [System Design](system-design/README.md)
- [Kubernetes](kubernetes/README.md)
- [Terraform](terraform/README.md)
- [Security](security/README.md)
- [Observability](observability/README.md)

## AI Engineering

- [AI Engineering](ai-engineering/README.md)
- [LLMs](llms/README.md)
- [MCP](mcp/README.md)
- [LangGraph](langgraph/README.md)
- [RAG](rag/README.md)
- [Knowledge Graphs](knowledge-graphs/README.md)
- [Vector Databases](vector-databases/README.md)

## Leadership & Career

- [Leadership](leadership/README.md)
- [Production Projects](production-projects/README.md)
- [Research Papers](research-papers/README.md)
- [Mock Interviews](mock-interviews/README.md)
- [Salesforce Interview Preparation](salesforce-interview-prep/README.md)

Add a new topic by creating `topics/<slug>/README.md` (copy an existing one) plus a first chapter:

```bash
python3 scripts/new_chapter.py <slug> introduction --title "<Title> - Introduction"
```
