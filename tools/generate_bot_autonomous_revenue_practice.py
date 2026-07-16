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
    lanes = ["problem_discovery", "offer_design", "sandbox_delivery", "sales_materials"]
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
                "daily_practice_packet": {
                    "research": "Find one client money problem or savings opportunity.",
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
            "revenue_practice_lanes": len(REVENUE_PRACTICE_LANES),
            "approval_required_actions": len(APPROVAL_REQUIRED),
            "all_bots_practice_autonomous_money": len(bot_rows) == len(bots) and len(bots) >= 1200,
            "live_money_actions_blocked_without_approval": True,
        },
        "buddy_example": buddy_example,
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
        f"- Revenue practice lanes: {summary['revenue_practice_lanes']}",
        f"- Approval-required actions: {summary['approval_required_actions']}",
        f"- All bots practice autonomous money: {summary['all_bots_practice_autonomous_money']}",
        f"- Live money actions blocked without approval: {summary['live_money_actions_blocked_without_approval']}",
        "",
        "## Buddy Example",
        "",
        report["buddy_example"]["example_offer"],
        "",
        "## Revenue Practice Lanes",
        "",
    ]
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

