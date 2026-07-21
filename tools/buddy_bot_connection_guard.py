#!/usr/bin/env python3
"""Verify every bot is connected to Buddy, testable, and resource-backed."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = ROOT / "reports/buddy_capability_inventory.json"
RESOURCE_INDEX_FILE = ROOT / "config/generated/system_libraries/resources.json"
REPORT_JSON = ROOT / "reports/buddy_bot_connection_report.json"
REPORT_MD = ROOT / "reports/BUDDY_BOT_CONNECTION_REPORT.md"


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


def inventory_bots() -> list[dict[str, Any]]:
    inventory = read_json(INVENTORY_FILE, {})
    bots = inventory.get("bots") or []
    if bots:
        return bots
    return inventory.get("buddy_bots") or []


def resource_entries_by_slug() -> dict[str, dict[str, Any]]:
    index = read_json(RESOURCE_INDEX_FILE, {})
    by_slug: dict[str, dict[str, Any]] = {}
    for shard_name in index.get("shards", []):
        shard_path = ROOT / shard_name
        shard = read_json(shard_path, {})
        for entry in shard.get("entries", []):
            slug = entry.get("bot_slug") or entry.get("bot_id")
            if slug:
                by_slug[str(slug)] = entry
    return by_slug


def test_packet_ready(bot: dict[str, Any]) -> bool:
    return all(
        [
            bot.get("slug"),
            bot.get("name"),
            bot.get("test_state"),
            bot.get("build_state"),
        ]
    )


def buddy_routing_ready(bot: dict[str, Any]) -> bool:
    return all(
        [
            bot.get("slug"),
            bot.get("name"),
            bot.get("division"),
            bot.get("description") or bot.get("capabilities"),
        ]
    )


def build_report() -> dict[str, Any]:
    bots = inventory_bots()
    resources = resource_entries_by_slug()
    failures: list[dict[str, Any]] = []
    ready_rows: list[dict[str, Any]] = []

    for bot in bots:
        slug = str(bot.get("slug") or "")
        resource = resources.get(slug)
        resource_count = int(resource.get("resource_count") or 0) if resource else 0
        has_100_resources = resource_count >= 100
        has_categories = len(resource.get("resource_categories", [])) >= 100 if resource else False
        routing_ready = buddy_routing_ready(bot)
        packet_ready = test_packet_ready(bot)
        actions_ready = routing_ready and packet_ready
        ready = actions_ready and has_100_resources and has_categories
        row = {
            "slug": slug,
            "name": bot.get("name"),
            "division": bot.get("division"),
            "buddy_routing_ready": routing_ready,
            "actions_test_packet_ready": packet_ready,
            "actions_page_testable": actions_ready,
            "custom_resource_count": resource_count,
            "custom_resources_ready": has_100_resources and has_categories,
            "tests": bot.get("tests", []),
            "test_count": bot.get("test_count", 0),
            "test_state": bot.get("test_state"),
            "build_state": bot.get("build_state"),
            "risk_hint": bot.get("risk_hint", "standard"),
            "ready": ready,
        }
        ready_rows.append(row)
        if not ready:
            failures.append(
                {
                    "slug": slug,
                    "name": bot.get("name"),
                    "issues": [
                        label
                        for label, ok in [
                            ("missing Buddy routing fields", routing_ready),
                            ("missing Actions test packet fields", packet_ready),
                            ("missing 100 customized resources", has_100_resources),
                            ("missing 100 resource categories", has_categories),
                        ]
                        if not ok
                    ],
                }
            )

    connected = sum(1 for row in ready_rows if row["buddy_routing_ready"])
    testable = sum(1 for row in ready_rows if row["actions_page_testable"])
    resource_ready = sum(1 for row in ready_rows if row["custom_resources_ready"])
    report = {
        "schema": "dreamco.buddy_bot_connection_guard.v1",
        "generated_at": utc_now(),
        "source_inventory": rel(INVENTORY_FILE),
        "source_resources": rel(RESOURCE_INDEX_FILE),
        "summary": {
            "all_bots_connected_to_buddy": connected == len(bots) and len(bots) > 0,
            "all_bots_testable_from_actions_page": testable == len(bots) and len(bots) > 0,
            "all_bots_have_custom_resources": resource_ready == len(bots) and len(bots) > 0,
            "all_bots_ready": len(failures) == 0 and len(bots) > 0,
            "bot_count": len(bots),
            "buddy_connected_bots": connected,
            "actions_page_testable_bots": testable,
            "custom_resource_ready_bots": resource_ready,
            "failed_bots": len(failures),
            "resources_per_bot_required": 100,
        },
        "failures": failures[:100],
        "bots": ready_rows,
        "actions_page_contract": {
            "test_command": "python3 tools/run_generated_bot_smoke.py",
            "mode": "sandbox_only",
            "approval_for_high_risk": "buddy_money_help_approval_required_before_live_actions",
            "selection_surface": "Actions page Buddy and bot test catalog",
        },
    }
    return report


def write_reports(report: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    lines = [
        "# Buddy Bot Connection Report",
        "",
        f"- Generated: {report['generated_at']}",
        f"- All bots connected to Buddy: {summary['all_bots_connected_to_buddy']}",
        f"- All bots testable from Actions page: {summary['all_bots_testable_from_actions_page']}",
        f"- All bots have custom resources: {summary['all_bots_have_custom_resources']}",
        f"- Bot count: {summary['bot_count']}",
        f"- Buddy-connected bots: {summary['buddy_connected_bots']}",
        f"- Actions-page testable bots: {summary['actions_page_testable_bots']}",
        f"- Custom resource-ready bots: {summary['custom_resource_ready_bots']}",
        f"- Failed bots: {summary['failed_bots']}",
        "",
        "## Actions Page Contract",
        "",
        f"- Test command: `{report['actions_page_contract']['test_command']}`",
        f"- Mode: `{report['actions_page_contract']['mode']}`",
        f"- High-risk approval: `{report['actions_page_contract']['approval_for_high_risk']}`",
        "",
    ]
    if report["failures"]:
        lines.extend(["## Failures", ""])
        for failure in report["failures"]:
            lines.append(f"- `{failure['slug']}`: {', '.join(failure['issues'])}")
    else:
        lines.extend(["## Failures", "", "- None."])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_reports(report)
    summary = report["summary"]
    print(
        "all_bots_ready={ready} bots={bots} connected={connected} testable={testable} resources={resources} failures={failures}".format(
            ready=summary["all_bots_ready"],
            bots=summary["bot_count"],
            connected=summary["buddy_connected_bots"],
            testable=summary["actions_page_testable_bots"],
            resources=summary["custom_resource_ready_bots"],
            failures=summary["failed_bots"],
        )
    )
    return 0 if summary["all_bots_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
