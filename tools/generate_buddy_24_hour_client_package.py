#!/usr/bin/env python3
"""Generate Buddy's sellable 24-hour all-bot client package."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONNECTION_REPORT = ROOT / "reports" / "buddy_bot_connection_report.json"
OWNER_SETTINGS_REPORT = ROOT / "reports" / "bot_owner_settings_report.json"
SCALING_REPORT = ROOT / "reports" / "dreamco_24_hour_scaling_report.json"
SPECIALIZED_KNOWLEDGE_REPORT = ROOT / "reports" / "specialized_bot_knowledge_report.json"
APP_FOUNDRY_REPORT = ROOT / "reports" / "app_foundry_readiness.json"
OUTPUT_JSON = ROOT / "reports" / "buddy_24_hour_client_package.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_24_HOUR_CLIENT_PACKAGE.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_package() -> dict[str, Any]:
    connection = read_json(CONNECTION_REPORT, {})
    owner = read_json(OWNER_SETTINGS_REPORT, {})
    scaling = read_json(SCALING_REPORT, {})
    knowledge = read_json(SPECIALIZED_KNOWLEDGE_REPORT, {})
    foundry = read_json(APP_FOUNDRY_REPORT, {})

    bots = connection.get("bots", [])
    owner_summary = owner.get("summary", {})
    scaling_summary = scaling.get("summary", {})
    divisions = Counter(str(bot.get("division") or "Unassigned") for bot in bots)
    risk = Counter(str(bot.get("risk_hint") or "standard") for bot in bots)

    cycles = scaling.get("daily_cycles", [])
    operating_lanes = [
        {
            "id": "research_lane",
            "label": "Research and opportunity lane",
            "purpose": "Study public markets, competitors, resources, client problems, and app opportunities.",
            "safe_outputs": ["source-backed notes", "problem statements", "opportunity briefs", "client-ready summaries"],
            "approval_required": ["private data collection", "customer contact", "paid research tools"],
        },
        {
            "id": "build_lane",
            "label": "Bot, app, game, course, and simulation build lane",
            "purpose": "Turn approved ideas into local-first build plans, sandbox prototypes, tests, and demo packets.",
            "safe_outputs": ["implementation plans", "sandbox prototypes", "test checklists", "pull-request packets"],
            "approval_required": ["production deployment", "third-party account changes", "credential changes"],
        },
        {
            "id": "client_package_lane",
            "label": "Client package and prospectus lane",
            "purpose": "Prepare sellable bot-system packages with demos, value props, pricing drafts, and onboarding tasks.",
            "safe_outputs": ["prospectus pages", "demo scripts", "package tiers", "onboarding checklists"],
            "approval_required": ["public publishing", "live payment links", "contract signing"],
        },
        {
            "id": "quality_lane",
            "label": "Debug, test, and reliability lane",
            "purpose": "Continuously refresh reports, run smoke checks, track failures, and keep only useful operational data.",
            "safe_outputs": ["failure reports", "test evidence", "quality gates", "storage budgets"],
            "approval_required": ["destructive repository actions", "merge to protected branches", "live API mutation"],
        },
    ]

    package_tiers = [
        {
            "id": "starter_showcase",
            "label": "Starter Showcase",
            "client_fit": "A client wants a professional demo of AI employees and one focused business system.",
            "included_bots": "up to 10 supervised bots",
            "runtime": "scheduled safe-mode cycles and manual approval gates",
            "deliverables": ["dashboard demo", "prospectus packet", "sandbox tests", "weekly improvement plan"],
        },
        {
            "id": "department_os",
            "label": "Department OS",
            "client_fit": "A client wants a department-level AI workforce for sales, ops, content, support, or finance.",
            "included_bots": "up to 100 supervised bots",
            "runtime": "24-hour safe-mode lanes with daily review queue",
            "deliverables": ["division dashboard", "workflow library", "API/webhook sandbox", "approval packet queue"],
        },
        {
            "id": "company_builder",
            "label": "Company Builder",
            "client_fit": "A client wants DreamCo to help build, test, package, and grow an AI-powered business.",
            "included_bots": "all relevant DreamCo bots under Buddy routing",
            "runtime": "24-hour supervised research/build/test/package/growth/review cycles",
            "deliverables": ["business launch packet", "app/game/course/simulation build lane", "contract discovery", "client growth drafts"],
        },
    ]

    runtime_contract = {
        "mode": "continuous_supervised_safe_mode",
        "always_on_meaning": "Bots can continuously research, plan, draft, test, package, and report. Live customer, money, account, deploy, legal, medical, financial, or destructive actions stay approval-gated.",
        "queue_model": "Buddy assigns safe work packets to bots, stores useful outputs, summarizes failures, and returns approval packets for human review.",
        "data_policy": "Store only useful operational data, source evidence, test results, approvals, and client deliverables. Avoid private data unless the client supplies it or explicitly approves its use.",
        "client_safety_note": "This package is sellable as a supervised AI workforce and app-building operating system, not as uncontrolled autonomous money movement.",
    }

    sample_bots = [
        {
            "slug": bot.get("slug"),
            "name": bot.get("name"),
            "division": bot.get("division"),
            "runtime_state": "safe_mode_24_hour_ready",
            "buddy_connected": bot.get("buddy_routing_ready", False),
            "testable": bot.get("actions_page_testable", False),
            "resource_count": bot.get("custom_resource_count", 0),
            "risk_hint": bot.get("risk_hint", "standard"),
        }
        for bot in bots[:25]
    ]

    all_connected = connection.get("summary", {}).get("all_bots_connected_to_buddy", False)
    all_testable = connection.get("summary", {}).get("all_bots_testable_from_actions_page", False)
    all_resources = connection.get("summary", {}).get("all_bots_have_custom_resources", False)
    bot_count = int(connection.get("summary", {}).get("bot_count") or len(bots))

    return {
        "schema": "dreamco.buddy_24_hour_client_package.v1",
        "generated_at": utc_now(),
        "mission": "Package every DreamCo bot as a Buddy-connected supervised AI workforce that can run safe 24-hour improvement cycles for clients.",
        "sellable_positioning": "Buddy is the trusted control layer for AI employees that research, build, test, package, and improve business systems around the clock with human approval gates.",
        "summary": {
            "bot_count": bot_count,
            "buddy_connected_bots": connection.get("summary", {}).get("buddy_connected_bots", 0),
            "actions_page_testable_bots": connection.get("summary", {}).get("actions_page_testable_bots", 0),
            "custom_resource_ready_bots": connection.get("summary", {}).get("custom_resource_ready_bots", 0),
            "business_owner_enabled_bots": owner_summary.get("business_owner_enabled_bots", 0),
            "safe_mode_enabled_bots": owner_summary.get("safe_mode_enabled_bots", 0),
            "safe_24_hour_cycles": scaling_summary.get("cycles_defined", len(cycles)),
            "safe_automation_steps": scaling_summary.get("safe_automation_steps", 0),
            "approval_gates": scaling_summary.get("always_blocked_gates", 0),
            "specialized_knowledge_bots": knowledge.get("summary", {}).get("bot_count", 0),
            "app_foundry_lanes": foundry.get("summary", {}).get("creation_lanes", 0),
            "all_bots_connected_to_buddy": all_connected,
            "all_bots_testable": all_testable,
            "all_bots_resource_backed": all_resources,
            "client_package_ready": all_connected and all_testable and all_resources and bot_count >= 1200,
        },
        "runtime_contract": runtime_contract,
        "operating_lanes": operating_lanes,
        "daily_cycles": cycles,
        "package_tiers": package_tiers,
        "division_coverage": dict(sorted(divisions.items())),
        "risk_coverage": dict(sorted(risk.items())),
        "approval_boundaries": scaling.get("always_blocked_without_owner_approval", []),
        "client_deliverables": [
            "Buddy command dashboard",
            "bot workforce catalog",
            "division prospectus pages",
            "sandbox bootcamp tests",
            "API and webhook test library",
            "workflow and skill library",
            "daily scorecards",
            "approval packet queue",
            "client-ready demo scripts",
            "safe-mode operating policy",
        ],
        "sample_bots": sample_bots,
        "sources": {
            "buddy_connections": rel(CONNECTION_REPORT),
            "owner_settings": rel(OWNER_SETTINGS_REPORT),
            "24_hour_scaling": rel(SCALING_REPORT),
            "specialized_knowledge": rel(SPECIALIZED_KNOWLEDGE_REPORT),
            "app_foundry": rel(APP_FOUNDRY_REPORT),
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Buddy 24-Hour Client Package",
        "",
        report["mission"],
        "",
        "## Sellable Positioning",
        "",
        report["sellable_positioning"],
        "",
        "## Summary",
        "",
        f"- Bot count: {summary['bot_count']}",
        f"- Buddy-connected bots: {summary['buddy_connected_bots']}",
        f"- Actions-page testable bots: {summary['actions_page_testable_bots']}",
        f"- Custom resource-ready bots: {summary['custom_resource_ready_bots']}",
        f"- Business-owner enabled bots: {summary['business_owner_enabled_bots']}",
        f"- Safe-mode enabled bots: {summary['safe_mode_enabled_bots']}",
        f"- 24-hour cycles: {summary['safe_24_hour_cycles']}",
        f"- Safe automation steps: {summary['safe_automation_steps']}",
        f"- Approval gates: {summary['approval_gates']}",
        f"- Client package ready: {summary['client_package_ready']}",
        "",
        "## Runtime Contract",
        "",
    ]
    for key, value in report["runtime_contract"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Operating Lanes", ""])
    for lane in report["operating_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["purpose"])
        lines.append("")
        lines.append(f"- Safe outputs: {', '.join(lane['safe_outputs'])}")
        lines.append(f"- Approval required: {', '.join(lane['approval_required'])}")
        lines.append("")
    lines.extend(["## Package Tiers", ""])
    for tier in report["package_tiers"]:
        lines.append(f"- {tier['label']}: {tier['client_fit']} Includes {tier['included_bots']}.")
    lines.extend(["", "## Approval Boundaries", ""])
    for boundary in report["approval_boundaries"]:
        lines.append(f"- {boundary}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_package()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy 24-hour client package report is missing; run the generator.")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Buddy 24-hour client package report is stale; run the generator.")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(
        "client_package_ready={ready} bots={bots} connected={connected} testable={testable} cycles={cycles}".format(
            ready=summary["client_package_ready"],
            bots=summary["bot_count"],
            connected=summary["buddy_connected_bots"],
            testable=summary["actions_page_testable_bots"],
            cycles=summary["safe_24_hour_cycles"],
        )
    )
    return 0 if summary["client_package_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

