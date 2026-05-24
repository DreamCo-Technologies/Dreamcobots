from __future__ import annotations

from typing import Any, AsyncIterator, Dict

import httpx


class DreamCoSDKClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def health(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/run", json=payload)
            response.raise_for_status()
            return response.json()

    async def stream_events(self) -> AsyncIterator[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", f"{self.base_url}/events") as stream:
                async for line in stream.aiter_lines():
                    if line:
                        yield {"raw": line}
