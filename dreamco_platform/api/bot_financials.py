"""Per-bot financial analytics endpoints."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

ROOT = Path(__file__).resolve().parents[2]
STRIPE_EVENTS = ROOT / "reports" / "stripe_events.json"
COST_EVENTS = ROOT / "reports" / "cost_tracking.json"


def _load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else []


def _bot_metrics(slug: str) -> dict[str, Any]:
    revenue_events = [event for event in _load(STRIPE_EVENTS) if event.get("bot") == slug]
    cost_events = [event for event in _load(COST_EVENTS) if event.get("bot") == slug]
    if not revenue_events and not cost_events:
        raise HTTPException(status_code=404, detail="Bot financials not found")
    revenue = sum(float(event.get("amount_usd", 0)) for event in revenue_events)
    cost = sum(float(event.get("amount_usd", 0)) for event in cost_events)
    margin = (revenue - cost) / revenue if revenue else 0.0
    history = defaultdict(lambda: {"revenue": 0.0, "cost": 0.0})
    for event in revenue_events:
        history[event.get("date", "unknown")]["revenue"] += float(event.get("amount_usd", 0))
    for event in cost_events:
        history[event.get("date", "unknown")]["cost"] += float(event.get("amount_usd", 0))
    return {"slug": slug, "mtd_revenue": revenue, "cost_basis": cost, "net_margin": margin, "trend_30d": list(history.items())[-30:]}


router = APIRouter(tags=["financials"])


@router.get("/api/bots/{slug}/financials")
async def bot_financials(slug: str) -> dict[str, Any]:
    return _bot_metrics(slug)


@router.get("/api/bots/{slug}/financials/history")
async def bot_financial_history(slug: str) -> dict[str, Any]:
    metrics = _bot_metrics(slug)
    return {"slug": slug, "history": metrics["trend_30d"]}
