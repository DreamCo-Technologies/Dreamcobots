#!/usr/bin/env python3
"""Free datasets a customer may open. This repo does not host the files."""
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
        if not str(row.get("license", "")).strip():
            raise ValueError("missing license")
        rows.append({
            "name": row["name"],
            "href": href,
            "license": row["license"],
            "train": bool(row["train"]),
            "note": row["note"],
            "hosted_here": False,
        })
    return {
        "count": len(rows),
        "ready_to_train": sum(1 for row in rows if row["train"]),
        "read_the_card_first": sum(1 for row in rows if not row["train"]),
        "hosted_here": False,
        "datasets": rows,
    }


if __name__ == "__main__":
    made = catalog()
    assert made["count"] >= 20 and made["hosted_here"] is False and made["ready_to_train"] >= 8
    print(json.dumps({"count": made["count"], "ready_to_train": made["ready_to_train"], "hosted_here": False}))
