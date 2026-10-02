#!/usr/bin/env python3
"""Open datasets and free platform docs. This repo does not host or study the files."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "website" / "data" / "free-datasets.json"
PLATFORMS = ROOT / "website" / "data" / "open-platforms.json"


def _rows(path: Path, key: str) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("studied_files") is not False or raw.get("hosted_here") not in {False, None}:
        raise ValueError("a listing must not claim the files were studied or hosted")
    rows = []
    for row in raw[key]:
        href = str(row["href"])
        parsed = urlparse(href)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("bad link")
        if not str(row.get("license", "")).strip() or not str(row.get("category", "")).strip():
            raise ValueError("missing license or category")
        rows.append(row)
    return rows


def catalog() -> dict:
    datasets = _rows(DATA, "datasets")
    platforms = _rows(PLATFORMS, "resources")
    return {
        "datasets": len(datasets),
        "platforms": len(platforms),
        "categories": sorted({row["category"] for row in datasets}),
        "ready_to_train": sum(1 for row in datasets if row["train"]),
        "hosted_here": False,
        "studied_files": False,
    }


if __name__ == "__main__":
    made = catalog()
    assert made["datasets"] >= 1000 and made["platforms"] >= 20
    assert made["studied_files"] is False and "language" in made["categories"]
    print(json.dumps(made))
