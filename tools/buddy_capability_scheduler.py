"""Select the next Buddy training jobs using capability value per compute cost."""
from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "config" / "buddy-capability-graph-v2.json"
OUT = ROOT / "artifacts" / "buddy-capability-training"


def priority(item: dict) -> float:
    gap = float(item.get("gap_severity", 0.5))
    value = float(item.get("user_value", 0.5))
    transfer = float(item.get("transfer_value", 0.5))
    gain = float(item.get("expected_learning_gain", 0.5))
    cost = max(float(item.get("estimated_compute_cost", 1.0)), 0.001)
    return gap * value * transfer * gain / cost


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    raw = os.getenv("BUDDY_CAPABILITY_QUEUE", "")
    if raw:
        items = json.loads(raw)
    else:
        items = [{
            "capability": "unclassified_gap",
            "gap_severity": 1.0,
            "user_value": 1.0,
            "transfer_value": 0.8,
            "expected_learning_gain": 0.8,
            "estimated_compute_cost": 1.0,
        }]

    for item in items:
        item["priority"] = round(priority(item), 8)
        item["recommended_path"] = [
            "deterministic_check",
            "cached_knowledge",
            "targeted_retrieval",
            "small_model_practice",
            "sandbox",
            "larger_reasoning_model_if_needed",
            "transfer_test",
            "regression"
        ]

    limit = int(os.getenv("BUDDY_TRAINING_QUEUE_SIZE", "50"))
    items.sort(key=lambda x: (-x["priority"], x.get("capability", "")))
    result = {
        "schema": "dreamco.buddy.training_queue.v1",
        "graph_schema": graph["schema"],
        "queue": items[:limit],
        "principle": "maximize capability improvement per unit compute while preserving evidence and test integrity"
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "latest-queue.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
