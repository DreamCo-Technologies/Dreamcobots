#!/usr/bin/env python3
"""Generate Buddy's unified governed bot workforce manifest."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MASTER_REGISTRY = ROOT / "config" / "master_bot_registry.json"
CONNECTION_REPORT = ROOT / "reports" / "buddy_bot_connection_report.json"
OWNER_REPORT = ROOT / "reports" / "bot_owner_settings_report.json"
SCALING_REPORT = ROOT / "reports" / "dreamco_24_hour_scaling_report.json"
MODEL_REGISTRY = ROOT / "config" / "buddy_user_model_choice_registry.json"
SAFE_CODE_BOTS = ROOT / "config" / "buddy_safe_codex_code_bots.json"
CAPABILITY_LIBRARY = ROOT / "config" / "bot_capabilities_library.json"
END_TO_END_READINESS = ROOT / "config" / "generated" / "bot_end_to_end_readiness" / "index.json"
OUTPUT_JSON = ROOT / "config" / "buddy_unified_bot_workforce.json"
OUTPUT_REPORT = ROOT / "reports" / "BUDDY_UNIFIED_BOT_WORKFORCE.md"


CODE_TERMS = ("code", "debug", "api", "workflow", "sandbox", "test", "deploy", "import", "builder")
MONEY_TERMS = (
    "money",
    "revenue",
    "sales",
    "lead",
    "contract",
    "grant",
    "loan",
    "payment",
    "pricing",
    "market",
    "customer",
)
MEDIA_TERMS = ("image", "voice", "video", "music", "photo", "3d", "game", "simulation", "course")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def slug_text(bot: dict[str, Any]) -> str:
    parts = [
        bot.get("slug"),
        bot.get("name"),
        bot.get("division"),
        bot.get("category"),
        bot.get("description"),
    ]
    for capability in bot.get("capabilities") or []:
        if isinstance(capability, dict):
            parts.append(capability.get("label") or capability.get("intent"))
        else:
            parts.append(str(capability))
    return " ".join(str(part or "") for part in parts).lower()


def work_lanes_for(bot: dict[str, Any]) -> list[str]:
    text = slug_text(bot)
    lanes = ["research", "planning", "capability_library", "sandbox_training"]
    if any(term in text for term in CODE_TERMS):
        lanes.extend(["code_build", "debug_repair"])
    if any(term in text for term in MONEY_TERMS):
        lanes.extend(["opportunity_discovery", "lead_followup_drafts"])
    if any(term in text for term in MEDIA_TERMS):
        lanes.extend(["creative_studio", "media_rights_review"])
    if str(bot.get("safety", {}).get("risk_level") or "").lower() == "high":
        lanes.append("approval_packet")
    return list(dict.fromkeys(lanes))


def safe_actions_for(bot: dict[str, Any]) -> list[str]:
    division = bot.get("division") or "DreamCo"
    category = bot.get("category") or "general"
    return [
        f"study {division} competitors and customer problems",
        f"draft {category} app, bot, workflow, or service ideas",
        "build sandbox-only prototypes and bootcamp tests",
        "write capability, API, webhook, workflow, and skill library entries",
        "compare optional AI models and recommend the best low-cost route",
        "prepare approval packets for live customer, money, account, or deploy actions",
    ]


def build_manifest() -> dict[str, Any]:
    registry = read_json(MASTER_REGISTRY, {})
    connection = read_json(CONNECTION_REPORT, {})
    owner = read_json(OWNER_REPORT, {})
    scaling = read_json(SCALING_REPORT, {})
    models = read_json(MODEL_REGISTRY, {})
    safe_code = read_json(SAFE_CODE_BOTS, {})
    capability_library = read_json(CAPABILITY_LIBRARY, {})
    readiness = read_json(END_TO_END_READINESS, {})

    bots = registry.get("bots", [])
    divisions = Counter(str(bot.get("division") or "Unassigned") for bot in bots)
    risks = Counter(str(bot.get("safety", {}).get("risk_level") or "standard") for bot in bots)
    lanes = Counter()
    workforce = []

    for bot in bots:
        bot_lanes = work_lanes_for(bot)
        lanes.update(bot_lanes)
        high_risk = str(bot.get("safety", {}).get("risk_level") or "").lower() == "high"
        workforce.append(
            {
                "slug": bot.get("slug") or bot.get("id"),
                "name": bot.get("name"),
                "emoji": bot.get("emoji") or "\U0001f916",
                "division": bot.get("division"),
                "category": bot.get("category"),
                "risk_level": bot.get("safety", {}).get("risk_level") or "standard",
                "status": "active_supervised",
                "buddy_role": "business_owner_bot",
                "safe_work_enabled": True,
                "previously_blocked_or_high_risk": high_risk,
                "live_actions_require_approval": True,
                "money_goal_mode": "practice_and_prepare_opportunities_without_unapproved_money_movement",
                "optional_model_routing": True,
                "default_execution": "local_first_sandbox_first",
                "work_lanes": bot_lanes,
                "safe_actions": safe_actions_for(bot),
                "dashboard_url": bot.get("dashboard_url"),
                "prospectus_url": bot.get("prospectus_url"),
            }
        )

    council = {
        "buddy_final_judge": True,
        "user_model_choice_enabled": True,
        "default_choice": models.get("default_choice", "buddy_recommended"),
        "optional_model_count": len(models.get("choices", [])),
        "policy": [
            "Use local deterministic tools first for scans, tests, JSON, TypeScript, Python imports, and repo repair.",
            "Let users choose other model families when configured, but keep Buddy as the router and final safety judge.",
            "No paid model call, live outreach, money movement, legal filing, public deployment, or account mutation runs without approval.",
            "Every model recommendation must include strengths, limits, likely cost posture, and test evidence before production use.",
        ],
    }

    operating_system = {
        "mode": "one_big_buddy_governed_system",
        "default_runtime": "continuous_supervised_safe_mode",
        "aggressive_mode": scaling.get("aggressive_mode", {}),
        "approved_safe_autonomy": [
            "research",
            "learning",
            "capability mapping",
            "sandbox prototype building",
            "workflow generation",
            "API and webhook mock testing",
            "code issue diagnosis",
            "local repair planning",
            "client prospectus drafting",
            "opportunity discovery drafts",
        ],
        "blocked_until_approval": scaling.get("always_blocked_without_owner_approval", []),
        "storage_policy": "Store only useful summaries, source evidence, test results, approvals, compact fix recipes, and client deliverables.",
    }

    summary = {
        "bot_count": len(bots),
        "division_count": len(divisions),
        "high_risk_or_previously_blocked_safe_work_enabled": sum(
            1 for item in workforce if item["previously_blocked_or_high_risk"] and item["safe_work_enabled"]
        ),
        "all_bots_safe_work_enabled": all(item["safe_work_enabled"] for item in workforce),
        "all_bots_live_actions_approval_gated": all(item["live_actions_require_approval"] for item in workforce),
        "buddy_connected_bots": connection.get("summary", {}).get("buddy_connected_bots", 0),
        "actions_page_testable_bots": connection.get("summary", {}).get("actions_page_testable_bots", 0),
        "owner_settings_bots": owner.get("summary", {}).get("bots_with_owner_settings", 0),
        "safe_code_specialists": safe_code.get("total_code_bots", 0),
        "optional_model_choices": len(models.get("choices", [])),
        "capability_target_per_bot": capability_library.get("capability_target_per_bot", 100),
        "readiness_bots_or_systems": readiness.get("totals", {}).get("bots", 0),
    }

    return {
        "schema": "dreamco.buddy_unified_bot_workforce.v1",
        "generated_at": utc_now(),
        "mission": "Fit every DreamCo bot into one Buddy-governed workforce where each bot can do safe autonomous work, learn its category, build sandbox systems, and prepare money-making opportunities with approval gates.",
        "summary": summary,
        "operating_system": operating_system,
        "model_council": council,
        "work_lanes": dict(sorted(lanes.items())),
        "division_coverage": dict(sorted(divisions.items())),
        "risk_coverage": dict(sorted(risks.items())),
        "sample_bots": workforce[:40],
        "all_bot_workforce": workforce,
        "source_files": {
            "master_registry": str(MASTER_REGISTRY.relative_to(ROOT)),
            "connection_report": str(CONNECTION_REPORT.relative_to(ROOT)),
            "owner_settings_report": str(OWNER_REPORT.relative_to(ROOT)),
            "scaling_report": str(SCALING_REPORT.relative_to(ROOT)),
            "model_registry": str(MODEL_REGISTRY.relative_to(ROOT)),
            "safe_code_bots": str(SAFE_CODE_BOTS.relative_to(ROOT)),
            "capability_library": str(CAPABILITY_LIBRARY.relative_to(ROOT)),
            "end_to_end_readiness": str(END_TO_END_READINESS.relative_to(ROOT)),
        },
    }


def write_report(manifest: dict[str, Any]) -> None:
    summary = manifest["summary"]
    lines = [
        "# Buddy Unified Bot Workforce",
        "",
        manifest["mission"],
        "",
        "## Summary",
        "",
        f"- Bots fitted into one system: {summary['bot_count']}",
        f"- Divisions covered: {summary['division_count']}",
        f"- High-risk or previously blocked bots enabled for safe work: {summary['high_risk_or_previously_blocked_safe_work_enabled']}",
        f"- Live-action approval gated bots: {summary['bot_count'] if summary['all_bots_live_actions_approval_gated'] else 'review required'}",
        f"- Buddy-connected bots: {summary['buddy_connected_bots']}",
        f"- Actions-page testable bots: {summary['actions_page_testable_bots']}",
        f"- Safe code specialists: {summary['safe_code_specialists']}",
        f"- Optional model choices: {summary['optional_model_choices']}",
        "",
        "## Operating Rules",
        "",
    ]
    for rule in manifest["model_council"]["policy"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Safe Autonomous Work", ""])
    for action in manifest["operating_system"]["approved_safe_autonomy"]:
        lines.append(f"- {action}")
    lines.extend(["", "## Work Lanes", ""])
    for lane, count in manifest["work_lanes"].items():
        lines.append(f"- {lane}: {count}")
    OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy unified bot workforce manifest is missing; run generator.")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = manifest["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Buddy unified bot workforce manifest is stale; run generator.")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_report(manifest)
    print(
        "bots={bot_count} high_risk_safe={high_risk_or_previously_blocked_safe_work_enabled} models={optional_model_choices}".format(
            **manifest["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
