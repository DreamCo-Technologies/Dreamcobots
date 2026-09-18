#!/usr/bin/env python3
"""Validate and publish the supplemental Grok operator team."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "team" / "grok-team.json"
OUT = ROOT / "config" / "generated" / "grok-team-registry.json"
REPORT = ROOT / "reports" / "GROK_TEAM.md"
REQUIRED = {
    "grok-repo-scanner",
    "grok-systems-builder",
    "grok-md-compiler",
    "grok-legacy-placer",
    "grok-actions-operator",
    "grok-fleet-debugger",
    "grok-safety-gate",
    "grok-research",
    "grok-pr-pilot",
    "grok-buddy-bridge",
}


def main() -> int:
    team = json.loads(SRC.read_text(encoding="utf-8"))
    slugs = {bot["slug"] for bot in team["bots"]}
    missing = sorted(REQUIRED - slugs)
    extra = sorted(slugs - REQUIRED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "dreamco.grok_team_registry.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(SRC.relative_to(ROOT)),
        "count": len(team["bots"]),
        "missing_required": missing,
        "unexpected": extra,
        "canonical_baseline_preserved": team.get("canonical_baseline_preserved", 1051),
        "bots": team["bots"],
        "truth_boundary": "Supplemental Grok team. Not part of the 1,051 canonical App_bots count. Sandbox only.",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Grok Team",
        "",
        f"- Registered: **{len(team['bots'])}**",
        f"- Missing required: **{len(missing)}**",
        "- Canonical App_bots count unchanged.",
        "",
        "| Slug | Name | Division | Role |",
        "| --- | --- | --- | --- |",
    ]
    for bot in team["bots"]:
        lines.append(f"| `{bot['slug']}` | {bot['displayName']} | {bot['division']} | {bot['role']} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": not missing, "count": len(slugs), "missing": missing}, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
