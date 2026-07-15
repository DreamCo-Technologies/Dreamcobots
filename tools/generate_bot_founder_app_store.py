#!/usr/bin/env python3
"""Generate DreamCo bot founder/app-store readiness packets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "bot_founder_app_store.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
SYSTEM_LIBRARY_INDEX_FILE = ROOT / "config" / "generated" / "system_libraries" / "index.json"
OUTPUT_JSON = ROOT / "reports" / "bot_founder_app_store_report.json"
OUTPUT_MD = ROOT / "reports" / "BOT_FOUNDER_APP_STORE_REPORT.md"


CATEGORY_MAP = {
    "coding-library": "developer_tools",
    "dreamco-system": "business_automation",
    "analytics": "data_and_analytics",
    "trading": "finance_and_payments",
    "investing": "finance_and_payments",
    "billing": "finance_and_payments",
    "payments": "finance_and_payments",
    "real-estate": "real_estate",
    "education": "education_and_courses",
    "gaming": "games_and_simulations",
    "marketing": "sales_and_marketing",
    "outreach": "sales_and_marketing",
    "growth": "sales_and_marketing",
    "security": "security_and_compliance",
    "compliance": "security_and_compliance",
    "content": "creative_media",
    "health": "health_and_wellness",
    "automation": "business_automation",
    "app": "websites_and_apps",
}


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def slug_text(value: str) -> str:
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def app_store_category(bot, config):
    category = str(bot.get("category") or "").lower()
    division = str(bot.get("division") or "").lower()
    for needle, target in CATEGORY_MAP.items():
        if needle in category or needle in division:
            return target
    categories = config.get("app_store_categories", [])
    return categories[0] if categories else "business_automation"


def bot_capability_labels(bot):
    labels = []
    for capability in bot.get("capabilities") or []:
        if isinstance(capability, dict):
            labels.append(capability.get("label") or capability.get("intent") or "capability")
        else:
            labels.append(str(capability))
    return labels


def founder_packet(bot, config):
    bot_name = bot.get("name") or slug_text(bot.get("slug"))
    division = bot.get("division") or "DreamCo"
    category = bot.get("category") or "business"
    app_category = app_store_category(bot, config)
    capability_labels = bot_capability_labels(bot)
    top_capabilities = capability_labels[:6]
    customer = f"{slug_text(category)} teams in {division}"
    problem = f"Help {customer} solve repeatable {slug_text(category)} work with less manual setup, better evidence, and safer automation."

    return {
        "bot_id": bot.get("id") or bot.get("slug"),
        "slug": bot.get("slug"),
        "name": bot_name,
        "emoji": bot.get("emoji", "🤖"),
        "division": division,
        "category": category,
        "app_store_category": app_category,
        "target_customer": customer,
        "customer_problem": problem,
        "competitor_study_plan": [
            "Map 5-10 public competitors or substitutes.",
            "Compare pricing, onboarding, features, integrations, proof, support, and trust signals.",
            "Capture public customer complaints and feature gaps without copying proprietary material.",
            "Turn gaps into a safer DreamCo differentiation angle.",
        ],
        "autonomous_app_concept": {
            "name": f"{bot_name} App",
            "type": app_category,
            "promise": f"A supervised DreamCo app that turns {bot_name} into a usable workflow, dashboard, or service.",
            "core_workflows": [
                "intake",
                "analysis",
                "sandbox_run",
                "recommendation",
                "approval_request",
                "evidence_log",
            ],
            "capability_seed": top_capabilities,
        },
        "revenue_model": {
            "primary": "subscription_or_project_fee",
            "secondary": ["setup_fee", "managed_service", "usage_add_on"],
            "blocked_claims": ["guaranteed income", "guaranteed customers", "risk-free automation"],
        },
        "marketing_plan": [
            "Create a plain-language app-store listing.",
            "Draft one landing page and demo script.",
            "Draft 3 educational posts and 3 outreach messages for owner review.",
            "Run customer interviews only after approval.",
        ],
        "customer_discovery_plan": [
            "Define one reachable customer segment.",
            "List public source URLs for problems and buying signals.",
            "Draft interview questions.",
            "Score leads without contacting them until approved.",
        ],
        "app_store_listing": {
            "title": f"{bot.get('emoji', '🤖')} {bot_name}",
            "subtitle": f"{division} app for {slug_text(category)} workflows.",
            "status": "draft_ready_for_owner_review",
            "proof_needed": ["sandbox demo", "test evidence", "pricing approval", "publish approval"],
        },
        "sandbox_test_plan": [
            "Run with mocked APIs and fake customer data.",
            "Verify no money movement, outreach, publishing, or live deployment happens in sandbox.",
            "Record inputs, outputs, failures, and next improvement.",
        ],
        "approval_gates": config.get("approval_gates", []),
        "daily_learning_loop": [
            "study public competitor changes",
            "collect customer problem evidence",
            "update app concept",
            "improve sandbox tests",
            "propose pull-request-safe changes",
        ],
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    library_index = read_json(SYSTEM_LIBRARY_INDEX_FILE, {})
    bots = registry.get("bots", [])
    packets = [founder_packet(bot, config) for bot in bots]
    category_counts = Counter(packet["app_store_category"] for packet in packets)
    division_counts = Counter(packet["division"] for packet in packets)

    summary = {
        "bot_count": len(bots),
        "founder_packets": len(packets),
        "bots_with_app_concept": sum(1 for packet in packets if packet.get("autonomous_app_concept")),
        "bots_with_competitor_study_plan": sum(1 for packet in packets if packet.get("competitor_study_plan")),
        "bots_with_revenue_model": sum(1 for packet in packets if packet.get("revenue_model")),
        "bots_with_marketing_plan": sum(1 for packet in packets if packet.get("marketing_plan")),
        "bots_with_customer_discovery_plan": sum(1 for packet in packets if packet.get("customer_discovery_plan")),
        "bots_with_app_store_listing": sum(1 for packet in packets if packet.get("app_store_listing")),
        "bots_with_sandbox_test_plan": sum(1 for packet in packets if packet.get("sandbox_test_plan")),
        "bots_blocked_from_live_actions_until_approval": len(packets),
        "app_store_categories": len(category_counts),
        "study_loops": len(config.get("founder_study_loops", [])),
        "approval_gates": len(config.get("approval_gates", [])),
        "system_library_bot_count": library_index.get("bot_count", 0),
    }

    return {
        "schema": "dreamco.bot_founder_app_store_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "source_registry": str(MASTER_REGISTRY_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "positioning": config.get("positioning", ""),
        "live_action_policy": config.get("live_action_policy", ""),
        "summary": summary,
        "founder_study_loops": config.get("founder_study_loops", []),
        "app_store_categories": [
            {"category": category, "bot_count": count}
            for category, count in category_counts.most_common()
        ],
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(15)
        ],
        "required_bot_founder_packet": config.get("required_bot_founder_packet", []),
        "approval_gates": config.get("approval_gates", []),
        "packets": packets,
        "dashboard_sample": packets[:12],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Bot Founder App Store Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bot founder packets: {summary['founder_packets']} / {summary['bot_count']}",
        f"- App concepts: {summary['bots_with_app_concept']}",
        f"- Competitor study plans: {summary['bots_with_competitor_study_plan']}",
        f"- Revenue models: {summary['bots_with_revenue_model']}",
        f"- Marketing plans: {summary['bots_with_marketing_plan']}",
        f"- Customer discovery plans: {summary['bots_with_customer_discovery_plan']}",
        f"- App-store listings: {summary['bots_with_app_store_listing']}",
        f"- Approval-gated bots: {summary['bots_blocked_from_live_actions_until_approval']}",
        "",
        "## Live Action Policy",
        "",
        report["live_action_policy"],
        "",
        "## Study Loops",
        "",
    ]
    for loop in report["founder_study_loops"]:
        lines.append(f"### {loop['label']}")
        lines.append("")
        lines.append(loop["purpose"])
        lines.append("")
        lines.append(f"- Outputs: {', '.join(loop.get('outputs', []))}")
        lines.append("")
    lines.extend(["## Top App Store Categories", ""])
    for item in report["app_store_categories"][:12]:
        lines.append(f"- {item['category']}: {item['bot_count']}")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("bot founder app store report is stale; run tools/generate_bot_founder_app_store.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("bot founder app store report is stale; run tools/generate_bot_founder_app_store.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"bot_founder_packets={report['summary']['founder_packets']} "
        f"categories={report['summary']['app_store_categories']} "
        f"approval_gated={report['summary']['bots_blocked_from_live_actions_until_approval']}"
    )


if __name__ == "__main__":
    main()
