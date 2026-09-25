#!/usr/bin/env python3
"""Free datasets a customer may open. Studying a listing does not download it."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "website" / "data" / "free-datasets.json"


def catalog() -> dict:
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    rows = []
    for row in raw["datasets"]:
        href = str(row["href"])
        parsed = urlparse(href)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("bad dataset link")
        if not str(row.get("license", "")).strip() or not str(row.get("category", "")).strip():
            raise ValueError("missing license or category")
        rows.append({
            "name": row["name"],
            "href": href,
            "license": row["license"],
            "category": row["category"],
            "train": bool(row["train"]),
            "note": row["note"],
            "hosted_here": False,
        })
    return {
        "count": len(rows),
        "ready_to_train": sum(1 for row in rows if row["train"]),
        "read_the_card_first": sum(1 for row in rows if not row["train"]),
        "categories": sorted({row["category"] for row in rows}),
        "hosted_here": False,
        "studied_files": False,
        "datasets": rows,
    }


def study_all() -> dict:
    made = catalog()
    studies = []
    for row in made["datasets"]:
        studies.append({
            "name": row["name"],
            "source": row["href"],
            "license": row["license"],
            "category": row["category"],
            "own": f"Cite {row['name']} and follow {row['license']}. Do not treat the card as a trained weight.",
            "downloaded": False,
        })
    return {
        "studied_listings": len(studies),
        "studied_files": False,
        "weights_trained": False,
        "studies": studies,
    }


if __name__ == "__main__":
    made = catalog()
    studied = study_all()
    assert made["count"] >= 500 and made["hosted_here"] is False and made["studied_files"] is False
    assert studied["studied_listings"] == made["count"] and studied["weights_trained"] is False
    print(json.dumps({
        "count": made["count"],
        "ready_to_train": made["ready_to_train"],
        "categories": made["categories"],
        "studied_listings": studied["studied_listings"],
        "studied_files": False,
    }))
