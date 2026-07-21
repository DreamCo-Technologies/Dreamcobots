from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("dreamco.mcp_server")

# ---------------------------------------------------------------------------
# MCP Tool Schema Builder
# ---------------------------------------------------------------------------
def _agent_to_tool(bot) -> Dict:
    """Convert a DreamCoBot to an MCP tool schema."""
    return {
        "name": f"dreamco_{bot.name.lower().replace(' ', '_').replace('-', '_')}",
        "description": (
            f"[DreamCo Agent — {bot.category}] {bot.description or bot.name}. "
            f"Methods: run, analyze, monetize, report."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["run", "analyze", "monetize", "report"],
                    "description": "Which agent method to invoke",
                    "default": "run",
                },
                "kwargs": {
                    "type": "object",
                    "description": "Optional keyword arguments passed to the method",
                    "additionalProperties": True,
                },
            },
            "required": ["method"],
        },
    }


# ---------------------------------------------------------------------------
# MCP Server (stdio transport)
# ---------------------------------------------------------------------------
class DreamCoMCPServer:
    """
    MCP server that exposes DreamCo agents as tools.
    Run standalone: python -m mcp_server.server
    Or integrate with Claude Desktop / any MCP client.
    """

    def __init__(self):
        from orchestrator.orchestrator import get_orchestrator
        self.orchestrator = get_orchestrator()
        self.server_info = {
            "name":    "dreamco-mcp-server",
            "version": "1.0.0",
        }

    def get_tools(self) -> List[Dict]:
        tools = []
        for bot in self.orchestrator.list_agents():
            agent = self.orchestrator.get(bot["agent_id"])
            if agent:
                tools.append(_agent_to_tool(agent))
        # Add orchestrator-level tools
        tools.append({
            "name": "dreamco_orchestrator_status",
            "description": "Get full health and revenue status of the DreamCo OS",
            "inputSchema": {"type": "object", "properties": {}},
        })
        tools.append({
            "name": "dreamco_revenue_report",
            "description": "Get aggregate revenue, cost, and profit across all agents",
            "inputSchema": {"type": "object", "properties": {}},
        })
        tools.append({
            "name": "dreamco_dispatch_category",
            "description": "Dispatch a method to ALL agents in a given category simultaneously",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Agent category"},
                    "method": {"type": "string", "enum": ["run", "analyze", "monetize", "report"]},
                },
                "required": ["category", "method"],
            },
        })
        return tools

    def call_tool(self, name: str, arguments: Dict) -> Dict:
        """Execute a tool call from an MCP client."""
        try:
            if name == "dreamco_orchestrator_status":
                return {
                    "health": self.orchestrator.health_check(),
                    "agents": self.orchestrator.list_agents(),
                }

            if name == "dreamco_revenue_report":
                return self.orchestrator.revenue_report()

            if name == "dreamco_dispatch_category":
                results = self.orchestrator.dispatch_all(
                    arguments["category"],
                    arguments.get("method", "run"),
                )
                return {"results": [r.to_dict() for r in results]}

            # Route to specific agent
            # Tool names are prefixed with "dreamco_"
            tool_suffix = name.removeprefix("dreamco_")
            agent = None
            for bot in self.orchestrator.list_agents():
                canonical = bot["name"].lower().replace(" ", "_").replace("-", "_")
                if canonical == tool_suffix:
                    agent = self.orchestrator.get(bot["agent_id"])
                    break

            if agent is None:
                return {"error": f"Agent for tool '{name}' not found"}

            method = arguments.get("method", "run")
            kwargs = arguments.get("kwargs", {})
            result = agent.execute(method, **kwargs)
            return result.to_dict()

        except Exception as e:
            logger.error(f"MCP tool call error: {e}", exc_info=True)
            return {"error": str(e)}

    async def run_stdio(self):
        """Run MCP server over stdio (compatible with Claude Desktop config)."""
        import sys

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        loop = asyncio.get_event_loop()
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        writer_transport, writer_protocol = await loop.connect_write_pipe(
            lambda: asyncio.BaseProtocol(), sys.stdout
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)

        async def send(obj: Dict):
            data = json.dumps(obj) + "\n"
            writer.write(data.encode())
            await writer.drain()

        # Handshake
        while True:
            line = await reader.readline()
            if not line:
                break
            try:
                req = json.loads(line.decode().strip())
            except json.JSONDecodeError:
                continue

            method = req.get("method", "")
            req_id = req.get("id")

            if method == "initialize":
                await send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": self.server_info,
                        "capabilities": {"tools": {}},
                    }
                })
            elif method == "tools/list":
                await send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"tools": self.get_tools()}
                })
            elif method == "tools/call":
                params = req.get("params", {})
                result = self.call_tool(params.get("name", ""), params.get("arguments", {}))
                await send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                })
            else:
                await send({
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                })


if __name__ == "__main__":
    server = DreamCoMCPServer()
    asyncio.run(server.run_stdio())