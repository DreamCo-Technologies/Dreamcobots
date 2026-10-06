"""Rank Hugging Face model types by task. No weights are downloaded."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name("catalog.json")


def load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def rank(task: str, catalog: dict | None = None, max_gb: float = 8.0, commercial: bool = True) -> dict:
    data = catalog or load_catalog()
    needle = task.lower().strip()
    rows = []
    for model in data["models"]:
        hay = " ".join([model["type"], model["task"], model["pipeline_tag"], " ".join(model["fits"])]).lower()
        match = 1.0 if needle in hay or any(needle in fit for fit in model["fits"]) else 0.0
        if match == 0.0:
            continue
        license_fit = 0.0 if commercial and not model["commercial_ok"] else 1.0
        hardware_fit = 1.0 if model["min_gb"] <= max_gb else 0.35
        evidence = 0.2
        score = round(match * 0.5 + license_fit * 0.25 + hardware_fit * 0.2 + evidence * 0.05, 3)
        rows.append({
            "type": model["type"],
            "task": model["task"],
            "pipeline_tag": model["pipeline_tag"],
            "score": score,
            "commercial_ok": model["commercial_ok"],
            "min_gb": model["min_gb"],
            "example": model["example"],
            "weights_tested": False,
        })
    rows.sort(key=lambda row: (-row["score"], row["min_gb"], row["type"]))
    return {"task": task, "ranked": rows, "weights_downloaded": False, "production_ranked": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rank model types for a task")
    parser.add_argument("--task", default="voice cloning")
    parser.add_argument("--max-gb", type=float, default=8.0)
    args = parser.parse_args(argv)
    report = rank(args.task, max_gb=args.max_gb)
    print(json.dumps({"task": report["task"], "count": len(report["ranked"]), "top": report["ranked"][:5]}, indent=2))
    return 0 if report["ranked"] else 1


if __name__ == "__main__":
    sys.exit(main())
