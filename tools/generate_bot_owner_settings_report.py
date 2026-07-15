#!/usr/bin/env python3
"""Generate governed business-owner settings for every DreamCo bot."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "bot_owner_settings_system.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
PRODUCTION_APPROVAL_PACKETS_FILE = ROOT / "reports" / "production_approval_packets.json"
OUTPUT_JSON = ROOT / "reports" / "bot_owner_settings_report.json"
OUTPUT_MD = ROOT / "reports" / "BOT_OWNER_SETTINGS_REPORT.md"


HIGH_RISK_TERMS = (
    "payment", "payout", "invoice", "trading", "trade", "crypto", "loan", "credit",
    "legal", "tax", "medical", "health", "security", "defense", "fraud", "compliance",
    "candidate", "hiring", "background", "personal data", "credential", "deploy",
)


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def words(value):
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def risk_hint(bot, approval_slugs):
    slug = str(bot.get("slug") or bot.get("id") or "")
    if slug in approval_slugs:
        return "high"
    searchable = " ".join(
        str(bot.get(key) or "")
        for key in ("name", "division", "category", "description")
    ).lower()
    for capability in bot.get("capabilities") or []:
        searchable += f" {capability}".lower()
    return "high" if any(term in searchable for term in HIGH_RISK_TERMS) else "standard"


def setting_defaults(config):
    return {setting["id"]: setting["default"] for setting in config.get("global_settings", [])}


def build_bot_settings(bot, config, approval_slugs):
    slug = bot.get("slug") or bot.get("id")
    risk = risk_hint(bot, approval_slugs)
    settings = setting_defaults(config)
    controls = {
        "bot_enabled": True,
        "safe_mode_enabled": True,
        "business_owner_mode_enabled": True,
        "contract_discovery_enabled": True,
        "data_package_enabled": True,
        "people_lookup_enabled": True,
        "sandbox_testing_enabled": True,
        "client_outreach_enabled": False,
        "paid_actions_enabled": False,
        "production_deploy_enabled": False,
        "money_movement_enabled": False,
        "third_party_account_actions_enabled": False,
    }
    if risk == "high":
        settings["business_owner_mode"] = True
        settings["sandbox_mode"] = True
        settings["contract_discovery"] = True
        settings["data_package_mode"] = True
        settings["people_lookup_safe_mode"] = True

    return {
        "slug": slug,
        "name": bot.get("name") or words(slug).title(),
        "division": bot.get("division") or "DreamCo",
        "category": bot.get("category") or "business",
        "risk_hint": risk,
        "business_owner_status": "enabled_safe_mode",
        "previously_blocked_live_actions": risk == "high",
        "safe_work_unblocked": True,
        "live_actions_require_approval": True,
        "settings": settings,
        "controls": controls,
        "permission_groups": config.get("permission_groups", []),
        "always_require_approval": config.get("always_require_approval", []),
        "dashboard_status": "ready_for_actions_page_settings",
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    approval_packets = read_json(PRODUCTION_APPROVAL_PACKETS_FILE, {})
    approval_slugs = {
        packet.get("slug")
        for packet in approval_packets.get("packets", [])
        if packet.get("slug")
    }
    bots = registry.get("bots", [])
    bot_settings = [build_bot_settings(bot, config, approval_slugs) for bot in bots]
    risk_counts = Counter(item["risk_hint"] for item in bot_settings)
    division_counts = Counter(item["division"] for item in bot_settings)

    high_risk = risk_counts.get("high", 0)
    summary = {
        "bot_count": len(bots),
        "bots_with_owner_settings": len(bot_settings),
        "business_owner_enabled_bots": sum(1 for item in bot_settings if item["controls"]["business_owner_mode_enabled"]),
        "safe_mode_enabled_bots": sum(1 for item in bot_settings if item["controls"]["safe_mode_enabled"]),
        "high_risk_bots": high_risk,
        "high_risk_bots_unblocked_for_safe_work": sum(
            1 for item in bot_settings if item["risk_hint"] == "high" and item["safe_work_unblocked"]
        ),
        "live_action_approval_required_bots": sum(1 for item in bot_settings if item["live_actions_require_approval"]),
        "settings_controls_ready": len(config.get("on_off_controls", [])),
        "permission_groups_ready": len(config.get("permission_groups", [])),
        "guardrails_ready": len(config.get("guardrails", [])),
        "all_bots_have_on_off_controls": len(bot_settings) == len(bots),
    }

    return {
        "schema": "dreamco.bot_owner_settings_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": summary,
        "global_settings": config.get("global_settings", []),
        "permission_groups": config.get("permission_groups", []),
        "on_off_controls": config.get("on_off_controls", []),
        "always_require_approval": config.get("always_require_approval", []),
        "guardrails": config.get("guardrails", []),
        "risk_breakdown": dict(risk_counts),
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(12)
        ],
        "dashboard_sample": bot_settings[:16],
        "next_actions": [
            "Connect Actions page switches to persisted owner approvals before enabling live actions.",
            "Keep high-risk bots business-owner enabled in safe mode while live actions remain approval-only.",
            "Add audit entries when an owner changes any live-action setting.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Bot Owner Settings Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bots with owner settings: {summary['bots_with_owner_settings']} / {summary['bot_count']}",
        f"- Business-owner enabled bots: {summary['business_owner_enabled_bots']}",
        f"- Safe-mode enabled bots: {summary['safe_mode_enabled_bots']}",
        f"- High-risk bots: {summary['high_risk_bots']}",
        f"- High-risk bots unblocked for safe work: {summary['high_risk_bots_unblocked_for_safe_work']}",
        f"- Live-action approval required bots: {summary['live_action_approval_required_bots']}",
        f"- Settings controls ready: {summary['settings_controls_ready']}",
        "",
        "## Guardrails",
        "",
    ]
    for guardrail in report["guardrails"]:
        lines.append(f"- {guardrail}")
    lines.extend(["", "## Always Require Approval", ""])
    for gate in report["always_require_approval"]:
        lines.append(f"- {gate}")
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("bot owner settings report is stale; run tools/generate_bot_owner_settings_report.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("bot owner settings report is stale; run tools/generate_bot_owner_settings_report.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"bots={report['summary']['bots_with_owner_settings']} "
        f"safe_mode={report['summary']['safe_mode_enabled_bots']} "
        f"high_risk_unblocked={report['summary']['high_risk_bots_unblocked_for_safe_work']}"
    )


if __name__ == "__main__":
    main()
