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
    packages = catalog["packages"]
    if len(packages) != 20:
        raise RuntimeError("the frontier shop sells 20 packages")
    for item in packages:
        if item.get("ships_weights"):
            raise RuntimeError("no package may ship someone else's weights")
        if not item.get("for_sale"):
            raise RuntimeError("each of the 20 is a lesson you can sell")
    return {
        "for_sale": [item["id"] for item in packages],
        "held": [],
        "count": 20,
        "frontier_model_trained": False,
        "sales_count_known": False,
    }


def public_read(owner: str, repo: str, path: str) -> dict:
    clean = path.strip().lstrip("/")
    if any(token in clean.lower() for token in ("token", "secret", ".env")):
        return {"allowed": False, "reason": "That path looks like a secret. Do not fetch it into a lesson."}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{clean}"
    return {"allowed": True, "url": url, "sends_a_token": False, "called": False}


if __name__ == "__main__":
    catalog = load_packages()
    result = shelf(catalog)
    assert result["count"] == 20 and result["frontier_model_trained"] is False
    assert result["sales_count_known"] is False
    assert all(not item.get("ships_weights") for item in catalog["packages"])
    blocked = public_read("DreamCo-Technologies", "Dreamcobots", ".env")
    ok = public_read("DreamCo-Technologies", "Dreamcobots", "README.md")
    assert blocked["allowed"] is False and ok["sends_a_token"] is False and ok["called"] is False
    print(json.dumps(result))
