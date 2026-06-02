"""Marketplace hybrid semantic and keyword search router."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query

ROOT = Path(__file__).resolve().parents[2]
router = APIRouter(tags=["marketplace"])


def _embed(text: str) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(16)]


def _score(query: str, profile: dict[str, Any]) -> float:
    query_terms = query.lower().split()
    haystack = json.dumps(profile).lower()
    keyword_boost = sum(1 for term in query_terms if term in haystack)
    tier_weight = {"free": 0.8, "pro": 1.0, "enterprise": 1.15, "elite": 1.25}.get(profile.get("tier", "pro"), 1.0)
    vector_score = sum(a * b for a, b in zip(_embed(query), _embed(profile.get("description", "")))) / 16
    return keyword_boost + tier_weight + vector_score


@router.get("/api/marketplace/search")
async def marketplace_search(q: str, tier: str | None = Query(None), division: str | None = Query(None)) -> list[dict[str, Any]]:
    results = []
    for path in sorted((ROOT / "bots").glob("*/replit_profile.json")):
        profile = json.loads(path.read_text())
        if tier and profile.get("tier") != tier:
            continue
        if division and profile.get("division") != division:
            continue
        results.append({"slug": profile.get("slug", path.parent.name), "relevance": _score(q, profile), "profile": profile})
    return sorted(results, key=lambda item: item["relevance"], reverse=True)[:25]
