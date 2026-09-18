#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "generated" / "us-open-model-foundry.json"
REPORT = ROOT / "reports" / "US_OPEN_MODEL_FOUNDRY.md"


def main() -> int:
    lora = json.loads((ROOT / "config" / "lora-recipe-catalog.json").read_text())
    rag = json.loads((ROOT / "config" / "rag-backend-catalog.json").read_text())
    payload = {
        "schema": "dreamco.us_open_model_foundry.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "positioning": "US workshop for customer-owned open-source code and optional open-weight specialists",
        "deepseek_comparison": "method and product shape only; no copied weights; no same-task superiority claim",
        "lora_recipes": lora["recipes"],
        "rag_backends": rag["backends"],
        "trained_weights_exist": False,
        "frontier_parity_proven": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# US Open Model Foundry\n\n"
        f"- LoRA recipes: **{len(lora['recipes'])}**\n"
        f"- RAG backends: **{len(rag['backends'])}**\n"
        "- Trained DreamCo frontier weights: **false**\n\n"
        "See docs/US_OPEN_MODEL_FOUNDRY.md\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "recipes": len(lora["recipes"]), "backends": len(rag["backends"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
