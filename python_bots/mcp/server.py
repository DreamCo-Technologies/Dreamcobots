from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket


@dataclass
class MCPEventBus:
    events: List[Dict[str, Any]] = field(default_factory=list)

    async def publish(self, event: Dict[str, Any]) -> None:
        self.events.append(event)


bus = MCPEventBus()
app = FastAPI(title="DreamCo MCP Server", version="1.0.0")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/bots")
async def list_bots() -> Dict[str, List[str]]:
    return {"bots": []}


@app.post("/run")
async def run_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = {"type": "task_run", "payload": payload}
    await bus.publish(event)
    return {"accepted": True, "event": event}


@app.websocket("/events")
async def event_stream(ws: WebSocket) -> None:
    await ws.accept()
    index = 0
    try:
        while True:
            await asyncio.sleep(0.5)
            while index < len(bus.events):
                await ws.send_json(bus.events[index])
                index += 1
    except Exception:
        await ws.close()
