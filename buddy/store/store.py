#!/usr/bin/env python3
"""What Buddy can sell. Weight files and copied models stay off the shelf."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_packages(path: Path | None = None) -> dict:
    source = path or (HERE / "packages.json")
    return json.loads(source.read_text(encoding="utf-8"))


def shelf(catalog: dict | None = None) -> dict:
    catalog = catalog if catalog is not None else load_packages()
    if catalog.get("frontier_model_trained") is True:
        raise RuntimeError("do not mark a frontier model trained from the catalog")
    for item in catalog["packages"]:
        if item["id"] == "weights" and item["for_sale"]:
            raise RuntimeError("weight package cannot be for sale without a weight file")
    selling = [item["id"] for item in catalog["packages"] if item["for_sale"]]
    held = [item["id"] for item in catalog["packages"] if not item["for_sale"]]
    return {"for_sale": selling, "held": held, "frontier_model_trained": False}


def public_read(owner: str, repo: str, path: str) -> dict:
    clean = path.strip().lstrip("/")
    if any(token in clean.lower() for token in ("token", "secret", ".env")):
        return {"allowed": False, "reason": "That path looks like a secret. Do not fetch it into a lesson."}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{clean}"
    return {"allowed": True, "url": url, "sends_a_token": False, "called": False}


if __name__ == "__main__":
    catalog = load_packages()
    result = shelf(catalog)
    assert "weights" in result["held"] and "weights" not in result["for_sale"]
    assert "data" in result["for_sale"]
    assert result["frontier_model_trained"] is False
    blocked = public_read("DreamCo-Technologies", "Dreamcobots", ".env")
    ok = public_read("DreamCo-Technologies", "Dreamcobots", "README.md")
    assert blocked["allowed"] is False and ok["sends_a_token"] is False and ok["called"] is False
    print(json.dumps(result))
