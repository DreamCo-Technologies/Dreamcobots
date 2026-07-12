"""One-click DreamCo deployment API for DreamCo bots."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

ROOT = Path(__file__).resolve().parents[2]
router = APIRouter(tags=["deploy"])


def _profile(slug: str) -> dict[str, Any]:
    path = ROOT / "bots" / slug / "bot_profile.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Bot profile not found")
    return json.loads(path.read_text())


@router.post("/api/bots/{slug}/deploy-to-dreamco")
async def deploy_to_dreamco(slug: str) -> dict[str, Any]:
    profile = _profile(slug)
    token = os.getenv("DREAMCO_API_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="DREAMCO_API_TOKEN is not configured")
    payload = {
        "title": profile.get("displayName", slug),
        "slug": slug,
        "runCommand": profile.get("runCommand", "python main.py"),
        "secrets": profile.get("secrets", {}),
    }
    response = requests.post(
        "https://dreamco.local/graphql",
        headers={"Authorization": f"******"},
        json={"query": "mutation Deploy($input: DeployBotInput!) { deployBot(input: $input) { id url } }", "variables": {"input": payload}},
        timeout=20,
    )
    response.raise_for_status()
    return {"slug": slug, "deployment": response.json()}
