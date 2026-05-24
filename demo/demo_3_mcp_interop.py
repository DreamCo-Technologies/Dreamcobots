"""
Demo 3 — MCP Interoperability
================================

Shows the DreamCo MCP server listing its tools and handling a tool call.
Demonstrates how external frameworks (Claude, LangChain, etc.) can
consume DreamCo bots via the MCP protocol.

Run::

    python demo/demo_3_mcp_interop.py
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import dreamco_mcp_server as mcp
from python_bots.core.base_bot import DreamCoBot
from python_bots.orchestrator import DreamCoOrchestrator


class StockAnalysisBot(DreamCoBot):
    async def run(self): return {"ticker": "AAPL", "price": 189.30, "signal": "BUY"}
    async def analyze(self): return {"pe_ratio": 28.5, "revenue_growth": 0.12}
    async def monetize(self): return {"signals_generated": 1, "value_usd": 0.10}
    async def report(self): return {"bot": self.name}


async def main():
    print("=" * 60)
    print("  Demo 3: MCP Protocol Interoperability")
    print("=" * 60)

    # Set up orchestrator + bots
    orch = DreamCoOrchestrator()
    bot = StockAnalysisBot("stock_analysis")
    orch.register(bot)
    bots = {"stock_analysis": bot}

    # Initialise MCP server
    mcp.init_server(orch, bots)

    print(f"\n📡 DreamCo MCP Server — {len(mcp._TOOL_REGISTRY)} tools registered")

    # List tools (simulating a Claude Desktop tools/list call)
    print("\n🔧 Available MCP Tools:")
    for tool in mcp.list_tools():
        print(f"   • {tool['name']}: {tool['description']}")

    # Simulate MCP initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    }
    init_response = await mcp._handle_request(init_request)
    print(f"\n✅ Initialize response:")
    print(f"   Protocol: {init_response['result']['protocolVersion']}")
    print(f"   Server: {init_response['result']['serverInfo']['name']}")

    # Simulate tools/call: run_bot
    print("\n🤖 Calling run_bot via MCP...")
    run_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "run_bot",
            "arguments": {"bot_name": "stock_analysis"},
        },
    }
    run_response = await mcp._handle_request(run_request)
    result_text = run_response["result"]["content"][0]["text"]
    result = json.loads(result_text)
    print(f"   Success: {result.get('success')}")
    print(f"   Result: {result.get('result')}")

    # Simulate tools/call: list_bots
    print("\n📋 Calling list_bots via MCP...")
    list_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "list_bots", "arguments": {}},
    }
    list_response = await mcp._handle_request(list_request)
    bots_text = list_response["result"]["content"][0]["text"]
    bots_list = json.loads(bots_text)
    print(f"   Found {len(bots_list)} bots:")
    for b in bots_list:
        print(f"   • {b['name']} — state: {b['state']}")

    # Simulate tools/call: web_search
    print("\n🔍 Calling web_search via MCP (mock)...")
    search_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "web_search",
            "arguments": {"query": "DreamCo Technologies AI agents", "num_results": 3},
        },
    }
    search_response = await mcp._handle_request(search_request)
    search_results = json.loads(search_response["result"]["content"][0]["text"])
    print(f"   Got {len(search_results)} results (mock)")
    print(f"   First result: {search_results[0]['title']}")

    print("\n✨ Demo 3 complete!")
    print("\n💡 To use with Claude Desktop, add to claude_desktop_config.json:")
    print('   { "mcpServers": { "dreamco": { "command": "python", "args": ["dreamco_mcp_server.py"] } } }')
    print()


if __name__ == "__main__":
    asyncio.run(main())
