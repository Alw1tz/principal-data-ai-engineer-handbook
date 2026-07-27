<!-- tags: ai, langgraph, salesforce-interview-preparation -->
<!-- status: complete -->
<!-- updated: 2026-07-26 -->

<!-- BREADCRUMB:START -->
[Home](../../README.md) / [Hands-on Labs](../README.md) / [AI Labs](README.md) / Concurrent Fan-Out/Join Stress Test Agents
<!-- BREADCRUMB:END -->

# Concurrent Fan-Out/Join Stress Test Agents

# Objective

Build the JD's "10:30 – Architectural Orchestration" scenario for real: a
CFO-style request for a market volatility stress test, handled by a
**Research Agent** (real external market data, no API key needed) and a
**Simulation Agent** (Monte Carlo) running genuinely concurrently, joined
by a **Synthesis Agent** that writes the executive brief — the JD's exact
words: "orchestrate a Research Agent... a Simulation Agent... a Synthesis
Agent... You spend your time on validation and strategic interpretation."

Deliberately reuses USD/MXN — the same currency pair behind the
08:00-scenario anomaly in
[01-mcp-langgraph-scout-agent.md](01-mcp-langgraph-scout-agent.md) — so
the two labs form one continuous narrative: Friday's data bug, Sunday's
stress test on the same exposure.

# Prerequisites

Same as the 08:00 lab (`uv`, local Ollama with `qwen3:30b-64k`), plus
real internet access — `research_node` makes a genuine network call to
Yahoo Finance via `yfinance` (no API key required).

# Setup

```bash
cd labs/ai/agentic-demo
uv add yfinance numpy
```

# Steps

`stress_test_graph.py` is a fan-out / fan-in `StateGraph`:

```
START --> research    ----+
START --> simulation  ----+--> synthesis --> END
```

- **research** (`async def`, wraps a blocking `yfinance` call in
  `asyncio.to_thread`): pulls 3 months of real USD/MXN closing prices and
  computes realized daily volatility — actual market data, not a mock.
- **simulation** (`async def`, wraps blocking numpy in
  `asyncio.to_thread`): runs a 20,000-path Monte Carlo simulation of a
  hypothetical $10M MXN-denominated exposure under an assumed *crisis*
  volatility (3x a baseline assumption) over a 30-day horizon —
  deliberately independent of `research`'s real data, because a stress
  test asks "what if," it isn't a backtest.
- **synthesis**: the only node that touches an LLM. Takes both prior
  nodes' output and writes a short executive brief comparing the
  *realized* market condition against the *assumed* stress scenario.

`research` and `simulation` have no dependency on each other in the
graph, so `add_edge(START, "research")` and `add_edge(START,
"simulation")` both fire in the same superstep; running the compiled
graph with `await app.ainvoke(...)` (not `.invoke()`) is what actually
lets them execute as concurrent asyncio tasks instead of one after the
other.

Run:

```bash
uv run stress_test_graph.py
```

# Expected Outcome

`research` and `simulation` complete within a fraction of a second of
each other (proving real concurrency), `synthesis` then makes one LLM
call and the graph prints a short CFO-style brief plus final state.

# Verification

Baseline (each node timed alone, run sequentially by hand):

```
research alone: 0.40s
simulation alone: 0.01s
sequential sum: 0.41s
```

Full graph run, real output:

```
[simulation] done in 0.0s -> {'var_95_usd': 1287438.52, 'worst_case_usd': 2787426.24, 'expected_loss_usd': 328321.99}
[research] done in 0.5s -> {'realized_vol': 0.004505869412350533, 'latest_fx_rate': 17.475000381469727, 'fx_data_points': 67}

[synthesis]
Today's realized volatility (0.4506%) equals the stress scenario's baseline
assumption. The VaR ($1,287,439) is derived from a 3.0x volatility crisis
scenario, which is not reflected in current market conditions. Consequently,
the VaR number represents a hypothetical stress test outcome, not an
immediate risk indicator. It should be treated as a worst-case scenario
analysis, not a near-term exposure estimate.

=== FINAL STATE ===
total wall time: 80.1s
realized vol: 0.4506%
95% VaR: $1,287,439
```

Two honest findings, not oversold ones:

1. **The concurrency is real but the wall-clock win is tiny in absolute
   terms** — `research` and `simulation` together cost ~0.4-0.5s whether
   run in parallel or sequentially, and the single LLM call in
   `synthesis` (part of the 80.1s total) dwarfs it completely. The
   correct lesson isn't "look how much faster parallel is" — here it
   barely matters — it's "the LLM call is the actual bottleneck in this
   pipeline, and fan-out only pays off when the parallelized work is
   itself expensive (a real Snowflake query, a large simulation, a slow
   third-party API)." Worth saying exactly this if asked to justify a
   fan-out design in the interview — parallelism for its own sake on
   cheap operations is complexity without payoff.
2. **The synthesis model's arithmetic is slightly loose**: it called
   0.4506% "equals" the 0.5% baseline assumption — close, not equal.
   Small, but it's a live example of the JD's own "Technical Intuition:
   the ability to identify subtle logic errors or hallucinations in
   agentic output before they reach production" — worth having noticed
   it rather than repeating the brief as gospel.

# Cleanup

Nothing to tear down — no persistent connections, no cloud resources.

# Troubleshooting

- `yfinance` returning an empty DataFrame usually means no internet
  access from wherever this runs, not a code bug — the tool degrades
  silently rather than raising.
- If you don't have real internet access when trying this yourself, swap
  `_fetch_fx_research` for a static/seeded array — the graph topology
  (the actual LangGraph teaching point) doesn't change either way.

# Notes

- This is the concrete, run answer to LangGraph question #19 ("How do
  you handle parallel processing and concurrency in LangGraph
  applications?") — see `topics/salesforce-interview-preparation/langgraph_questions.md`.
- `asyncio.to_thread` matters here specifically because both blocking
  calls (`yfinance`'s HTTP request, numpy's CPU-bound array math) would
  otherwise block the single asyncio event loop and serialize anyway —
  wrapping them is what makes `ainvoke` actually concurrent instead of
  concurrent-looking.

# Related

<!-- RELATED:START -->
- [MCP + LangGraph Scout Agent](01-mcp-langgraph-scout-agent.md) _(ai, langgraph, salesforce-interview-preparation)_
- [LangGraph - Introduction](../../topics/langgraph/01-introduction.md) _(langgraph)_
- [Salesforce Interview Preparation - Introduction](../../topics/salesforce-interview-preparation/01-introduction.md) _(salesforce-interview-preparation)_
<!-- RELATED:END -->
