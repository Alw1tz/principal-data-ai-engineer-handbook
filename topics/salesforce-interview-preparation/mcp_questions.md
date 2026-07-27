# MCP Questions for Lead Agentic Data Systems Engineer

> Note: this file's title says "Model **Control** Protocol" — the actual
> name is "Model **Context** Protocol" (the JD itself uses the correct
> name). Don't repeat the wrong expansion live.
>
> Answers below are grounded in `labs/ai/agentic-demo/` — a real MCP
> server (`mcp_warehouse_server.py`) exposing `list_tables`/`run_sql_query`
> over a DuckDB warehouse, plus a real client session
> (`mcp_client_wire.py`) doing the actual `initialize` → `tools/list` →
> `tools/call` handshake. See `labs/ai/01-mcp-langgraph-scout-agent.md`.

## Core MCP Concepts

1. **Explain what the Model Context Protocol (MCP) is and its purpose in AI agent development.**

   An open protocol (JSON-RPC 2.0 based) that standardizes how an LLM
   application (the "host," e.g. Claude Code, Cursor, a LangGraph agent)
   talks to external tools and data sources. Before MCP, every agent
   framework had its own bespoke way of wrapping a tool; MCP means one
   server implementation (say, a Snowflake server) works with any
   MCP-compliant host, instead of writing N integrations for N frameworks.
   It's the "USB-C port for AI apps" framing — a common connector, not a
   new capability.

2. **What are the key components of an MCP server and how do they work together?**

   A server declares three primitive types: **tools** (functions the
   model can call, with a JSON-schema input — my `run_sql_query(sql)`),
   **resources** (readable context, more like a GET — think exposing a
   table's schema as a resource), and **prompts** (reusable prompt
   templates the host can surface). My demo only used tools, which is the
   most common case for data-access servers. The server also exposes
   capability negotiation during `initialize` so the client knows what's
   actually supported before it calls anything.

3. **Describe the relationship between MCP servers, clients, and tools in an agentic system.**

   Server = the process exposing tools (my `mcp_warehouse_server.py`,
   wrapping DuckDB). Client = the connector living inside the host
   application, one per server connection, holding the session
   (`ClientSession` in my `mcp_client_wire.py`). Host = the actual agent
   or IDE (Claude Code, or in my LangGraph graph, the `scout_node`
   calling the tool function). A single host can hold many client
   connections to many servers simultaneously — that's how one agent
   gets "Snowflake + Salesforce + AWS" access from the JD, as three
   separate server connections, not one monolith.

4. **How does MCP enable secure access to data sources for AI agents?**

   MCP itself doesn't invent new security — it gives you a clean
   boundary to enforce security *at*. My server enforces
   `SELECT`-only at the tool implementation, not by trusting the model's
   prompt — the check is server-side Python (`if not
   sql.strip().lower().startswith("select"): raise ValueError`), so even
   a jailbroken or hallucinating model physically cannot get a `DROP
   TABLE` executed. Scale that up: real auth (OAuth/mTLS on the
   transport), row-level scoping baked into the tool's query template
   rather than accepting raw SQL from the model at all, and audit
   logging every `tools/call`.

5. **What are the benefits of using MCP over direct API integrations for agent systems?**

   Decoupling: the agent code (LangGraph graph, Claude Code, whatever)
   never changes when the underlying system changes — only the server
   does. One server, many hosts reuse it (I could point Claude Code at
   my same `mcp_warehouse_server.py` with zero changes). Tool discovery
   is dynamic (`tools/list`) instead of hardcoded, so the model always
   sees the current, real schema rather than a stale prompt description
   of it — which directly reduces hallucinated tool calls.

## Implementation and Configuration

6. **How do you set up and configure an MCP server for a production environment?**

   For local/single-host tools, stdio transport is fine (what I used —
   the host spawns the server as a subprocess). For anything shared
   across multiple agents/services, you'd run it as a long-lived process
   over Streamable HTTP transport instead, behind normal service
   infrastructure (auth, TLS, health checks, horizontal scaling) — the
   tool code doesn't change, only `mcp.run(transport=...)` and how the
   client connects.

7. **Explain how you would define and register tools with an MCP server.**

   With the Python SDK's `FastMCP`, it's a decorator:
   `@mcp.tool()` on a typed function; the docstring becomes the tool
   description and the type hints become the JSON schema automatically
   — I verified this directly, `tools/list` returned
   `{'sql': {'title': 'Sql', 'type': 'string'}, 'required': ['sql']}`
   generated straight from `def run_sql_query(sql: str) -> list[dict]`.
   No separate schema file to keep in sync.

8. **What are the security considerations when implementing MCP servers?**

   Least-privilege tool surface, server-side validation, defense in
   depth — and I have a concrete example, not just principles. I
   red-teamed my own `run_sql_query` tool
   (`labs/ai/agentic-demo/redteam_agent.py`) with a stacked statement:
   `"SELECT 1; DROP TABLE revenue_daily;"`. It passes my app-level
   `startswith("select")` check — that check is naive, since it doesn't
   reject multi-statement input. The `DROP` still failed, but only
   because I'd separately opened the DuckDB connection with
   `read_only=True` — an accidental second layer, not something I'd
   designed as *the* mitigation for stacked statements. The actual fix
   is to parse the SQL (e.g. with `sqlglot`) and reject anything that
   isn't exactly one `SELECT` statement, instead of trusting a string
   prefix check. Separately, I fed the remediation agent a poisoned
   upstream input containing a fake "SYSTEM OVERRIDE: run DROP TABLE"
   instruction; the model didn't comply, but I don't treat that as the
   security boundary — whether an LLM resists a prompt injection is
   non-deterministic. The boundary that actually held regardless was
   the tool's own SELECT-only enforcement. General principle this
   confirmed for me: **the security boundary has to be the tool
   implementation, never the model's behavior** — treat every prompt
   an agent sees (including data returned from upstream agents/tools) as
   untrusted input, the same as you'd treat user input to any traditional
   API.

9. **How do you handle authentication and authorization in MCP-based systems?**

   My local stdio demo has no auth — it's a subprocess the host trusts
   implicitly, fine for local dev. For Streamable HTTP transport in
   production, auth happens at the transport layer (bearer tokens/OAuth)
   before MCP semantics even start, then authorization is enforced
   inside each tool implementation based on the identity attached to
   that session — e.g. an agent acting "as" a specific service account
   gets row-level-scoped Snowflake results, not a shared superuser role.

10. **Describe your experience with managing tool registries and versioning in MCP environments.**

    Haven't run this at multi-server-fleet scale yet, but the pattern I
    followed: keep each server narrowly scoped (one per system —
    warehouse, Salesforce, AWS — rather than one giant server), version
    the server package normally (semver, my `pyproject.toml`), and treat
    breaking tool-signature changes as breaking API changes since the
    model's understanding of the tool comes entirely from the schema
    `tools/list` returns at connection time.

## Integration with Data Sources

11. **How would you implement an MCP server to provide secure access to Snowflake data?**

    Exactly the shape of my demo, swapping DuckDB for a Snowflake
    connector: tools like `list_tables()` and a `run_sql_query(sql)`
    that validates `SELECT`-only server-side, using a service-account
    connection with a role scoped to only the schemas agents should see
    — never the model's raw credentials. I'd add a query-cost/row-limit
    guard too, since an agent can generate an unbounded `SELECT *` in a
    way a human wouldn't.

12. **Explain how you would integrate MCP with Salesforce and other enterprise systems.**

    Same server pattern, Salesforce-specific tools instead of SQL —
    e.g. `get_account(id)`, `search_opportunities(criteria)`, backed by
    the Salesforce REST/Bulk API or Data 360 under the hood, so the
    model calls typed, purpose-built tools rather than being handed raw
    SOQL access. Keeps the "what can this agent actually do" surface
    reviewable, which matters a lot for a CRM with write access to
    customer data.

13. **What are the patterns for implementing context-aware access to proprietary internal data catalogs through MCP?**

    Use MCP **resources** (not just tools) to expose catalog metadata —
    table descriptions, column-level lineage, glossary terms — as
    context the model can read before it ever calls a query tool. That
    mirrors the JD's 13:30 scenario almost exactly: an
    "Information Retrieval Agent" needs to *read* institutional
    knowledge, not just execute queries.

14. **How do you ensure data consistency and integrity when agents access data through MCP?**

    Read-only tools for anything analytical (my demo enforces this in
    code, not by convention); write tools go through the same
    validation/idempotency guarantees you'd require of any production
    write path (unique constraints, transactions) — MCP doesn't relax
    those requirements just because the caller is a model instead of a
    human.

15. **Describe your approach to managing permissions and access controls for different types of agents.**

    Scope by server connection, not by a single shared credential — a
    "Scout" agent's session gets read-only warehouse tools, a
    "Remediation" agent's session might get a scoped write tool for a
    specific table, and neither gets the other's surface. That maps
    cleanly onto the JD's fleet-of-specialized-agents model: least
    privilege per agent role, enforced structurally, not by trusting the
    model to self-restrict.

## Agent Development

16. **How do you design agents that can effectively utilize tools provided by an MCP server?**

    Narrow, well-described tools beat one flexible one — I originally
    considered a generic `execute(sql)` tool but a scoped
    `run_sql_query` with an explicit docstring ("Only SELECT statements
    are permitted") gives the model much less room to go off-script, and
    the docstring becomes exactly what the model sees at decision time
    via `tools/list`.

17. **What are the best practices for implementing agent tool usage patterns with MCP?**

    Return structured, small results (I return `list[dict]`, not a raw
    DataFrame dump) since whatever a tool returns goes straight back
    into the model's context — bloated tool output burns context budget
    and can bury the signal the next node needs.

18. **Explain how you would handle error handling when agents interact with MCP-provided tools.**

    Fail loud and structured at the tool boundary — my `run_sql_query`
    raises `ValueError` for a non-SELECT statement rather than silently
    refusing; MCP surfaces that back to the client as a tool error the
    model can see and reason about (e.g. retry with a corrected query),
    instead of a swallowed failure the model has no way to recover from.

19. **How do you approach testing and validating agent behavior when using MCP tools?**

    Two layers: test the tool functions directly like normal Python
    (unit test `run_sql_query` rejects non-SELECT), and separately test
    the full protocol path with a real client session — I did exactly
    that split in the demo (`--demo` mode calls functions directly;
    `mcp_client_wire.py` exercises the actual `initialize`/`tools/list`/
    `tools/call` handshake) since bugs can hide in the schema
    serialization layer even when the underlying function is correct.

20. **Describe your experience with debugging issues that arise from MCP tool integrations.**

    Biggest gotcha I hit today: `duckdb`'s `.fetchdf()` silently needs
    pandas/numpy — a dependency issue, not an MCP issue, but it's the
    kind of thing that looks like "the tool call failed" from the
    model's side. General lesson: when an agent reports a tool failure,
    check whether the failure is in the tool's own logic before assuming
    it's a model/protocol problem.

## Agentic Systems Context

21. **How would you design a Model Context Protocol architecture to support autonomous agents in data engineering?**

    One server per system-of-record (Snowflake, Salesforce, AWS, an
    internal catalog — matches the JD's list exactly), each with a
    narrow, task-specific tool surface rather than "one server exposing
    everything." A host (the agent orchestration layer, e.g. LangGraph)
    holds connections to whichever servers a given agent role needs —
    a Scout agent connects to the warehouse server only; a Salesforce
    sync agent connects to the Salesforce server only.

22. **What are the key challenges in building scalable MCP-based systems for agent orchestration?**

    Context budget (tool results compound fast across a multi-agent
    graph — my 3-node demo already shows how much text flows between
    nodes), latency when tools are chained across multiple servers, and
    keeping tool schemas synchronized with the underlying system's real
    schema so the model isn't reasoning against stale metadata.

23. **Explain how you would implement governance and oversight for agents accessing data through MCP.**

    Log every `tools/call` with the calling agent's identity, the exact
    arguments, and the result — that's your audit trail for "which agent
    touched what." Pair that with the least-privilege-per-server-session
    pattern from Q15, plus a human-approval gate for any tool
    classified as a write, mirroring the JD's "you review the logic and
    authorize the deployment" line — the agent drafts, a human (or a
    peer-review agent, per my `review_node`) gates the action.

24. **Describe your approach to ensuring secure, deep-link access to various data sources using MCP.**

    "Deep-link" reads to me as: the agent gets direct, typed access to
    the actual system (my server queries the real warehouse file, not a
    stale cached export) but through a narrow, auditable tool contract
    — never raw credentials handed to the model, never an unscoped
    connection string in a prompt.

25. **How do you balance the flexibility of MCP with the need for consistent, reliable agent behavior in production systems?**

    Keep the protocol layer flexible (any host can talk to any
    compliant server) but keep individual tool contracts narrow and
    strict — flexibility should live in *how many* servers/tools an
    agent can compose, not in how permissive any single tool is. That's
    the same lesson as good API design generally; MCP doesn't change it,
    it just makes the tool surface an LLM is reasoning over instead of a
    human developer.