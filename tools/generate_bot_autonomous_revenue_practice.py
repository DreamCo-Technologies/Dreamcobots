#!/usr/bin/env python3
"""Generate sandbox-first autonomous revenue practice plans for every bot."""

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
CLIENT_PACKAGE_REPORT = ROOT / "reports" / "buddy_24_hour_client_package.json"
OUTPUT_JSON = ROOT / "reports" / "bot_autonomous_revenue_practice.json"
OUTPUT_MD = ROOT / "reports" / "BOT_AUTONOMOUS_REVENUE_PRACTICE.md"


REVENUE_PRACTICE_LANES = [
    {
        "id": "problem_discovery",
        "label": "Problem Discovery",
        "practice": "Find expensive, urgent, repeated client problems from public sources and user-provided context.",
        "safe_outputs": ["problem brief", "buyer pain map", "evidence links", "urgency score"],
    },
    {
        "id": "offer_design",
        "label": "Offer Design",
        "practice": "Design a clear service, app, automation, course, report, or AI employee offer that solves the problem.",
        "safe_outputs": ["offer draft", "scope", "deliverables", "success criteria"],
    },
    {
        "id": "pricing_modeling",
        "label": "Pricing Modeling",
        "practice": "Model subscription, one-time, usage-based, retainer, referral, license, or performance-fee pricing.",
        "safe_outputs": ["pricing options", "unit economics", "margin assumptions", "risk notes"],
    },
    {
        "id": "lead_research",
        "label": "Lead Research",
        "practice": "Build public-source ideal-client profiles and target segments without contacting anyone.",
        "safe_outputs": ["ICP notes", "lead category list", "qualification checklist", "source log"],
    },
    {
        "id": "marketplace_need_discovery",
        "label": "Marketplace Need Discovery",
        "practice": "Study public marketplace demand signals to find paying-customer needs AI can fill.",
        "safe_outputs": ["need brief", "buyer intent notes", "offer gap map", "approval-ready proposal draft"],
    },
    {
        "id": "sales_materials",
        "label": "Sales Materials",
        "practice": "Draft landing page copy, demo scripts, prospectus pages, proposals, and objection handling.",
        "safe_outputs": ["prospectus copy", "demo outline", "proposal draft", "FAQ"],
    },
    {
        "id": "sandbox_delivery",
        "label": "Sandbox Delivery",
        "practice": "Build a safe demo, workflow, API test, simulation, dashboard, or report that proves the offer.",
        "safe_outputs": ["sandbox demo", "test evidence", "workflow map", "client walkthrough"],
    },
    {
        "id": "automation_packaging",
        "label": "Automation Packaging",
        "practice": "Package repeatable workflows into reusable bot systems, libraries, templates, and checklists.",
        "safe_outputs": ["workflow library", "tool list", "handoff checklist", "support plan"],
    },
    {
        "id": "partnership_paths",
        "label": "Partnership Paths",
        "practice": "Find safe partner, supplier, affiliate, reseller, referral, and marketplace paths.",
        "safe_outputs": ["partner map", "supplier notes", "referral concept", "approval packet"],
    },
    {
        "id": "contract_opportunities",
        "label": "Contract Opportunities",
        "practice": "Search for public RFPs, grants, procurement needs, and contract categories the offer could serve.",
        "safe_outputs": ["contract category brief", "bid fit score", "requirements summary", "deadline log"],
    },
    {
        "id": "retention_growth",
        "label": "Retention Growth",
        "practice": "Design upsell, renewal, support, education, reporting, and client success loops.",
        "safe_outputs": ["retention plan", "upsell map", "usage report template", "support playbook"],
    },
    {
        "id": "cost_savings",
        "label": "Cost Savings",
        "practice": "Find ways to save the client money through automation, consolidation, monitoring, and prevention.",
        "safe_outputs": ["savings estimate", "before-after workflow", "risk reduction map", "proof checklist"],
    },
    {
        "id": "data_productization",
        "label": "Data Productization",
        "practice": "Turn rights-cleared operational outputs into reusable data, benchmarks, templates, or eval packs.",
        "safe_outputs": ["data package concept", "rights checklist", "schema draft", "buyer use case"],
    },
]

APPROVAL_REQUIRED = [
    "contact_leads_or_customers",
    "log_into_marketplace_accounts",
    "scrape_sites_against_terms",
    "submit_bids_or_proposals",
    "send_email_sms_calls_or_social_posts",
    "spend_ad_budget",
    "collect_private_or_sensitive_data",
    "collect_or_move_money",
    "trade_or_invest_client_assets",
    "publish_payment_links",
    "sign_or_submit_contracts",
    "make_legal_medical_financial_claims",
    "deploy_to_production_or_app_stores",
]

DAILY_REVENUE_TARGET_USD = 1000
TODAY_REVENUE_SPRINT_TARGET_USD = 100

TARGET_SCENARIOS = [
    {
        "id": "one_client_high_value",
        "label": "One High-Value Client",
        "formula": "1 client/day x $1,000 offer",
        "best_for": "Complex automation, app builds, audits, implementation packages, and urgent business fixes.",
        "proof_needed": "Sandbox demo, before/after workflow, clear deliverables, buyer pain evidence, and approval packet.",
    },
    {
        "id": "ten_clients_service",
        "label": "Ten Smaller Client Services",
        "formula": "10 clients/day x $100 service",
        "best_for": "Reports, setup services, templates, lead lists, dashboards, design packets, and quick-turn deliverables.",
        "proof_needed": "Repeatable service checklist, turnaround test, quality review, sample output, and pricing assumptions.",
    },
    {
        "id": "subscription_stack",
        "label": "Subscription Stack",
        "formula": "100 users x $10/day equivalent",
        "best_for": "Bot subscriptions, monitoring dashboards, learning tools, workflow libraries, and managed AI employees.",
        "proof_needed": "Retention reason, support plan, onboarding flow, usage metrics, and churn-risk notes.",
    },
    {
        "id": "cost_savings_retainer",
        "label": "Cost-Savings Retainer",
        "formula": "1 client saves or protects $1,000/day in modeled value",
        "best_for": "Automation, fraud/risk monitoring, operations cleanup, quality checks, compliance prep, and downtime reduction.",
        "proof_needed": "Savings model, risk assumptions, baseline workflow, sandbox evidence, and human review.",
    },
    {
        "id": "marketplace_micro_sales",
        "label": "Marketplace Micro-Sales",
        "formula": "50 buyers/day x $20 digital product",
        "best_for": "Templates, courses, prompts, datasets, app packs, game assets, simulation kits, and industry playbooks.",
        "proof_needed": "Rights-cleared product, landing copy, test audience, refund policy, and distribution plan.",
    },
]

TODAY_SPRINT_SCENARIOS = [
    {
        "id": "one_100_dollar_service",
        "label": "One $100 Service",
        "formula": "1 approved customer x $100 quick service",
        "safe_offer": "Audit, setup, report, dashboard, prompt pack, automation map, design packet, or bug triage.",
    },
    {
        "id": "two_50_dollar_deliverables",
        "label": "Two $50 Deliverables",
        "formula": "2 approved customers x $50 lightweight deliverable",
        "safe_offer": "Checklist, template, mini research brief, landing copy, content plan, data cleanup, or sandbox test.",
    },
    {
        "id": "five_20_dollar_digital_packs",
        "label": "Five $20 Digital Packs",
        "formula": "5 approved buyers x $20 reusable digital product",
        "safe_offer": "Rights-cleared prompt pack, worksheet, micro-course, comparison sheet, calculator, or starter kit.",
    },
]

TARGET_POLICY = {
    "income_guarantee": False,
    "target_statement": "$1,000/day is an aspirational owner-and-user value target, not a promised result.",
    "evidence_rule": "Separate projections, sandbox results, approved live tests, and actual revenue in every bot record.",
    "approval_rule": "Any live money, outreach, ads, account changes, contracts, sensitive data, trading, or production deploys require explicit approval.",
    "blocked_methods": [
        "deception",
        "spam",
        "unauthorized scraping",
        "fake testimonials or endorsements",
        "unapproved financial activity",
        "unsafe legal, medical, or financial claims",
    ],
}

MARKETPLACE_DEMAND_SOURCES = [
    {
        "id": "freelance_marketplaces",
        "label": "Freelance Marketplaces",
        "examples": ["Fiverr-style gigs", "Upwork-style jobs", "Contra-style projects", "PeoplePerHour-style services"],
        "safe_research": "Use public category pages, visible demand themes, user-provided screenshots, exports, or approved APIs.",
    },
    {
        "id": "creator_service_markets",
        "label": "Creator Service Markets",
        "examples": ["design services", "video editing", "music production", "course creation", "game asset services"],
        "safe_research": "Compare visible service packaging, pricing bands, turnaround promises, and recurring buyer needs.",
    },
    {
        "id": "business_software_markets",
        "label": "Business Software Markets",
        "examples": ["app stores", "SaaS directories", "automation marketplaces", "template stores"],
        "safe_research": "Find repetitive pain points, integration gaps, reviews, and missing workflows without collecting private data.",
    },
    {
        "id": "public_contract_and_rfp_sources",
        "label": "Public Contract And RFP Sources",
        "examples": ["government procurement", "grant notices", "vendor portals", "public bid listings"],
        "safe_research": "Summarize requirements, deadlines, qualification gaps, and fit scores before any submission.",
    },
    {
        "id": "community_problem_sources",
        "label": "Community Problem Sources",
        "examples": ["forums", "public Q&A", "reviews", "social comments", "support boards"],
        "safe_research": "Extract anonymized problem themes and product opportunities without contacting people or storing private data.",
    },
]

MARKETPLACE_DEMAND_WORKFLOW = [
    "scan public or user-approved demand signals",
    "cluster repeated paying-customer needs",
    "match the need to the bot's division and lanes",
    "draft an AI-fillable service, app, automation, report, course, game, or simulation offer",
    "estimate price, delivery time, proof needed, and risk",
    "build a sandbox demo or sample output",
    "create a proposal, gig, or landing-page draft",
    "prepare an approval packet before outreach, bidding, account login, scraping, or payment collection",
]

MARKETPLACE_APPROVAL_GATES = [
    "marketplace_account_login",
    "automated_site_collection",
    "buyer_or_seller_messaging",
    "proposal_or_bid_submission",
    "paid_order_acceptance",
    "payment_link_or_invoice_creation",
    "delivery_to_real_customer",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def infer_primary_lanes(bot: dict[str, Any]) -> list[str]:
    division = str(bot.get("division") or "").lower()
    name = str(bot.get("name") or bot.get("slug") or "").lower()
    text = f"{division} {name}"
    lanes = ["problem_discovery", "marketplace_need_discovery", "offer_design", "sandbox_delivery", "sales_materials"]
    if any(term in text for term in ["sales", "market", "influence", "social", "retail"]):
        lanes.extend(["lead_research", "pricing_modeling", "retention_growth"])
    if any(term in text for term in ["finance", "payment", "loan", "crypto", "trade"]):
        lanes.extend(["pricing_modeling", "cost_savings", "contract_opportunities"])
    if any(term in text for term in ["code", "automation", "flow", "ops", "data", "aiinfra"]):
        lanes.extend(["automation_packaging", "data_productization", "cost_savings"])
    if any(term in text for term in ["legal", "admin", "proservices", "construction", "transport"]):
        lanes.extend(["contract_opportunities", "partnership_paths", "cost_savings"])
    if any(term in text for term in ["education", "health", "food", "science", "arts", "game"]):
        lanes.extend(["data_productization", "retention_growth", "partnership_paths"])
    return list(dict.fromkeys(lanes))[:8]


def build_daily_target_path(bot: dict[str, Any], lanes: list[str]) -> dict[str, Any]:
    name = str(bot.get("name") or bot.get("slug") or "Bot")
    division = str(bot.get("division") or "DreamCo")
    lane_text = ", ".join(lanes[:4])
    return {
        "target_usd_per_day": DAILY_REVENUE_TARGET_USD,
        "target_type": "aspirational_sandbox_goal_not_income_guarantee",
        "owner_goal": "Find, test, and package ethical ways this bot could help the owner earn, save, or protect $1,000/day.",
        "user_goal": "Find, test, and package ethical ways this bot could help a client or user earn, save, or protect $1,000/day.",
        "primary_formula": "price x qualified buyers x delivery capacity = daily revenue target",
        "practice_scenarios": TARGET_SCENARIOS,
        "bot_specific_angle": (
            f"{name} should use {division} knowledge and its primary lanes ({lane_text}) "
            "to build a validated $1,000/day target path."
        ),
        "validation_steps": [
            "state assumptions",
            "identify buyer or user problem",
            "draft offer",
            "estimate price and volume",
            "build sandbox proof",
            "list risks and constraints",
            "create approval packet before live actions",
            "track actual evidence separately from projections",
        ],
        "blocked_until_approval": APPROVAL_REQUIRED,
    }


def build_today_revenue_sprint(bot: dict[str, Any], lanes: list[str]) -> dict[str, Any]:
    name = str(bot.get("name") or bot.get("slug") or "Bot")
    division = str(bot.get("division") or "DreamCo")
    return {
        "target_usd_today": TODAY_REVENUE_SPRINT_TARGET_USD,
        "target_type": "same_day_sandbox_goal_not_income_guarantee",
        "owner_goal": "Prepare one ethical same-day path that could help the owner earn, save, or protect $100 with approval.",
        "user_goal": "Prepare one ethical same-day path that could help a user earn, save, or protect $100 with approval.",
        "scenarios": TODAY_SPRINT_SCENARIOS,
        "bot_specific_prompt": (
            f"{name} should use {division} knowledge and {', '.join(lanes[:4])} to package one same-day $100 offer, "
            "one proof sample, and one approval packet."
        ),
        "today_outputs": [
            "one paying-customer need hypothesis",
            "one $20/$50/$100 offer draft",
            "one sandbox sample or demo",
            "one delivery checklist",
            "one payment-link request draft",
            "one risk note",
            "one owner approval packet",
        ],
        "evidence_tracking": {
            "projected_value_usd": TODAY_REVENUE_SPRINT_TARGET_USD,
            "actual_revenue_usd": 0,
            "actual_revenue_requires_payment_confirmation": True,
            "separate_projection_from_actual": True,
        },
        "blocked_until_approval": APPROVAL_REQUIRED,
    }


def build_marketplace_need_packet(bot: dict[str, Any], lanes: list[str]) -> dict[str, Any]:
    name = str(bot.get("name") or bot.get("slug") or "Bot")
    division = str(bot.get("division") or "DreamCo")
    return {
        "status": "marketplace_need_discovery_ready",
        "mission": (
            f"{name} studies public paying-customer needs and prepares AI-fillable offers for {division} "
            "without contacting customers or taking live marketplace actions until approved."
        ),
        "source_categories": [source["id"] for source in MARKETPLACE_DEMAND_SOURCES],
        "workflow": MARKETPLACE_DEMAND_WORKFLOW,
        "offer_outputs": [
            "customer need brief",
            "AI-fillable service or product idea",
            "pricing hypothesis",
            "sandbox proof plan",
            "sample deliverable",
            "gig or proposal draft",
            "risk and approval checklist",
        ],
        "fit_scoring": {
            "buyer_urgency": "How often the need appears and how painful it looks.",
            "ai_delivery_fit": "How much of the work can be safely automated or accelerated by AI.",
            "proof_speed": "How quickly the bot can build a sandbox sample.",
            "margin_potential": "Expected price minus tool, review, support, and delivery cost.",
            "approval_risk": "Whether the opportunity requires outreach, private data, platform login, money movement, or regulated advice.",
        },
        "bot_specific_prompt": (
            f"Find three paying-customer needs for {division} that match {', '.join(lanes[:5])}; "
            "rank them by buyer urgency, AI delivery fit, proof speed, margin potential, and approval risk."
        ),
        "approval_gates": MARKETPLACE_APPROVAL_GATES,
    }


def build_practice() -> dict[str, Any]:
    connection = read_json(CONNECTION_REPORT, {})
    owner = read_json(OWNER_SETTINGS_REPORT, {})
    package = read_json(CLIENT_PACKAGE_REPORT, {})
    bots = connection.get("bots", [])
    owner_summary = owner.get("summary", {})
    package_summary = package.get("summary", {})

    bot_rows: list[dict[str, Any]] = []
    division_counter: Counter[str] = Counter()
    lane_counter: Counter[str] = Counter()

    for bot in bots:
        lanes = infer_primary_lanes(bot)
        for lane in lanes:
            lane_counter[lane] += 1
        division = str(bot.get("division") or "Unassigned")
        division_counter[division] += 1
        bot_rows.append(
            {
                "slug": bot.get("slug"),
                "name": bot.get("name"),
                "division": division,
                "buddy_connected": bool(bot.get("buddy_routing_ready")),
                "safe_mode": True,
                "practice_status": "sandbox_revenue_practice_ready",
                "primary_revenue_lanes": lanes,
                "daily_revenue_target_usd": DAILY_REVENUE_TARGET_USD,
                "daily_revenue_target_path": build_daily_target_path(bot, lanes),
                "today_revenue_sprint_target_usd": TODAY_REVENUE_SPRINT_TARGET_USD,
                "today_revenue_sprint": build_today_revenue_sprint(bot, lanes),
                "marketplace_need_discovery": build_marketplace_need_packet(bot, lanes),
                "daily_practice_packet": {
                    "research": "Find one client money problem, savings opportunity, or public marketplace need AI can fill.",
                    "offer": "Draft one safe offer or service packet.",
                    "proof": "Create or update one sandbox test, demo, or evidence checklist.",
                    "package": "Prepare one client-facing value note, prospectus update, or approval packet.",
                    "review": "Log what worked, what failed, what needs approval, and the next best money-practice task.",
                },
                "blocked_live_actions": APPROVAL_REQUIRED,
                "evidence_required": [
                    "source links or user-provided context",
                    "assumptions",
                    "risk notes",
                    "test evidence",
                    "approval packet for live action",
                ],
            }
        )

    buddy_example = {
        "name": "Buddy",
        "role": "Reference example for every bot",
        "practice_status": "gold_standard_revenue_coach",
        "daily_revenue_target_usd": DAILY_REVENUE_TARGET_USD,
        "today_revenue_sprint_target_usd": TODAY_REVENUE_SPRINT_TARGET_USD,
        "target_instruction": "Buddy coaches every bot toward a $1,000/day target path while marking assumptions, evidence, and approval gates.",
        "today_sprint_instruction": "Buddy asks every bot to prepare a same-day $100 offer path, proof sample, and approval packet without claiming actual revenue until payment is confirmed.",
        "daily_loop": [
            "Pick the highest-impact client money problem.",
            "Route safe research, offer design, sandbox build, sales materials, and quality checks to specialist bots.",
            "Score outputs by usefulness, evidence, client value, and approval risk.",
            "Package the best result into a demo, prospectus, client offer, or approval packet.",
            "Keep live money, outreach, ads, contracts, trading, and deployments blocked until approved.",
        ],
        "example_offer": "Buddy sells a supervised AI workforce that helps clients discover revenue, save costs, build apps and automations, test ideas, and package sellable systems.",
        "example_metrics": [
            "new revenue ideas per day",
            "validated sandbox demos",
            "client-ready offers",
            "cost-saving opportunities",
            "approval packets ready",
            "blocked risky actions avoided",
            "marketplace needs converted into sandbox offers",
        ],
    }

    return {
        "schema": "dreamco.bot_autonomous_revenue_practice.v1",
        "generated_at": utc_now(),
        "mission": "Every DreamCo bot practices helping clients make autonomous money through sandbox-first discovery, offers, demos, tests, packaging, and approval-gated live action.",
        "default_mode": "sandbox_first_supervised_revenue_practice",
        "summary": {
            "bot_count": len(bots),
            "bots_with_revenue_practice": len(bot_rows),
            "buddy_connected_bots": sum(1 for row in bot_rows if row["buddy_connected"]),
            "safe_mode_bots": len(bot_rows),
            "business_owner_enabled_bots": owner_summary.get("business_owner_enabled_bots", 0),
            "client_package_ready": bool(package_summary.get("client_package_ready")),
            "daily_revenue_target_usd": DAILY_REVENUE_TARGET_USD,
            "bots_with_1000_day_target": len(bot_rows),
            "today_revenue_sprint_target_usd": TODAY_REVENUE_SPRINT_TARGET_USD,
            "bots_with_today_100_sprint": len(bot_rows),
            "same_day_income_guarantee": False,
            "actual_revenue_requires_payment_confirmation": True,
            "owner_and_user_target_enabled_bots": len(bot_rows),
            "income_guarantee": False,
            "target_requires_validation": True,
            "bots_with_marketplace_need_discovery": len(bot_rows),
            "marketplace_source_categories": len(MARKETPLACE_DEMAND_SOURCES),
            "marketplace_approval_gates": len(MARKETPLACE_APPROVAL_GATES),
            "revenue_practice_lanes": len(REVENUE_PRACTICE_LANES),
            "approval_required_actions": len(APPROVAL_REQUIRED),
            "all_bots_practice_autonomous_money": len(bot_rows) == len(bots) and len(bots) >= 1200,
            "live_money_actions_blocked_without_approval": True,
        },
        "buddy_example": buddy_example,
        "target_scenarios": TARGET_SCENARIOS,
        "today_sprint_scenarios": TODAY_SPRINT_SCENARIOS,
        "target_policy": TARGET_POLICY,
        "marketplace_demand_sources": MARKETPLACE_DEMAND_SOURCES,
        "marketplace_demand_workflow": MARKETPLACE_DEMAND_WORKFLOW,
        "marketplace_approval_gates": MARKETPLACE_APPROVAL_GATES,
        "revenue_practice_lanes": REVENUE_PRACTICE_LANES,
        "approval_required": APPROVAL_REQUIRED,
        "division_coverage": dict(sorted(division_counter.items())),
        "lane_coverage": dict(sorted(lane_counter.items())),
        "client_value_promises": [
            "Find new revenue opportunities.",
            "Save money with automation and monitoring.",
            "Package AI employees as sellable services.",
            "Build sandbox demos before spending money.",
            "Create client-ready offers, prospectus pages, and proof packets.",
            "Keep risky live actions approval-gated.",
        ],
        "bots": bot_rows,
        "sources": {
            "buddy_connections": str(CONNECTION_REPORT.relative_to(ROOT)),
            "owner_settings": str(OWNER_SETTINGS_REPORT.relative_to(ROOT)),
            "buddy_24_hour_package": str(CLIENT_PACKAGE_REPORT.relative_to(ROOT)),
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Bot Autonomous Revenue Practice",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bots: {summary['bot_count']}",
        f"- Bots with revenue practice: {summary['bots_with_revenue_practice']}",
        f"- Buddy-connected bots: {summary['buddy_connected_bots']}",
        f"- Safe-mode bots: {summary['safe_mode_bots']}",
        f"- Daily target path: ${summary['daily_revenue_target_usd']:,}/day",
        f"- Bots with $1,000/day target paths: {summary['bots_with_1000_day_target']}",
        f"- Today sprint target: ${summary['today_revenue_sprint_target_usd']:,}",
        f"- Bots with today $100 sprint: {summary['bots_with_today_100_sprint']}",
        f"- Income guarantee: {summary['income_guarantee']}",
        f"- Same-day income guarantee: {summary['same_day_income_guarantee']}",
        f"- Actual revenue requires payment confirmation: {summary['actual_revenue_requires_payment_confirmation']}",
        f"- Target requires validation: {summary['target_requires_validation']}",
        f"- Bots with marketplace need discovery: {summary['bots_with_marketplace_need_discovery']}",
        f"- Marketplace source categories: {summary['marketplace_source_categories']}",
        f"- Revenue practice lanes: {summary['revenue_practice_lanes']}",
        f"- Approval-required actions: {summary['approval_required_actions']}",
        f"- All bots practice autonomous money: {summary['all_bots_practice_autonomous_money']}",
        f"- Live money actions blocked without approval: {summary['live_money_actions_blocked_without_approval']}",
        "",
        "## Buddy Example",
        "",
        report["buddy_example"]["example_offer"],
        "",
        report["buddy_example"]["target_instruction"],
        "",
        report["buddy_example"]["today_sprint_instruction"],
        "",
        "## Target Policy",
        "",
        report["target_policy"]["target_statement"],
        "",
        "## Target Scenarios",
        "",
    ]
    for scenario in report["target_scenarios"]:
        lines.append(f"- **{scenario['label']}**: {scenario['formula']}")
    lines.extend(["", "## Today $100 Sprint Scenarios", ""])
    for scenario in report["today_sprint_scenarios"]:
        lines.append(f"- **{scenario['label']}**: {scenario['formula']}")
    lines.extend(["", "## Marketplace Demand Sources", ""])
    for source in report["marketplace_demand_sources"]:
        lines.append(f"- **{source['label']}**: {source['safe_research']}")
    lines.extend(
        [
            "",
            "## Revenue Practice Lanes",
            "",
        ]
    )
    for lane in report["revenue_practice_lanes"]:
        lines.append(f"- **{lane['label']}**: {lane['practice']}")
    lines.extend(["", "## Approval Required", ""])
    for action in report["approval_required"]:
        lines.append(f"- {action}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_practice()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("bot autonomous revenue practice report missing; run the generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if rendered != existing_rendered:
            raise SystemExit("bot autonomous revenue practice report stale; run the generator")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(
        "revenue_practice_ready={ready} bots={bots} lanes={lanes} approval_gates={gates}".format(
            ready=summary["all_bots_practice_autonomous_money"],
            bots=summary["bot_count"],
            lanes=summary["revenue_practice_lanes"],
            gates=summary["approval_required_actions"],
        )
    )
    return 0 if summary["all_bots_practice_autonomous_money"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
