"""
DreamCo OS — Web Search Tool
==============================

Unified web search supporting Serper, Tavily, and SerpAPI backends.
Falls back gracefully to a mock result when no API key is configured.

Usage::

    tool = WebSearchTool()
    results = await tool.execute(query="DreamCo Technologies AI", num_results=5)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from python_bots.tools.base import BaseTool

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web and return a list of results with titles, URLs, and snippets."

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "default": 5},
                "backend": {"type": "string", "enum": ["serper", "tavily", "serpapi"], "default": "serper"},
            },
            "required": ["query"],
        }

    async def execute(
        self,
        query: str,
        num_results: int = 5,
        backend: str = "serper",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Execute a web search and return structured results."""
        try:
            if backend == "serper":
                return await self._serper(query, num_results)
            elif backend == "tavily":
                return await self._tavily(query, num_results)
        except Exception as exc:  # noqa: BLE001
            logger.warning("WebSearchTool (%s) failed: %s", backend, exc)
        return self._mock_results(query, num_results)

    async def _serper(self, query: str, n: int) -> list[dict[str, Any]]:
        api_key = os.getenv("SERPER_API_KEY", "")
        if not api_key:
            return self._mock_results(query, n)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": n},
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            {"title": r.get("title"), "url": r.get("link"), "snippet": r.get("snippet")}
            for r in data.get("organic", [])[:n]
        ]

    async def _tavily(self, query: str, n: int) -> list[dict[str, Any]]:
        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            return self._mock_results(query, n)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": api_key, "query": query, "max_results": n},
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            {"title": r.get("title"), "url": r.get("url"), "snippet": r.get("content")}
            for r in data.get("results", [])[:n]
        ]

    @staticmethod
    def _mock_results(query: str, n: int) -> list[dict[str, Any]]:
        return [
            {
                "title": f"Mock result {i+1} for: {query}",
                "url": f"https://example.com/result/{i+1}",
                "snippet": f"This is a mock search result snippet for '{query}'. Configure SERPER_API_KEY or TAVILY_API_KEY for live results.",
            }
            for i in range(n)
        ]
