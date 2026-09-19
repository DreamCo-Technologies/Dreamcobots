#!/usr/bin/env python3
"""Emit the next legal, efficient US-weight step. Never claims weights exist."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "config" / "us-weight-system.json"
OUT = ROOT / "config" / "generated" / "us-weight-plan.json"
REPORT = ROOT / "reports" / "US_WEIGHT_SYSTEM.md"


def main() -> int:
    spec = json.loads(SRC.read_text(encoding="utf-8"))
    next_id = spec["line"][0]["id"] if not spec["trained_weights_exist"] else spec["line"][1]["id"]
    plan = {
        "schema": "dreamco.us_weight_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "next_train_target": next_id,
        "do_now": [
            "RAG + eval packs",
            "QLoRA on dream-work base candidate",
            "holdout + safety + fleet regression",
            "only then consider MoE pretrain budget",
        ],
        "do_not": [
            "claim frontier parity",
            "download leaked checkpoints",
            "train on client data globally",
            "skip dream-edge/work and jump to dream-frontier",
        ],
        "trained_weights_exist": spec["trained_weights_exist"],
        "frontier_parity_proven": spec["frontier_parity_proven"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# US Weight System Plan\n\n"
        f"- Next target: **{next_id}**\n"
        f"- Weights exist: **{spec['trained_weights_exist']}**\n"
        f"- Frontier parity: **{spec['frontier_parity_proven']}**\n\n"
        "See docs/US_WEIGHT_SYSTEM.md\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "next": next_id, "weights_exist": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
