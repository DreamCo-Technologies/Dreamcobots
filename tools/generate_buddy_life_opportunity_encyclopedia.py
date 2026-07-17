#!/usr/bin/env python3
"""Generate Buddy life, work, and business opportunity encyclopedia."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "buddy_life_opportunity_encyclopedia.json"
REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
CONTRACT_REPORT_FILE = ROOT / "reports" / "bot_contract_discovery_report.json"
OUTPUT_JSON = ROOT / "reports" / "buddy_life_opportunity_encyclopedia.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_LIFE_OPPORTUNITY_ENCYCLOPEDIA.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_lane_packet(lane: dict[str, Any], bot_count: int) -> dict[str, Any]:
    return {
        **lane,
        "bot_coverage": bot_count,
        "refresh_cadence": "weekly" if lane["id"] in {"settlements_and_claims", "jobs_and_careers"} else "monthly",
        "buddy_prompt": (
            f"Buddy, help me with {lane['label'].lower()}. Research official or owner-approved sources, "
            "show the steps, score fit, and stop before any approval-required action."
        ),
        "client_task_packet": {
            "inputs": ["client_goal", "location", "deadline", "budget", "documents_available", "risk_tolerance"],
            "outputs": ["source_list", "fit_score", "eligibility_questions", "document_checklist", "approval_packet"],
            "must_not_do": lane.get("approval_required", []),
        },
    }


def build_report() -> dict[str, Any]:
    config = read_json(CONFIG_FILE, {})
    registry = read_json(REGISTRY_FILE, {})
    contract_report = read_json(CONTRACT_REPORT_FILE, {})
    bots = registry.get("bots", [])
    lanes = [build_lane_packet(lane, len(bots)) for lane in config.get("resource_lanes", [])]
    approval_wall = config.get("approval_wall", [])
    source_policy = config.get("source_policy", {})

    return {
        "schema": "dreamco.buddy_life_opportunity_encyclopedia_report.v1",
        "generated_at": utc_now(),
        "source_config": rel(CONFIG_FILE),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": {
            "bot_count": len(bots),
            "resource_lanes": len(lanes),
            "lanes_with_all_bot_coverage": sum(1 for lane in lanes if lane["bot_coverage"] == len(bots)),
            "friend_copilot_steps": len(config.get("friend_copilot", {}).get("split_screen_steps", [])),
            "device_surfaces": len(config.get("friend_copilot", {}).get("device_surfaces", [])),
            "approval_gates": len(approval_wall),
            "allowed_source_types": len(source_policy.get("allowed", [])),
            "blocked_source_types": len(source_policy.get("blocked", [])),
            "contract_opportunity_types": contract_report.get("summary", {}).get("opportunity_types_tracked", 0),
            "settlement_claims_guarded": any(lane["id"] == "settlements_and_claims" for lane in lanes),
            "unclaimed_estate_research_ready": any(lane["id"] == "unclaimed_money_estates" for lane in lanes),
        },
        "friend_copilot": config.get("friend_copilot", {}),
        "resource_lanes": lanes,
        "source_policy": source_policy,
        "approval_wall": approval_wall,
        "safety_note": (
            "Buddy can research, organize, score, and prepare packets. Buddy must not create false claims, "
            "guarantee money, submit applications, contact outside parties, or provide legal/financial/credit decisions without approval and review."
        ),
        "next_actions": [
            "Connect this encyclopedia to the Actions page task screen.",
            "Create weekly official-source settlement and claims digest with truthful eligibility questions.",
            "Create official unclaimed-property and estate research checklists by state and country.",
            "Map each bot division to associations, job boards, grants, contracts, and side-hustle resources.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Buddy Life Opportunity Encyclopedia",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Resource lanes: {summary['resource_lanes']}",
        f"- Bot coverage: {summary['bot_count']}",
        f"- Friend copilot steps: {summary['friend_copilot_steps']}",
        f"- Device surfaces: {summary['device_surfaces']}",
        f"- Approval gates: {summary['approval_gates']}",
        "",
        "## Resource Lanes",
        "",
    ]
    for lane in report["resource_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["purpose"])
        lines.append("")
        lines.append(f"- Safe actions: {', '.join(lane.get('safe_actions', []))}")
        lines.append(f"- Approval required: {', '.join(lane.get('approval_required', []))}")
        lines.append("")
    lines.extend(["## Safety Note", "", report["safety_note"], ""])
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy life opportunity encyclopedia report missing; run generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        if json.dumps(existing, indent=2, sort_keys=True) + "\n" != rendered:
            raise SystemExit("Buddy life opportunity encyclopedia report stale; run generator")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(
        "life_opportunity_encyclopedia_ready=True lanes={lanes} bots={bots} devices={devices}".format(
            lanes=summary["resource_lanes"],
            bots=summary["bot_count"],
            devices=summary["device_surfaces"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
