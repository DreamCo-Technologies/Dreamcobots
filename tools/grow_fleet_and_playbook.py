#!/usr/bin/env python3
"""Materialize 10 growth divisions and publish the Grok learn/earn playbook."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "config" / "new-divisions-seed.json"
APP = ROOT / "App_bots"
PLAY = ROOT / "config" / "grok-help-playbook.json"
OUT = ROOT / "config" / "generated" / "fleet-growth.json"
REPORT = ROOT / "reports" / "FLEET_GROWTH_AND_GROK_PLAYBOOK.md"


def main() -> int:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    created = []
    APP.mkdir(parents=True, exist_ok=True)
    for division, slugs in seed["divisions"].items():
        bots = []
        for slug in slugs:
            bots.append({
                "slug": slug,
                "displayName": slug.replace("-", " ").title(),
                "tier": "pro",
                "category": "growth",
                "description": f"Growth bot in {division}. Grok caretaker studies its goal and keeps tools in sandbox.",
                "capabilities": ["goal-study", "resource-link", "sandbox-demo", "grok-care"],
                "status": "active",
                "growth": True,
            })
        doc = {"division": division, "total": len(bots), "growth": True, "bots": bots}
        (APP / f"{division}.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        created.append({"division": division, "bots": len(bots)})
    play = json.loads(PLAY.read_text(encoding="utf-8"))
    payload = {
        "schema": "dreamco.fleet_growth_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "divisions_added": created,
        "new_bot_count": sum(row["bots"] for row in created),
        "learn_actions": len(play["learn"]),
        "earn_actions": len(play["earn"]),
        "canonical_count_is_a_cap": False,
        "live_money": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Fleet growth and Grok playbook",
        "",
        f"- New divisions: **{len(created)}**",
        f"- New bots: **{payload['new_bot_count']}**",
        f"- Learn actions: **{payload['learn_actions']}**",
        f"- Earn actions: **{payload['earn_actions']}**",
        "- 1051 is a snapshot, not a cap.",
        "",
        "## Divisions",
        "",
    ]
    for row in created:
        lines.append(f"- {row['division']}: {row['bots']} bots")
    lines += ["", "## Learn", ""]
    for item in play["learn"]:
        lines.append(f"- {item}")
    lines += ["", "## Earn (sandbox until live-revenue-gate)", ""]
    for item in play["earn"]:
        lines.append(f"- {item}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, **{k: payload[k] for k in ("new_bot_count", "learn_actions", "earn_actions")}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
