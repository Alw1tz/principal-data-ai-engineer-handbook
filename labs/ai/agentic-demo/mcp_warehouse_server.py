"""A real MCP server exposing read-only access to a local warehouse.

Stands in for "secure, deep-link access to Snowflake" from the JD.
Two tools only, on purpose — the point of this lab is to see the actual
MCP request/response shape, not to build a full catalog.

Run standalone to see tool discovery + a call over stdio:
    uv run mcp_warehouse_server.py --demo

Run as a real MCP server (what an agent/host would connect to):
    uv run mcp_warehouse_server.py
"""
import sys

import duckdb
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("warehouse")

DB_PATH = "warehouse.duckdb"


@mcp.tool()
def list_tables() -> list[str]:
    """List tables available in the warehouse."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        return [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    finally:
        con.close()


@mcp.tool()
def run_sql_query(sql: str) -> list[dict]:
    """Run a read-only SQL query against the warehouse and return rows as dicts.

    Only SELECT statements are permitted.
    """
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed through this tool.")
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        con.close()


def _demo() -> None:
    """Show what MCP tool discovery + invocation actually look like, without a client."""
    print("=== Tools this server advertises to any MCP client ===")
    for name, tool in mcp._tool_manager._tools.items():
        print(f"- {name}: {tool.description}")
        print(f"  input schema: {tool.parameters}")

    print("\n=== Calling list_tables() directly (same code path a client triggers) ===")
    print(list_tables())

    print("\n=== Calling run_sql_query() with an anomaly-hunting query ===")
    rows = run_sql_query(
        "SELECT country, report_date, revenue_usd FROM revenue_daily "
        "WHERE revenue_usd < 1000 ORDER BY report_date"
    )
    for row in rows:
        print(row)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        _demo()
    else:
        mcp.run(transport="stdio")
