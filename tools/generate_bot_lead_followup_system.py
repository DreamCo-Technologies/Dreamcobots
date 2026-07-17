#!/usr/bin/env python3
"""Generate per-bot lead generation, follow-up, and source-quality packets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "bot_lead_followup_system.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "reports" / "bot_lead_followup_system.json"
OUTPUT_MD = ROOT / "reports" / "BOT_LEAD_FOLLOWUP_SYSTEM.md"


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def words(value: Any) -> str:
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def choose_api_categories(bot: dict[str, Any], config: dict[str, Any]) -> list[str]:
    text = f"{bot.get('division') or ''} {bot.get('category') or ''} {bot.get('name') or ''} {bot.get('slug') or ''}".lower()
    base = ["forms", "webhooks", "analytics", "crm"]
    if any(term in text for term in ["sales", "market", "content", "influence", "customer"]):
        base.extend(["email_marketing_after_approval", "calendar_booking_after_approval", "app_store_metadata"])
    if any(term in text for term in ["legal", "construction", "transport", "education", "health", "government"]):
        base.extend(["government_procurement", "grants", "business_registry", "job_and_contract_boards"])
    if any(term in text for term in ["real", "local", "food", "retail", "service"]):
        base.extend(["maps_and_local_business", "business_registry", "domain_and_dns"])
    if any(term in text for term in ["finance", "payment", "stripe", "loan"]):
        base.extend(["payments_after_approval", "business_registry", "analytics"])
    if any(term in text for term in ["app", "code", "software", "data", "ai"]):
        base.extend(["app_store_metadata", "search_console_or_site_analytics_after_approval", "support_ticketing"])

    allowed = set(config.get("useful_api_categories", []))
    chosen: list[str] = []
    for item in base:
        if item in allowed and item not in chosen:
            chosen.append(item)
    return chosen[:8]


def build_lead_packet(bot: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    slug = bot.get("slug") or bot.get("id")
    name = bot.get("name") or words(slug).title()
    division = bot.get("division") or "DreamCo"
    category = bot.get("category") or "business"
    api_categories = choose_api_categories(bot, config)
    lead_problem = (
        f"Find qualified {words(category).lower()} leads for {name} in {division} where the bot can "
        "solve a real problem, save time, reduce cost, or create measurable value."
    )
    return {
        "slug": slug,
        "name": name,
        "division": division,
        "category": category,
        "controller": config.get("controller", {}),
        "lead_generator": {
            "status": "ready_for_safe_lead_research",
            "problem_focus": lead_problem,
            "pipeline": config.get("lead_pipeline", []),
            "source_quality_policy": {
                "minimum_source_score_to_use": config.get("source_quality_policy", {}).get("minimum_source_score_to_use"),
                "score_factors": config.get("source_quality_policy", {}).get("source_score_factors", []),
                "allowed_source_types": config.get("source_quality_policy", {}).get("allowed_source_types", []),
                "low_value_or_blocked_by_default": config.get("source_quality_policy", {}).get("low_value_or_blocked_by_default", []),
            },
            "lead_score_fields": [
                "category_fit",
                "buyer_intent",
                "problem_urgency",
                "budget_signal",
                "reachable_decision_maker",
                "permission_basis",
                "privacy_risk",
                "expected_value",
            ],
        },
        "followup_system": {
            "status": "draft_only_until_approval",
            "cadence": config.get("followup_system", {}).get("cadence", []),
            "safe_outputs": config.get("followup_system", {}).get("safe_outputs", []),
            "blocked_without_approval": config.get("followup_system", {}).get("blocked_without_approval", []),
            "bot_specific_followup_prompt": (
                f"Draft a helpful, non-spam follow-up sequence for {name} that explains the specific {division} "
                "problem, shows proof, asks permission before contact, and stops before sending."
            ),
        },
        "useful_api_study_plan": {
            "status": "ready_to_study_useful_apis",
            "api_categories": api_categories,
            "reject_noise_rule": config.get("source_quality_policy", {}).get("api_study_rule", ""),
            "study_outputs": [
                "api_or_source_name",
                "category_fit",
                "buyer_intent_signal",
                "terms_notes",
                "privacy_risk",
                "cost_notes",
                "sample_safe_use",
                "decision_keep_or_reject",
            ],
        },
        "blocked_source_filter": config.get("source_quality_policy", {}).get("low_value_or_blocked_by_default", []),
        "twenty_four_hour_cycle": {
            **config.get("24_hour_cycle", {}),
            "bot_specific_cycle_prompt": (
                f"Every safe cycle, {name} should study one useful source/API, find lead candidates without contact, "
                "score them, draft follow-ups, prepare proof, and request approval before live outreach."
            ),
        },
        "codex_final_judge_packet": {
            "required": True,
            "checks": [
                "source_quality_score",
                "blocked_source_filter_passed",
                "no_live_outreach",
                "no_private_social_scraping",
                "useful_api_fit",
                "followup_is_helpful_not_spam",
                "owner_approval_needed_for_live_contact",
            ],
            "allowed_labels": ["approved_for_sandbox", "needs_more_evidence", "owner_approval_required", "blocked_risky"],
        },
        "owner_approval_packet": {
            "required_for_live_contact": True,
            "approval_gates": config.get("approval_gates", []),
        },
    }


def build_report() -> dict[str, Any]:
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    packets = [build_lead_packet(bot, config) for bot in bots]
    api_counter = Counter(api for packet in packets for api in packet["useful_api_study_plan"]["api_categories"])
    division_counter = Counter(packet["division"] for packet in packets)

    summary = {
        "bot_count": len(bots),
        "bots_with_lead_generator": len(packets),
        "bots_with_followup_system": len(packets),
        "bots_with_useful_api_study_plan": len(packets),
        "bots_with_blocked_source_filter": len(packets),
        "bots_with_24_hour_lead_cycle": len(packets),
        "codex_final_judge_required": True,
        "owner_approval_required_for_live_contact": True,
        "allowed_source_types": len(config.get("source_quality_policy", {}).get("allowed_source_types", [])),
        "blocked_source_types": len(config.get("source_quality_policy", {}).get("low_value_or_blocked_by_default", [])),
        "useful_api_categories": len(config.get("useful_api_categories", [])),
        "approval_gates": len(config.get("approval_gates", [])),
        "all_bots_have_lead_followup_system": len(packets) == len(bots) and len(bots) > 0,
        "live_outreach_blocked_without_approval": True,
    }

    return {
        "schema": "dreamco.bot_lead_followup_system_report.v1",
        "generated_at": utc_now(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": summary,
        "controller": config.get("controller", {}),
        "lead_pipeline": config.get("lead_pipeline", []),
        "followup_system": config.get("followup_system", {}),
        "source_quality_policy": config.get("source_quality_policy", {}),
        "useful_api_categories": config.get("useful_api_categories", []),
        "approval_gates": config.get("approval_gates", []),
        "top_api_categories": [{"api_category": api, "bot_count": count} for api, count in api_counter.most_common(12)],
        "top_divisions": [{"division": division, "bot_count": count} for division, count in division_counter.most_common(12)],
        "dashboard_sample": packets[:15],
        "bots": packets,
        "next_actions": [
            "Connect dashboard controls to show each bot's lead generator, follow-up drafts, and source-quality score.",
            "Keep all outreach draft-only until owner approval is recorded.",
            "Reject low-value or risky sources by default unless a reviewed business case approves them.",
            "Run this report in the local aggressive runner so lead/follow-up plans stay fresh without paid GitHub minutes.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Bot Lead Follow-Up System",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bots with lead generator: {summary['bots_with_lead_generator']} / {summary['bot_count']}",
        f"- Bots with follow-up system: {summary['bots_with_followup_system']}",
        f"- Bots with useful API study plan: {summary['bots_with_useful_api_study_plan']}",
        f"- Bots with blocked source filter: {summary['bots_with_blocked_source_filter']}",
        f"- Bots with 24-hour lead cycle: {summary['bots_with_24_hour_lead_cycle']}",
        f"- Codex final judge required: {summary['codex_final_judge_required']}",
        f"- Owner approval required for live contact: {summary['owner_approval_required_for_live_contact']}",
        f"- Live outreach blocked without approval: {summary['live_outreach_blocked_without_approval']}",
        "",
        "## Blocked Or Low-Value Sources By Default",
        "",
    ]
    for source in report["source_quality_policy"].get("low_value_or_blocked_by_default", []):
        lines.append(f"- {source}")
    lines.extend(["", "## Useful API Categories", ""])
    for category in report["useful_api_categories"]:
        lines.append(f"- {category}")
    lines.extend(["", "## Approval Gates", ""])
    for gate in report["approval_gates"]:
        lines.append(f"- {gate}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("bot lead follow-up report missing; run tools/generate_bot_lead_followup_system.py")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if rendered != existing_rendered:
            raise SystemExit("bot lead follow-up report stale; run tools/generate_bot_lead_followup_system.py")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(
        "lead_followup_ready={ready} bots={bots} api_categories={apis} blocked_sources={blocked}".format(
            ready=summary["all_bots_have_lead_followup_system"],
            bots=summary["bot_count"],
            apis=summary["useful_api_categories"],
            blocked=summary["blocked_source_types"],
        )
    )
    return 0 if summary["all_bots_have_lead_followup_system"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
