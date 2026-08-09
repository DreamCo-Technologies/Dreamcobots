#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
PROGRAM = ROOT / "config" / "autonomous-bot-business-owner-program.json"
OUT = ROOT / "config" / "generated" / "bot-business-owner-curriculum.json"


def words(values):
    return [re.sub(r"[_-]+", " ", str(v)).strip() for v in values if str(v).strip()]


def choose_offer(bot: dict) -> str:
    caps = words(bot.get("capabilities") or [])
    if caps:
        return f"Outcome-focused service using verified capability: {caps[0]}"
    return "Capability audit and assisted service; monetization blocked until a sellable capability is verified"


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    rows = []
    seen = set()
    for path in sorted(APP_BOTS.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            slug = str(bot.get("slug", "")).strip()
            if not slug or slug in seen:
                continue
            seen.add(slug)
            caps = words(bot.get("capabilities") or [])
            rows.append({
                "slug": slug,
                "display_name": bot.get("displayName") or slug,
                "division": division,
                "source": str(path.relative_to(ROOT)),
                "declared_capabilities": caps,
                "business_status": "sandbox_training_not_live_business",
                "offer": choose_offer(bot),
                "target_customer_hypothesis": f"People or organizations needing {caps[0] if caps else slug.replace('-', ' ')}",
                "revenue_experiment": {
                    "target_usd": 1000,
                    "guaranteed": False,
                    "strategies_to_compare": [
                        {"price_usd": 50, "sales_needed": 20},
                        {"price_usd": 100, "sales_needed": 10},
                        {"price_usd": 250, "sales_needed": 4},
                        {"price_usd": 500, "sales_needed": 2}
                    ],
                    "status": "planned_not_run"
                },
                "marketing_channels": program["marketing_channels_to_simulate"],
                "business_owner_curriculum": program["business_owner_curriculum"],
                "workflow_requirements": program["workflow_requirements"],
                "stripe": program["stripe_policy"],
                "autonomy": program["autonomy"],
                "personal_business_sandbox": {
                    "catalog": "config/generated/universal-human-ai-task-sandbox.json",
                    "required": True,
                    "rule": "Map this bot to all applicable personal and business task categories; passing requires executable evidence, not a generated plan."
                },
                "graduation": program["graduation"]
            })
    payload = {
        "schema": "dreamco.bot_business_owner_curriculum.generated.v1",
        "bot_count": len(rows),
        "target_usd_per_bot": program["revenue_experiment"]["target_usd"],
        "aggregate_simulation_target_usd": len(rows) * program["revenue_experiment"]["target_usd"],
        "aggregate_target_is_guarantee": False,
        "bots": rows,
        "truth_boundary": program["truth_rule"]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "bots": len(rows), "aggregate_simulation_target_usd": payload["aggregate_simulation_target_usd"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
