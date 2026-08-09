#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
PROGRAM = ROOT / "config" / "council-bot-career-entrepreneur-program.json"
SANDBOX = ROOT / "config" / "generated" / "bot-sandbox-curriculum.json"
OUT = ROOT / "config" / "generated" / "council-bot-career-paths.json"


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    sandbox_by_slug = {}
    if SANDBOX.exists():
        sandbox = json.loads(SANDBOX.read_text(encoding="utf-8"))
        sandbox_by_slug = {row["slug"]: row for row in sandbox.get("bots", [])}

    paths = []
    for path in sorted(APP_BOTS.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            slug = bot.get("slug")
            if not slug:
                continue
            sandbox_row = sandbox_by_slug.get(slug)
            capability_count = len(bot.get("capabilities") or [])
            stage = "recruit"
            reasons = ["Career path created from canonical bot definition."]
            if sandbox_row:
                stage = "apprentice"
                reasons.append("Sandbox curriculum exists; runtime evidence still required for higher stages.")
            paths.append({
                "slug": slug,
                "display_name": bot.get("displayName"),
                "division": division,
                "category": bot.get("category"),
                "current_stage": stage,
                "stage_reason": reasons,
                "declared_capability_count": capability_count,
                "next_stage": "specialist" if stage == "apprentice" else "apprentice",
                "required_scorecard": program["required_scorecard"],
                "entrepreneur_curriculum": program["entrepreneur_curriculum"],
                "business_graduation_alignment": program["business_graduation_alignment"],
                "career_update_triggers": program["career_update_triggers"],
                "council_review": {
                    "status": "required",
                    "roles": [role["id"] for role in program["council_roles"]],
                    "evidence_required": True,
                    "can_regress_stage": True,
                },
                "entrepreneur_readiness": {
                    "status": "not_proven",
                    "requires_market_evidence": True,
                    "requires_unit_economics": True,
                    "requires_customer_path": True,
                    "requires_owner_permission_boundary": True,
                },
            })

    payload = {
        "schema": "dreamco.council_bot_career_paths.v1",
        "source_program": str(PROGRAM.relative_to(ROOT)),
        "bot_count": len(paths),
        "division_count": len({row["division"] for row in paths}),
        "career_stage_count": len(program["career_stages"]),
        "paths": paths,
        "truth_boundary": "Generated career paths are governance plans. Higher career/business stages require current executable and business evidence; generation alone does not prove readiness."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "bots": len(paths), "divisions": payload["division_count"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
