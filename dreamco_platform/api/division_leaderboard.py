"""Division leaderboard endpoints for DreamCo performance rankings."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query

ROOT = Path(__file__).resolve().parents[2]


def _profiles() -> list[dict[str, Any]]:
    return [json.loads(path.read_text()) for path in sorted((ROOT / "bots").glob("*/bot_profile.json"))]


def _leaderboard() -> list[dict[str, Any]]:
    divisions = defaultdict(lambda: {"total_bots": 0, "active_bots": 0, "mtd_revenue": 0.0, "avg_health_score": 0.8, "pct_elite": 0.0, "sparkline": []})
    for profile in _profiles():
        division = profile.get("division", "Unknown")
        divisions[division]["total_bots"] += 1
        divisions[division]["active_bots"] += int(profile.get("status", "active") == "active")
        divisions[division]["mtd_revenue"] += 0.0
        divisions[division]["pct_elite"] += int(profile.get("tier") == "elite")
        divisions[division]["sparkline"] = [0, 1, 2, 3, 4]
    rows = []
    for division, data in divisions.items():
        total = max(data["total_bots"], 1)
        data["pct_elite"] = round(data["pct_elite"] / total, 4)
        rows.append({"division": division, **data})
    return rows


router = APIRouter(tags=["divisions"])


@router.get("/api/divisions/leaderboard")
async def division_leaderboard(sort_by: str = Query("total_bots")) -> list[dict[str, Any]]:
    rows = _leaderboard()
    return sorted(rows, key=lambda row: row.get(sort_by, 0), reverse=True)
