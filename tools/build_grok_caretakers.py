#!/usr/bin/env python3
"""Give every canonical bot, system package, and proposed division a Grok caretaker."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "App_bots"
SYSTEMS = ROOT / "systems"
PROPOSED = ROOT / "config" / "proposed-10-divisions.json"
OUT = ROOT / "config" / "generated" / "grok-caretakers.json"
REPORT = ROOT / "reports" / "GROK_CARETAKERS.md"

CHECKS = [
    "connected_to_study_resources",
    "has_required_code_or_stub",
    "tools_listed",
    "capabilities_listed",
    "original_goal_studied",
    "grok_twin_route",
    "sandbox_only_until_gates",
]


def main() -> int:
    caretakers = []
    if APP.exists():
        for path in sorted(APP.glob("*.json")):
            if path.name.startswith("masterbots"):
                continue
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            division = doc.get("division") or path.stem
            for bot in doc.get("bots", []) if isinstance(doc, dict) else []:
                if not isinstance(bot, dict) or not bot.get("slug"):
                    continue
                caretakers.append({
                    "kind": "canonical_bot",
                    "slug": bot["slug"],
                    "division": division,
                    "grok_caretaker": f"grok-care-{bot['slug']}"[:140],
                    "model_route": "xai/grok-best-available",
                    "goal": str(bot.get("description") or bot.get("displayName") or bot["slug"])[:400],
                    "checks": CHECKS,
                    "canonical_counted": True,
                })
    if SYSTEMS.exists():
        for path in sorted(SYSTEMS.glob("*/bots.json")):
            caretakers.append({
                "kind": "system_package",
                "slug": path.parent.name,
                "division": path.parent.name,
                "grok_caretaker": f"grok-care-system-{path.parent.name.lower()}"[:140],
                "model_route": "xai/grok-best-available",
                "goal": f"Keep {path.parent.name} connected, tested, and sandbox-safe",
                "checks": CHECKS,
                "canonical_counted": False,
            })
    if PROPOSED.exists():
        proposed = json.loads(PROPOSED.read_text(encoding="utf-8"))
        for row in proposed.get("divisions", []):
            caretakers.append({
                "kind": "proposed_division",
                "slug": row["id"],
                "division": row["id"],
                "grok_caretaker": f"grok-care-{row['id'].lower()}",
                "model_route": "xai/grok-best-available",
                "goal": row["mission"],
                "covers": row.get("covers", []),
                "checks": CHECKS,
                "canonical_counted": False,
            })
    payload = {
        "schema": "dreamco.grok_caretakers.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(caretakers),
        "canonical_baseline_preserved": 1051,
        "caretakers": caretakers,
        "truth": "Caretakers are Grok routes + checklists. They do not add to the 1,051 count or prove live tool execution.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    kinds = {}
    for row in caretakers:
        kinds[row["kind"]] = kinds.get(row["kind"], 0) + 1
    lines = ["# Grok Caretakers", "", f"- Total: **{len(caretakers)}**"]
    for key, value in sorted(kinds.items()):
        lines.append(f"- {key}: **{value}**")
    lines += ["", "## Proposed 10 divisions", ""]
    if PROPOSED.exists():
        for row in json.loads(PROPOSED.read_text())["divisions"]:
            lines.append(f"- **{row['id']}**: {row['mission']}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "caretakers": len(caretakers), "kinds": kinds}))
    return 0 if caretakers else 1


if __name__ == "__main__":
    raise SystemExit(main())
