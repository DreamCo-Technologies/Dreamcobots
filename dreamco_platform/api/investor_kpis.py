"""Investor KPI router with optional PDF snapshot generation and caching."""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
TTL_SECONDS = 3600


def _load_profiles() -> list[dict[str, Any]]:
    profiles = []
    for profile_path in sorted((ROOT / "bots").glob("*/replit_profile.json")):
        profiles.append(json.loads(profile_path.read_text()))
    return profiles


def _compute_kpis() -> dict[str, Any]:
    profiles = _load_profiles()
    bots_per_tier = Counter(profile.get("tier", "free") for profile in profiles)
    division_breakdown = defaultdict(int)
    for profile in profiles:
        division_breakdown[profile.get("division", "Unknown")] += 1
    active = [profile for profile in profiles if profile.get("status", "active") == "active"]
    price_values = []
    for profile in profiles:
        price = str(profile.get("priceRange", "0")).replace("$", "").replace("/mo", "")
        try:
            price_values.append(float(price.split("-")[0].replace(",", "")))
        except ValueError:
            price_values.append(0.0)
    mrr = sum(price_values)
    return {
        "total_bots": len(profiles),
        "active_bots": len(active),
        "mrr_usd": round(mrr, 2),
        "arr_usd": round(mrr * 12, 2),
        "bots_per_tier": dict(bots_per_tier),
        "avg_revenue_per_bot": round(mrr / len(profiles), 2) if profiles else 0.0,
        "division_breakdown": dict(division_breakdown),
        "growth_rate_30d": 0.0,
    }


def _cached_kpis() -> dict[str, Any]:
    cached = CACHE.get("investor_kpis")
    now = time.time()
    if cached and now - cached[0] < TTL_SECONDS:
        return cached[1]
    value = _compute_kpis()
    CACHE["investor_kpis"] = (now, value)
    return value


def _render_pdf(payload: dict[str, Any]) -> bytes:
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    y = 750
    pdf.drawString(72, y, "DreamCo Investor KPI Snapshot")
    for key, value in payload.items():
        y -= 20
        pdf.drawString(72, y, f"{key}: {value}")
    pdf.save()
    return stream.getvalue()


router = APIRouter(tags=["investor"])


@router.get("/api/investor-kpis")
async def investor_kpis(format: str = "json") -> Response | dict[str, Any]:
    payload = _cached_kpis()
    if format.lower() == "pdf":
        return Response(content=_render_pdf(payload), media_type="application/pdf")
    return payload
