#!/usr/bin/env python3
"""Generate Buddy's governed autonomous-everything operating plan."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
READINESS_INDEX = ROOT / "config" / "generated" / "bot_end_to_end_readiness" / "index.json"
SAFETY_FILE = ROOT / "config" / "buddy_laptop_safety.json"
OUTPUT_FILE = ROOT / "config" / "generated" / "buddy_autonomous_everything.json"
REPORT_FILE = ROOT / "reports" / "BUDDY_AUTONOMOUS_EVERYTHING.md"


SAFE_AUTONOMOUS_LANES = [
    {
        "id": "repo_health",
        "goal": "Keep code quality, imports, generated catalogs, reports, and dashboard routes continuously checked.",
        "runs_without_approval": [
            "repository scans",
            "local import audits",
            "TypeScript checks",
            "Python syntax checks",
            "JSON validation",
            "generated bot smoke tests",
            "failure summaries",
        ],
    },
    {
        "id": "bot_buildout",
        "goal": "Move every bot toward a runnable local-first service with prospectus, capabilities, sandbox, workflow, and test evidence.",
        "runs_without_approval": [
            "capability library refresh",
            "sandbox packet refresh",
            "workflow packet refresh",
            "bot prospectus refresh",
            "readiness scoring",
            "local test plans",
        ],
    },
    {
        "id": "app_and_simulation_factory",
        "goal": "Prepare apps, websites, games, courses, simulations, media packets, and business-system packets for Buddy or clients.",
        "runs_without_approval": [
            "requirements packet",
            "design brief",
            "prototype plan",
            "test checklist",
            "deployment checklist",
            "rollback checklist",
        ],
    },
    {
        "id": "all_app_task_control",
        "goal": "Let Buddy help with tasks across apps by preparing visible, reversible, approval-ready steps.",
        "runs_without_approval": [
            "open local dashboard task cards",
            "prepare signup packets",
            "prepare account access checklists",
            "draft form data",
            "draft support messages",
            "draft marketplace listings",
            "prepare browser task instructions",
        ],
    },
    {
        "id": "secret_access_management",
        "goal": "Safely manage access requirements without exposing or committing secret values.",
        "runs_without_approval": [
            "detect missing secret names",
            "verify environment-variable wiring",
            "prepare provider setup checklists",
            "prepare masked secret status reports",
            "prepare rotation instructions",
        ],
    },
    {
        "id": "money_opportunity_research",
        "goal": "Find useful, lawful, low-cost opportunities and prepare reviewed action packets.",
        "runs_without_approval": [
            "opportunity research",
            "lead list structure",
            "pricing drafts",
            "grant and contract checklist drafts",
            "client offer drafts",
            "risk notes",
        ],
    },
]

APPROVAL_WALL = [
    "submit signups",
    "accept terms",
    "grant repository, cloud, payment, email, or social access",
    "create or change live credentials",
    "spend, move, refund, charge, trade, or reconcile money",
    "send outreach, messages, calls, proposals, bids, or social posts",
    "buy domains",
    "publish websites, apps, games, store listings, or marketplace listings",
    "collect private or sensitive people data",
    "make legal, medical, financial, employment, tenant, credit, identity, or public-safety decisions",
    "delete files, overwrite user work, or run destructive commands",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def build_division_queues(readiness: dict[str, Any]) -> list[dict[str, Any]]:
    queues = []
    for shard in readiness.get("division_shards", []):
        division = shard.get("division", "Unknown")
        slug = shard.get("slug", str(division).lower())
        bot_count = int(shard.get("bot_count", 0))
        queues.append(
            {
                "division": division,
                "slug": slug,
                "bot_count": bot_count,
                "autonomous_local_tasks": [
                    "refresh capabilities",
                    "refresh prospectus",
                    "refresh sandbox workflow",
                    "run local readiness checks",
                    "prepare app or service idea packet",
                    "prepare opportunity research packet",
                ],
                "approval_tasks": [
                    "live customer contact",
                    "live signup",
                    "live credential or access change",
                    "live payment, listing, deploy, or publishing action",
                ],
            }
        )
    return queues


def build_report() -> dict[str, Any]:
    readiness = read_json(READINESS_INDEX, {})
    safety = read_json(SAFETY_FILE, {})
    totals = readiness.get("totals", {})
    division_queues = build_division_queues(readiness)
    return {
        "schema": "dreamco.buddy_autonomous_everything.v1",
        "generated_at": utc_now(),
        "mission": "Add governed autonomy for every DreamCo bot, division, app task, signup packet, access request, and local repair loop.",
        "mode": "supervised_autonomous_everything",
        "totals": {
            "bots_connected_to_queue": int(totals.get("bots", 0)),
            "divisions_connected_to_queue": len(division_queues),
            "ready_for_local_end_to_end_testing": int(totals.get("ready_for_local_end_to_end_testing", 0)),
        },
        "safe_autonomous_lanes": SAFE_AUTONOMOUS_LANES,
        "division_queues": division_queues,
        "approval_wall": APPROVAL_WALL,
        "laptop_safety": safety.get("resource_limits", {}),
        "secret_policy": safety.get("secret_key_policy", {}),
        "operating_rule": "Buddy may work continuously on local scans, plans, tests, drafts, packets, and repair reports. Live external impact requires approval.",
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Buddy Autonomous Everything",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Bots connected to queue: {report['totals']['bots_connected_to_queue']}",
        f"- Divisions connected to queue: {report['totals']['divisions_connected_to_queue']}",
        f"- Ready for local end-to-end testing: {report['totals']['ready_for_local_end_to_end_testing']}",
        "",
        "## Safe Autonomous Lanes",
        "",
    ]
    for lane in report["safe_autonomous_lanes"]:
        lines.append(f"- {lane['id']}: {lane['goal']}")
    lines.extend(["", "## Approval Wall", ""])
    for item in report["approval_wall"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Division Queues", ""])
    for queue in report["division_queues"]:
        lines.append(f"- {queue['division']}: {queue['bot_count']} bots")
    lines.extend(["", "## Operating Rule", "", report["operating_rule"], ""])
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy governed autonomous-everything plan.")
    parser.add_argument("--check", action="store_true", help="Fail if generated files are missing or stale in shape.")
    args = parser.parse_args()

    report = build_report()
    if args.check:
        existing = read_json(OUTPUT_FILE, {})
        required_keys = {"schema", "mode", "totals", "safe_autonomous_lanes", "division_queues", "approval_wall"}
        ok = OUTPUT_FILE.exists() and REPORT_FILE.exists() and required_keys.issubset(existing.keys())
        ok = ok and existing.get("totals", {}).get("bots_connected_to_queue") == report["totals"]["bots_connected_to_queue"]
        print(json.dumps({"ok": ok, "bots": report["totals"]["bots_connected_to_queue"], "divisions": report["totals"]["divisions_connected_to_queue"]}, indent=2))
        return 0 if ok else 1

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print(json.dumps({"ok": True, **report["totals"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
