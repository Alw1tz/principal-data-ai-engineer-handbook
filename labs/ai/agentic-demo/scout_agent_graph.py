"""LangGraph pipeline mirroring the JD's 08:00 'Intelligence Synthesis' scenario:

    scout (finds anomaly via MCP tool) -> remediate (drafts SQL fix + test)
    -> review (self-correction / peer-review gate) --revise--> remediate
                                                   --approve--> END

Runs against local qwen3 via Ollama (no API tokens spent). State is a plain
TypedDict — this is deliberately small so every transition is visible.
"""
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from mcp_warehouse_server import run_sql_query

llm = ChatOllama(model="qwen3:30b-64k", temperature=0)


class PipelineState(TypedDict):
    anomaly_report: str
    draft_sql: str
    draft_test: str
    review_verdict: str  # "APPROVE" | "REVISE"
    review_notes: str
    revision_count: int


def scout_node(state: PipelineState) -> dict:
    rows = run_sql_query(
        "SELECT country, report_date, revenue_usd FROM revenue_daily "
        "WHERE revenue_usd < 1000 ORDER BY report_date"
    )
    prompt = (
        "You are a data pipeline scout agent. You queried revenue_daily and found "
        f"these suspiciously low rows (likely a currency conversion bug): {rows}\n"
        "In 2-3 sentences, summarize the anomaly for a human data engineer."
    )
    summary = llm.invoke(prompt).content
    print(f"[scout] {summary}\n")
    return {"anomaly_report": summary}


def remediate_node(state: PipelineState) -> dict:
    revision_context = ""
    if state.get("review_notes"):
        revision_context = (
            f"\nA reviewer rejected your previous attempt with this feedback: "
            f"{state['review_notes']}\nAddress it directly."
        )

    prompt = (
        "You are a remediation agent. Anomaly report: "
        f"{state['anomaly_report']}\n"
        "The table is revenue_daily(report_date DATE, country VARCHAR, "
        "currency VARCHAR, revenue_usd DECIMAL). Root cause: the MXN row for "
        "2026-07-24 was converted twice (rate applied to an already-converted value). "
        "Write:\n"
        "1) A single UPDATE statement to correct revenue_usd for that one row back to "
        "approximately 64000 (recompute from the neighboring days' pattern, don't "
        "invent an unrelated number).\n"
        "2) One SQL assertion query that would FAIL (return rows) if the bug recurs.\n"
        f"{revision_context}\n"
        "Return ONLY the two SQL statements, labeled 'FIX:' and 'TEST:'. No prose."
    )
    draft = llm.invoke(prompt).content
    print(f"[remediate]\n{draft}\n")

    fix = draft.split("TEST:")[0].replace("FIX:", "").strip()
    test = draft.split("TEST:")[1].strip() if "TEST:" in draft else ""
    return {"draft_sql": fix, "draft_test": test}


def review_node(state: PipelineState) -> dict:
    prompt = (
        "You are a skeptical senior data engineer peer-reviewing a proposed fix "
        "before it goes to production.\n"
        f"Proposed FIX:\n{state['draft_sql']}\n\n"
        f"Proposed TEST:\n{state['draft_test']}\n\n"
        "Reject if: it's not scoped to exactly the broken row (no WHERE clause "
        "pinning report_date/country), it could touch other rows, or the test "
        "wouldn't actually catch a recurrence.\n"
        "Respond with 'VERDICT: APPROVE' or 'VERDICT: REVISE' on the first line, "
        "then one sentence of reasoning."
    )
    verdict_text = llm.invoke(prompt).content
    print(f"[review] {verdict_text}\n")

    verdict = "REVISE" if "REVISE" in verdict_text.upper() else "APPROVE"
    return {
        "review_verdict": verdict,
        "review_notes": verdict_text,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def route_after_review(state: PipelineState) -> str:
    if state["review_verdict"] == "APPROVE":
        return "approved"
    if state["revision_count"] >= 2:
        return "escalate"
    return "revise"


graph = StateGraph(PipelineState)
graph.add_node("scout", scout_node)
graph.add_node("remediate", remediate_node)
graph.add_node("review", review_node)

graph.set_entry_point("scout")
graph.add_edge("scout", "remediate")
graph.add_edge("remediate", "review")
graph.add_conditional_edges(
    "review",
    route_after_review,
    {"approved": END, "revise": "remediate", "escalate": END},
)

app = graph.compile()


if __name__ == "__main__":
    final_state = app.invoke({"revision_count": 0, "review_notes": ""})
    print("=== FINAL STATE ===")
    print(f"verdict: {final_state['review_verdict']}")
    print(f"revisions needed: {final_state['revision_count']}")
    print(f"final SQL fix:\n{final_state['draft_sql']}")
