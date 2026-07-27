# LangGraph Questions for Lead Agentic Data Systems Engineer

> Answers below are grounded in `labs/ai/agentic-demo/scout_agent_graph.py`
> — a real 3-node `StateGraph` (scout → remediate → review, with a
> conditional edge looping review's REVISE verdict back to remediate)
> running against local `qwen3:30b` via Ollama. See
> `labs/ai/01-mcp-langgraph-scout-agent.md` for the full walkthrough and
> verified output.

## Core LangGraph Concepts

1. **Explain what LangGraph is and how it differs from other agentic frameworks.**

   LangGraph models an agent workflow as an explicit graph — a state
   machine — rather than a single prompt loop or a fixed chain. The
   difference that matters in practice: control flow is a first-class,
   inspectable object (`StateGraph`, nodes, edges) instead of implicit
   in prompt logic, so branching/looping/retrying is code you can read
   and test, not something the LLM has to reliably decide on its own
   every time. My demo's `add_conditional_edges` call is a literal
   if/else in the graph definition — not a hope that the model says the
   right thing.

2. **What are the key components of a LangGraph application (Nodes, Edges, State)?**

   **State**: a typed schema (my `PipelineState` TypedDict — 
   `anomaly_report`, `draft_sql`, `draft_test`, `review_verdict`,
   `review_notes`, `revision_count`) that flows through the whole graph.
   **Nodes**: plain Python functions that take state in and return a
   partial-state dict to merge in (`scout_node`, `remediate_node`,
   `review_node`). **Edges**: the wiring between nodes — either fixed
   (`add_edge("scout", "remediate")`) or conditional
   (`add_conditional_edges("review", route_after_review, {...})`).

3. **Describe how LangGraph handles state management in agent workflows.**

   Each node returns only the keys it changed; LangGraph merges that
   into the running state object rather than requiring nodes to pass the
   full state through. Concretely, `remediate_node` returns
   `{"draft_sql": fix, "draft_test": test}` and the framework merges
   that on top of whatever `scout_node` already set — so nodes stay
   decoupled from each other's concerns.

4. **What are the different ways to define edges between nodes in LangGraph?**

   Fixed edges (`add_edge`) for "always go here next" — my
   `scout → remediate` transition. Conditional edges
   (`add_conditional_edges`) where a router function inspects state and
   returns a string key mapped to the next node — my
   `route_after_review` returns `"approved" | "revise" | "escalate"`,
   mapped to `END`, `"remediate"`, or `END` respectively. There's also
   `set_entry_point`/`END` as the graph's start/terminal markers.

5. **How does LangGraph support conditional logic in agent decision-making?**

   The conditional-edge router is just a Python function over the
   current state — no magic, no requiring the LLM to emit a structured
   "next action" the graph blindly trusts. In my demo,
   `route_after_review` inspects `state["review_verdict"]` (which itself
   came from parsing the reviewer LLM's `VERDICT: APPROVE/REVISE` line)
   and a hard cap (`revision_count >= 2` → escalate) so the loop can't
   run forever even if the model keeps rejecting its own fixes.

## Implementation and Design

6. **How do you approach designing complex agent workflows using LangGraph?**

   Start from the state schema, not the nodes — decide what information
   has to survive across steps first (that's what `PipelineState`
   captures), then write each node as a small, single-responsibility
   function. Keep nodes narrow enough that each one is independently
   testable outside the graph (every node in my demo is just a function
   you can call directly with a hand-built state dict).

7. **Explain how you would structure a multi-step reasoning process using LangGraph.**

   Exactly the scout → remediate → review shape: each step has a
   distinct responsibility and a distinct prompt framing (scout
   summarizes, remediate drafts, review critiques adversarially) rather
   than one node doing everything in one giant prompt. Splitting review
   into its own node with a different persona is what makes the
   self-correction loop possible — a single node can't peer-review its
   own output.

8. **What are the best practices for managing state in large LangGraph applications?**

   Keep state minimal and typed (TypedDict/Pydantic) so it's obvious
   what each node reads and writes; avoid dumping raw LLM output or
   large blobs into state where a summary would do — every field in
   state gets re-serialized into every downstream prompt that touches
   it, so bloated state directly inflates token cost across the whole
   graph, not just one call.

9. **How do you handle error handling and recovery in LangGraph workflows?**

   Two layers: the "expected failure" path is architectural — my
   `review_node` rejecting a draft isn't an error, it's a designed
   `REVISE` branch with a hard cap to prevent infinite loops. The
   "unexpected failure" path (tool exception, malformed LLM output) is
   handled inside the node itself — e.g. my `remediate_node`'s
   `draft.split("TEST:")` would need a guard in production for a
   malformed LLM response that omits the `TEST:` label, rather than
   letting an `IndexError` crash the whole graph run.

10. **Describe your experience with debugging and monitoring LangGraph applications.**

    Printed every node's output as it fired in the demo specifically so
    each transition is visible — that's the same instinct you'd want in
    production, just via LangSmith tracing or structured logs instead of
    stdout: for every state transition you should be able to answer
    "what did this node see, what did it decide, why."

## Integration with Data Systems

11. **How would you integrate LangGraph agents with data sources like Snowflake or databases?**

    Through an MCP tool call inside a node, not a raw DB driver call
    scattered through node logic — my `scout_node` calls
    `run_sql_query` (imported straight from `mcp_warehouse_server.py`)
    to get the anomalous rows before ever calling the LLM. That keeps
    data access consistent whether the caller is this LangGraph graph,
    Claude Code, or any other MCP host.

12. **Explain how you would implement agent memory and context management in LangGraph.**

    Short-term/within-run memory is just state (my `review_notes`
    carried from `review_node` back into `remediate_node` on a revision
    pass — that's the whole self-correction mechanism). Cross-run memory
    would use LangGraph's checkpointer/persistence layer to snapshot
    state to a store between runs, which I didn't need for a single
    linear demo run but would for anything resuming across sessions.

13. **What are the considerations when connecting LangGraph agents to external APIs or services?**

    Same as any tool call from an LLM: validate/sanitize what the model
    sends before it hits a real API (my server enforces SELECT-only
    server-side, not by trusting the prompt), and treat latency as a
    per-node cost that compounds — three sequential LLM calls plus a
    tool call in my demo pipeline is already a multi-second-to-minute
    round trip depending on the model.

14. **How do you approach testing LangGraph workflows and agent behavior?**

    Unit-test nodes as plain functions first (call `remediate_node`
    directly with a hand-built state dict, assert the SQL it returns is
    scoped correctly) before testing the compiled graph end-to-end.
    For the LLM-dependent parts, I'd assert on structure (does the
    output contain a `VERDICT:` line, does the SQL have a WHERE clause)
    rather than exact text, since LLM output isn't deterministic even
    at temperature 0 across model versions.

15. **Describe your experience with deploying LangGraph applications in production environments.**

    Haven't deployed at scale yet — this demo is the honest extent of my
    hands-on LangGraph experience going into this interview. What I can
    speak to concretely: the graph topology is model-agnostic (swapping
    `ChatOllama` for `ChatAnthropic` is a one-line change, same nodes/
    edges), which is exactly the kind of portability you'd want before
    committing to a specific model vendor in production.

## Advanced Patterns

16. **How would you implement a self-improving agent system using LangGraph?**

    My review/revise loop is the minimal version: an agent's output
    gets critiqued and the critique becomes input to a retry, up to a
    bound. "Self-improving" across runs (not just within one) would mean
    persisting which fixes got approved/rejected and feeding that
    history back into future scout/remediate prompts — a memory layer on
    top of this same graph shape, not a different architecture.

17. **Explain how you would create agents that can learn from their interactions and adapt their behavior.**

    Within LangGraph specifically, that's a checkpointed memory feeding
    summarized past outcomes into future prompts — the graph structure
    doesn't "learn," the context you feed each node does. I'd be
    skeptical of anything claiming genuine online learning inside the
    graph itself; more realistically it's retrieval over past
    approved/rejected decisions.

18. **What are the patterns for implementing feedback loops in LangGraph workflows?**

    Exactly my review → remediate conditional edge: a critique-producing
    node, a router that inspects the critique's verdict, and a bounded
    retry count so the loop terminates. The bound
    (`revision_count >= 2` → escalate to a human) is the part people
    skip and shouldn't — an unbounded agent-critiques-agent loop is a
    real cost/availability risk.

19. **How do you handle parallel processing and concurrency in LangGraph applications?**

    Built exactly this — `labs/ai/agentic-demo/stress_test_graph.py`,
    the JD's 10:30 scenario. Two `add_edge(START, ...)` calls (to
    `research` and `simulation`) with no edge between them fan out; both
    feeding into `synthesis` fans back in — LangGraph waits for all of a
    node's predecessors before running it. The part people get wrong:
    defining the edges this way isn't sufficient for real concurrency —
    I had to make both nodes `async def` and wrap their blocking calls
    (`yfinance`'s network request, numpy's Monte Carlo) in
    `asyncio.to_thread`, and run the graph with `await
    app.ainvoke(...)` instead of `.invoke()`. Verified it was real, not
    just topologically parallel: timed each node alone (0.40s +
    0.01s sequential), then in the graph both finished within 0.5s of
    each other — actual overlap, not sequential execution that happens
    to look fine on a diagram. Honest caveat I'd mention if asked: the
    win was real but tiny here (both nodes are cheap; a single LLM call
    in `synthesis` took 80s of the total runtime) — fan-out only pays
    off when the parallelized work is itself expensive, and I'd say that
    directly rather than oversell a demo's numbers.

20. **Describe your approach to scaling LangGraph agents for handling large volumes of data or requests.**

    Keep per-node payloads small (return summaries/aggregates from tool
    calls, not raw table dumps — my `run_sql_query` already returns a
    handful of rows, not the whole table) and treat each graph run as a
    unit of work you can queue/parallelize across many runs, rather than
    trying to make a single graph run handle unbounded data volume
    internally.

## Agentic Systems Context

21. **How would you design an autonomous agent ecosystem using LangGraph for data engineering tasks?**

    One graph per business capability (an anomaly-remediation graph like
    this demo, a separate ingestion-QA graph, etc.), each with its own
    narrow MCP tool access, rather than one mega-graph trying to do
    everything. Cross-capability coordination happens by handing off
    structured state/results between graphs, not by cramming every
    responsibility into one state schema.

22. **What are the key challenges in building production-grade agents with LangGraph?**

    From what I hit even in a toy demo: LLM output isn't perfectly
    structured (I had to defensively split `"TEST:"` out of the
    remediation draft — a real system needs structured output/function-
    calling enforcement, not string splitting), latency compounds across
    sequential LLM calls, and unbounded self-correction loops are a real
    cost risk without a hard cap like my `revision_count`.

23. **Explain how you would ensure reliability and consistency in LangGraph-based agent systems.**

    Structured output validation at node boundaries (don't trust free
    text between nodes if you can enforce a schema instead), bounded
    retries everywhere a loop exists, and — most directly matching the
    JD's "verification protocols" language — a dedicated review/critique
    node with a genuinely different framing than the drafting node, so
    it isn't just the same model rubber-stamping itself.

24. **Describe your experience with implementing context-aware agents that can access and utilize domain knowledge.**

    My `scout_node` grounds its summary in actual queried rows (via the
    MCP tool), not general knowledge — that's the difference between a
    context-aware agent and a chatbot: the LLM call happens *after* the
    real data is already in the prompt, so the model is summarizing
    fact, not guessing.

25. **How do you approach monitoring and maintaining LangGraph agents in a distributed, autonomous system environment?**

    Log state transitions per node (what I did with print statements at
    demo scale — LangSmith tracing at production scale), track loop/
    revision counts as a metric (a spike in agents hitting the
    revision cap is a signal something upstream degraded), and version
    both the graph topology and the prompts inside each node, since
    either one changing changes agent behavior.