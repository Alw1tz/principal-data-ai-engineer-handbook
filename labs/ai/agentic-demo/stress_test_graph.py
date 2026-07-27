"""LangGraph pipeline mirroring the JD's 10:30 'Architectural Orchestration'
scenario: a CFO asks for a market volatility stress test, and instead of
building the model by hand, you orchestrate a Research Agent (real
external market data) and a Simulation Agent (Monte Carlo) to run
CONCURRENTLY, then a Synthesis Agent joins their output into an
executive-ready brief.

Deliberately reuses the same USD/MXN currency pair from the 08:00 demo
(scout_agent_graph.py) — Friday's anomaly was a real currency bug in that
pair; today's stress test asks whether the market itself is already
moving that much for real.

Fan-out / fan-in pattern:

    START --> research    ----+
    START --> simulation  ----+--> synthesis --> END

research and simulation share no dependency on each other, so they run
as real concurrent asyncio tasks (network I/O + CPU-bound numpy both
released to threads via asyncio.to_thread) — this is verified by timing,
not just claimed.
"""
import asyncio
import time
from typing import TypedDict

import numpy as np
import yfinance as yf
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

llm = ChatOllama(model="qwen3:30b-64k", temperature=0)

MXN_EXPOSURE_USD = 10_000_000  # hypothetical MXN-denominated revenue exposure
STRESS_VOL_MULTIPLIER = 3.0  # "crisis" scenario: 3x a typical daily vol assumption
ASSUMED_BASELINE_DAILY_VOL = 0.005  # 0.5%/day, a normal-regime FX vol assumption
N_SIMULATIONS = 20_000
HORIZON_DAYS = 30


class StressTestState(TypedDict):
    realized_vol: float
    latest_fx_rate: float
    fx_data_points: int
    var_95_usd: float
    worst_case_usd: float
    expected_loss_usd: float
    executive_brief: str


def _fetch_fx_research() -> dict:
    """Blocking network call — real USD/MXN data, no API key needed."""
    df = yf.Ticker("MXN=X").history(period="3mo")
    returns = df["Close"].pct_change().dropna()
    return {
        "realized_vol": float(returns.std()),
        "latest_fx_rate": float(df["Close"].iloc[-1]),
        "fx_data_points": len(df),
    }


def _run_monte_carlo() -> dict:
    """Blocking CPU-bound call — independent of research, uses an assumed
    stress scenario rather than realized data (that's the point: this is
    a hypothetical stress test, not a backtest)."""
    rng = np.random.default_rng(seed=42)
    stress_vol = ASSUMED_BASELINE_DAILY_VOL * STRESS_VOL_MULTIPLIER
    daily_shocks = rng.normal(loc=0.0, scale=stress_vol, size=(N_SIMULATIONS, HORIZON_DAYS))
    cumulative_moves = np.prod(1 + daily_shocks, axis=1) - 1
    losses_usd = -np.minimum(cumulative_moves, 0) * MXN_EXPOSURE_USD

    return {
        "var_95_usd": float(np.percentile(losses_usd, 95)),
        "worst_case_usd": float(losses_usd.max()),
        "expected_loss_usd": float(losses_usd.mean()),
    }


async def research_node(state: StressTestState) -> dict:
    t0 = time.monotonic()
    result = await asyncio.to_thread(_fetch_fx_research)
    print(f"[research] done in {time.monotonic() - t0:.1f}s -> {result}\n")
    return result


async def simulation_node(state: StressTestState) -> dict:
    t0 = time.monotonic()
    result = await asyncio.to_thread(_run_monte_carlo)
    print(f"[simulation] done in {time.monotonic() - t0:.1f}s -> {result}\n")
    return result


async def synthesis_node(state: StressTestState) -> dict:
    prompt = (
        "You are a Synthesis Agent writing a 4-5 sentence executive brief "
        "for a CFO who requested a High-Resolution Market Volatility Stress "
        "Test on USD/MXN currency exposure.\n\n"
        f"REALIZED MARKET DATA (last {state['fx_data_points']} trading days): "
        f"current USD/MXN rate {state['latest_fx_rate']:.4f}, realized daily "
        f"volatility {state['realized_vol']:.4%}.\n\n"
        f"STRESS SCENARIO (Monte Carlo, {N_SIMULATIONS:,} paths, "
        f"{HORIZON_DAYS}-day horizon, assumed crisis volatility = "
        f"{STRESS_VOL_MULTIPLIER}x baseline): on a "
        f"${MXN_EXPOSURE_USD:,.0f} MXN-denominated exposure, 95% VaR = "
        f"${state['var_95_usd']:,.0f}, worst simulated case = "
        f"${state['worst_case_usd']:,.0f}, expected loss = "
        f"${state['expected_loss_usd']:,.0f}.\n\n"
        "State plainly whether TODAY'S realized volatility is close to, "
        "far below, or already exceeding the stress scenario's baseline "
        "assumption, and what that implies about how seriously to take the "
        "VaR number. No preamble, no headers, just the brief."
    )
    brief = llm.invoke(prompt).content
    print(f"[synthesis]\n{brief}\n")
    return {"executive_brief": brief}


graph = StateGraph(StressTestState)
graph.add_node("research", research_node)
graph.add_node("simulation", simulation_node)
graph.add_node("synthesis", synthesis_node)

graph.add_edge(START, "research")
graph.add_edge(START, "simulation")
graph.add_edge("research", "synthesis")
graph.add_edge("simulation", "synthesis")
graph.add_edge("synthesis", END)

app = graph.compile()


async def main() -> None:
    t0 = time.monotonic()
    final_state = await app.ainvoke({})
    total = time.monotonic() - t0

    print("=== FINAL STATE ===")
    print(f"total wall time: {total:.1f}s")
    print(f"realized vol: {final_state['realized_vol']:.4%}")
    print(f"95% VaR: ${final_state['var_95_usd']:,.0f}")
    print(f"executive brief:\n{final_state['executive_brief']}")


if __name__ == "__main__":
    asyncio.run(main())
