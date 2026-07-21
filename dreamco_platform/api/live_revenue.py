"""Live revenue dashboard router with polling websocket updates."""

from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, WebSocket

ROOT = Path(__file__).resolve().parents[2]
STRIPE_EVENTS = ROOT / "reports" / "stripe_events.json"


def _load_events() -> list[dict[str, Any]]:
    return json.loads(STRIPE_EVENTS.read_text()) if STRIPE_EVENTS.exists() else []


def _aggregate(events: list[dict[str, Any]]) -> dict[str, Any]:
    by_bot = defaultdict(float)
    by_division = defaultdict(float)
    by_tier = defaultdict(float)
    for event in events:
        amount = float(event.get("amount_usd", 0))
        by_bot[event.get("bot", "unknown")] += amount
        by_division[event.get("division", "unknown")] += amount
        by_tier[event.get("tier", "unknown")] += amount
    return {"by_bot": dict(by_bot), "by_division": dict(by_division), "by_tier": dict(by_tier), "time_period": "all"}


router = APIRouter(tags=["revenue"])


@router.get("/api/revenue/live")
async def live_revenue() -> dict[str, Any]:
    return _aggregate(_load_events())


@router.websocket("/ws/revenue/stream")
async def revenue_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    last_payload = None
    try:
        while True:
            payload = _aggregate(_load_events())
            if payload != last_payload:
                await websocket.send_json(payload)
                last_payload = payload
            await asyncio.sleep(2)
    finally:
        await websocket.close()
