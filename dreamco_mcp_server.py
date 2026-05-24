"""
DreamCo OS — MCP Server
=========================

Exposes DreamCo tools via the Model Context Protocol (MCP), making the
entire bot ecosystem interoperable with LangChain, CrewAI, AutoGen, and
any MCP-compatible framework.

10 registered MCP tools:
  1. run_bot          — execute a registered bot by name
  2. list_bots        — list all registered bots + health status
  3. get_bot_status   — get a single bot's health check
  4. get_memory       — retrieve a bot's short-term memory key
  5. set_memory       — write to a bot's short-term memory
  6. recall_memory    — semantic vector recall for a bot
  7. kill_bot         — activate kill switch for a bot
  8. get_orchestrator_summary — orchestrator state snapshot
  9. web_search       — search the web
  10. execute_code    — run Python/bash code safely

Run the server::

    python dreamco_mcp_server.py
    # Starts MCP server on port 8765 (WebSocket)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Tool registry — name → (description, input_schema, handler_fn)
_TOOL_REGISTRY: dict[str, dict[str, Any]] = {}


def mcp_tool(name: str, description: str, input_schema: dict[str, Any]):
    """Decorator to register a function as an MCP tool."""
    def decorator(fn):
        _TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": fn,
        }
        return fn
    return decorator


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

_orchestrator: Any = None
_bots: dict[str, Any] = {}


def init_server(orchestrator: Any, bots: dict[str, Any] | None = None) -> None:
    """Initialise the MCP server with an orchestrator and bot registry."""
    global _orchestrator, _bots
    _orchestrator = orchestrator
    _bots = bots or {}


@mcp_tool(
    name="run_bot",
    description="Execute a registered DreamCo bot by name and return its result.",
    input_schema={
        "type": "object",
        "properties": {
            "bot_name": {"type": "string", "description": "Name of the bot to run"},
            "payload": {"type": "object", "description": "Optional task parameters"},
        },
        "required": ["bot_name"],
    },
)
async def run_bot(bot_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if _orchestrator is None:
        return {"error": "Orchestrator not initialised"}
    return await _orchestrator.dispatch(bot_name, payload)


@mcp_tool(
    name="list_bots",
    description="List all registered bots with their current health status.",
    input_schema={"type": "object", "properties": {}},
)
async def list_bots() -> list[dict[str, Any]]:
    if _orchestrator is None:
        return []
    return _orchestrator.list_bots()


@mcp_tool(
    name="get_bot_status",
    description="Get the health check for a specific bot.",
    input_schema={
        "type": "object",
        "properties": {"bot_name": {"type": "string"}},
        "required": ["bot_name"],
    },
)
async def get_bot_status(bot_name: str) -> dict[str, Any]:
    bot = _bots.get(bot_name)
    if bot is None:
        return {"error": f"Bot '{bot_name}' not found"}
    return bot.health_check()


@mcp_tool(
    name="get_memory",
    description="Retrieve a short-term memory key for a bot.",
    input_schema={
        "type": "object",
        "properties": {
            "bot_name": {"type": "string"},
            "key": {"type": "string"},
        },
        "required": ["bot_name", "key"],
    },
)
async def get_memory(bot_name: str, key: str) -> Any:
    bot = _bots.get(bot_name)
    if bot is None or not hasattr(bot, "memory"):
        return {"error": f"Bot '{bot_name}' not found or has no memory"}
    return bot.memory.load(key)


@mcp_tool(
    name="set_memory",
    description="Write a value to a bot's short-term memory.",
    input_schema={
        "type": "object",
        "properties": {
            "bot_name": {"type": "string"},
            "key": {"type": "string"},
            "value": {"description": "Value to store"},
        },
        "required": ["bot_name", "key", "value"],
    },
)
async def set_memory(bot_name: str, key: str, value: Any) -> dict[str, Any]:
    bot = _bots.get(bot_name)
    if bot is None or not hasattr(bot, "memory"):
        return {"error": f"Bot '{bot_name}' not found"}
    bot.memory.save(key, value)
    return {"success": True}


@mcp_tool(
    name="recall_memory",
    description="Semantic vector recall from a bot's long-term memory.",
    input_schema={
        "type": "object",
        "properties": {
            "bot_name": {"type": "string"},
            "query": {"type": "string"},
            "top_k": {"type": "integer", "default": 5},
        },
        "required": ["bot_name", "query"],
    },
)
async def recall_memory(bot_name: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    bot = _bots.get(bot_name)
    if bot is None or not hasattr(bot, "memory"):
        return []
    return bot.memory.recall(query, top_k)


@mcp_tool(
    name="kill_bot",
    description="Activate the kill switch for a specific bot, immediately halting execution.",
    input_schema={
        "type": "object",
        "properties": {"bot_name": {"type": "string"}},
        "required": ["bot_name"],
    },
)
async def kill_bot(bot_name: str) -> dict[str, Any]:
    if _orchestrator is None:
        return {"error": "Orchestrator not initialised"}
    success = _orchestrator.kill(bot_name)
    return {"killed": success, "bot_name": bot_name}


@mcp_tool(
    name="get_orchestrator_summary",
    description="Return a full summary of the orchestrator state.",
    input_schema={"type": "object", "properties": {}},
)
async def get_orchestrator_summary() -> dict[str, Any]:
    if _orchestrator is None:
        return {"error": "Orchestrator not initialised"}
    return _orchestrator.summary()


@mcp_tool(
    name="web_search",
    description="Search the web and return structured results.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_results": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
)
async def web_search_tool(query: str, num_results: int = 5) -> list[dict[str, Any]]:
    from python_bots.tools.web_search import WebSearchTool
    tool = WebSearchTool()
    return await tool.execute(query=query, num_results=num_results)


@mcp_tool(
    name="execute_code",
    description="Execute Python or bash code safely in a subprocess.",
    input_schema={
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "language": {"type": "string", "enum": ["python", "bash"], "default": "python"},
        },
        "required": ["code"],
    },
)
async def execute_code_tool(code: str, language: str = "python") -> dict[str, Any]:
    from python_bots.tools.code_executor import CodeExecutorTool
    tool = CodeExecutorTool()
    return await tool.execute(code=code, language=language)


# ---------------------------------------------------------------------------
# MCP protocol handler (WebSocket / stdio)
# ---------------------------------------------------------------------------

async def _handle_request(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "tools/list":
        tools = [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            }
            for t in _TOOL_REGISTRY.values()
        ]
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}

    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        args = params.get("arguments", {})
        tool = _TOOL_REGISTRY.get(tool_name)
        if tool is None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
            }
        try:
            result = await tool["handler"](**args)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
        except Exception as exc:  # noqa: BLE001
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}}

    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "dreamco-mcp-server", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found"}}


async def run_stdio_server() -> None:
    """Run MCP server on stdio (for use with Claude Desktop, Cursor, etc.)."""
    import sys
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    writer_transport, writer_protocol = await loop.connect_write_pipe(
        asyncio.BaseProtocol, sys.stdout
    )

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            request = json.loads(line.decode())
            response = await _handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as exc:  # noqa: BLE001
            logger.error("MCP stdio error: %s", exc)


def list_tools() -> list[dict[str, Any]]:
    """Return the registered MCP tools (for testing/inspection)."""
    return [{"name": t["name"], "description": t["description"]} for t in _TOOL_REGISTRY.values()]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("DreamCo MCP Server starting — %d tools registered", len(_TOOL_REGISTRY))
    asyncio.run(run_stdio_server())
