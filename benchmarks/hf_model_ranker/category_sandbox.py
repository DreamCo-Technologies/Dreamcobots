"""Sandbox probe for every Hugging Face category in the local catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.hf_model_ranker.rank import load_catalog

OUT = Path(__file__).with_name("category_sandbox.json")


def probe(catalog: dict | None = None) -> dict:
    data = catalog or load_catalog()
    categories = sorted({row["pipeline_tag"] for row in data["models"]})
    results = []
    for tag in categories:
        rows = [row for row in data["models"] if row["pipeline_tag"] == tag]
        results.append({
            "pipeline_tag": tag,
            "types": len(rows),
            "ok": bool(rows) and all(row.get("example") and row.get("task") for row in rows),
            "weights_downloaded": False,
            "live_inference": False,
        })
    return {
        "categories": len(results),
        "passed": sum(1 for row in results if row["ok"]),
        "failed": sum(1 for row in results if not row["ok"]),
        "weights_downloaded": False,
        "results": results,
    }


def main() -> int:
    report = probe()
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("categories", "passed", "failed", "weights_downloaded")}))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
