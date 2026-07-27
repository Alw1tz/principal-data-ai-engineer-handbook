"""Talks to mcp_warehouse_server.py as a REAL MCP client over stdio.

This is the piece the --demo mode skips: an actual client session doing
initialize -> list_tools -> call_tool, the same handshake any agent host
(Claude Code, Cursor, a LangGraph tool node) performs against an MCP server.
"""
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command="uv", args=["run", "mcp_warehouse_server.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init_result = await session.initialize()
            print("=== initialize() handshake ===")
            print(f"server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")
            print(f"protocolVersion: {init_result.protocolVersion}")

            print("\n=== tools/list ===")
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"- {t.name}: {t.inputSchema}")

            print("\n=== tools/call: run_sql_query ===")
            result = await session.call_tool(
                "run_sql_query",
                {
                    "sql": (
                        "SELECT country, report_date, revenue_usd FROM revenue_daily "
                        "WHERE revenue_usd < 1000"
                    )
                },
            )
            for block in result.content:
                print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
