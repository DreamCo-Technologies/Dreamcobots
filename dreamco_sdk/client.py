"""
DreamCo SDK — Async HTTP Client
==================================

Connects external applications to the DreamCo platform REST API.
"""

from __future__ import annotations

from typing import Any

import httpx

from dreamco_sdk.models import BotResult, BotStatus, RunRequest


class DreamCoClient:
    """Async HTTP client for the DreamCo platform.

    Parameters
    ----------
    api_url:
        Base URL of the DreamCo orchestrator API.
    api_key:
        DreamCo API key (format: ``dc_<tier>_<hex32>``).
    timeout:
        Request timeout in seconds.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: str = "",
        timeout: float = 30.0,
    ) -> None:
        self._base = api_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self._timeout = timeout

    async def list_bots(self) -> list[BotStatus]:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.get(f"{self._base}/api/bots")
            resp.raise_for_status()
            return [BotStatus(**b) for b in resp.json()]

    async def get_bot(self, bot_name: str) -> BotStatus:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.get(f"{self._base}/api/bots/{bot_name}")
            resp.raise_for_status()
            return BotStatus(**resp.json())

    async def run_bot(
        self,
        bot_name: str,
        payload: dict[str, Any] | None = None,
        priority: int = 5,
    ) -> BotResult:
        req = RunRequest(bot_name=bot_name, payload=payload or {}, priority=priority)
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.post(f"{self._base}/api/bots/{bot_name}/run", json=req.model_dump())
            resp.raise_for_status()
            return BotResult(**resp.json())

    async def kill_bot(self, bot_name: str) -> dict[str, Any]:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.post(f"{self._base}/api/bots/{bot_name}/kill")
            resp.raise_for_status()
            return resp.json()

    async def get_memory(self, bot_name: str, key: str) -> Any:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.get(f"{self._base}/api/bots/{bot_name}/memory/{key}")
            resp.raise_for_status()
            return resp.json()

    async def search_memory(self, bot_name: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.get(
                f"{self._base}/api/bots/{bot_name}/memory/recall",
                params={"query": query, "top_k": top_k},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.get(f"{self._base}/health")
            resp.raise_for_status()
            return resp.json()

    async def get_metrics(self) -> str:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as c:
            resp = await c.get(f"{self._base}/metrics")
            resp.raise_for_status()
            return resp.text
