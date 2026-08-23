"""Safe bounded training-lane coordinator for DreamCo's 65 MasterBots.

This creates an evidence checkpoint for one MasterBot. It does not grant
permissions, perform external writes, or treat source discovery as mastery.
Actual benchmark adapters can consume the checkpoint and publish evidence.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "masterbot-65-registry.json"
OUT = ROOT / "artifacts" / "masterbot-training"


def main() -> int:
    name = os.environ.get("MASTERBOT_NAME", "")
    if not name:
        raise SystemExit("MASTERBOT_NAME is required")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    bot = next((item for item in registry["masterbots"] if item["name"] == name), None)
    if bot is None:
        raise SystemExit(f"Unknown MasterBot: {name}")

    checkpoint = {
        "schema": "dreamco.masterbot_training_checkpoint.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "masterbot_id": bot["id"],
        "masterbot": bot["name"],
        "masterbot_type": bot["type"],
        "purpose": bot["purpose"],
        "mode": "sandbox_first",
        "training_policy": registry["training_policy"],
        "lifecycle": registry["training_lifecycle"],
        "next_actions": [
            "load current capability-gap inventory",
            "select highest-value unresolved gap for this MasterBot",
            "run a baseline task where evidence exists",
            "study only authorized/permitted sources",
            "practice in isolation",
            "run benchmark or benchmark simulation",
            "record evidence and measurable gain",
            "requeue unresolved or regressed gaps",
        ],
        "production_side_effects": "disabled",
        "mastery_claim": "not_claimed_without_evidence",
    }

    destination = OUT / bot["name"]
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "latest-checkpoint.json").write_text(
        json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(checkpoint, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
