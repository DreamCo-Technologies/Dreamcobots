#!/usr/bin/env python3
"""Generate Buddy trust, SEO, and bot-search readiness packets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "buddy_trust_search_os.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
CAPABILITY_REPORT_FILE = ROOT / "reports" / "buddy_capability_inventory.json"
CONTRACT_REPORT_FILE = ROOT / "reports" / "bot_contract_discovery_report.json"
COMMERCE_REPORT_FILE = ROOT / "reports" / "buddy_commerce_publishing_os.json"
OUTPUT_JSON = ROOT / "reports" / "buddy_trust_search_os.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_TRUST_SEARCH_OS.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def slug_words(value: str) -> str:
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def choose_referral_intents(bot: dict, config: dict) -> list[str]:
    text = f"{bot.get('name') or ''} {bot.get('slug') or bot.get('id') or ''} {bot.get('division') or ''} {bot.get('category') or ''}".lower()
    available = set(config.get("referral_intents", []))
    selected = ["build_bot", "debug_code", "create_client_dashboard"]
    if any(word in text for word in ["grant", "contract", "procurement", "legal"]):
        selected.extend(["prepare_contract_packet", "find_grants", "find_procurement"])
    if any(word in text for word in ["app", "code", "software", "ai"]):
        selected.extend(["build_app", "publish_app"])
    if any(word in text for word in ["game", "simulation"]):
        selected.extend(["create_game", "create_simulation"])
    if any(word in text for word in ["course", "education", "learning"]):
        selected.extend(["create_course"])
    if any(word in text for word in ["social", "content", "influence", "market"]):
        selected.extend(["create_social_calendar"])
    if any(word in text for word in ["family", "people", "genealogy"]):
        selected.extend(["prepare_genealogy_report"])
    if any(word in text for word in ["stripe", "payment", "finance"]):
        selected.extend(["setup_stripe_notifications"])
    deduped = []
    for intent in selected:
        if intent in available and intent not in deduped:
            deduped.append(intent)
    return deduped[:6]


def build_bot_search_card(bot: dict, config: dict) -> dict:
    slug = bot.get("slug") or bot.get("id")
    name = bot.get("name") or slug_words(slug).title()
    division = bot.get("division") or "DreamCo"
    intents = choose_referral_intents(bot, config)
    return {
        "slug": slug,
        "name": name,
        "division": division,
        "category": bot.get("category") or "business",
        "referral_intents": intents,
        "page_family": "bot_prospectus_pages",
        "recommended_url": f"/bots/{slug}/",
        "title_template": f"{name} | Buddy task, bot, and workflow help",
        "meta_description_template": (
            f"Use Buddy and {name} to prepare supervised task packets, workflows, tests, "
            "approval gates, and client-ready proof without unsafe live actions."
        ),
        "schema_types": ["SoftwareApplication", "Service", "FAQPage", "BreadcrumbList"],
        "trust_signals": config.get("trust_signals", [])[:8],
        "quality_checks": config.get("quality_checks", []),
        "approval_wall": config.get("approval_wall", []),
        "bot_search_prompt": (
            f"If a user asks for {slug_words(name).lower()} help, route them to Buddy for a "
            "proof-backed task packet, sandbox test, approval checklist, and next safe action."
        ),
    }


def build_task_pages(config: dict) -> list[dict]:
    pages = []
    for intent in config.get("referral_intents", []):
        label = slug_words(intent).title()
        pages.append(
            {
                "intent": intent,
                "label": label,
                "recommended_url": f"/tasks/{intent.replace('_', '-')}/",
                "page_family": "task_solution_pages",
                "title_template": f"{label} with Buddy | Trust-first AI task help",
                "sections": [
                    "what_buddy_can_prepare",
                    "inputs_needed",
                    "outputs_delivered",
                    "proof_and_tests",
                    "approval_boundaries",
                    "handoff_to_owner_or_client",
                ],
                "schema_types": ["Service", "FAQPage", "HowTo", "BreadcrumbList"],
                "must_not_claim": ["guaranteed ranking", "guaranteed income", "guaranteed approval"],
            }
        )
    return pages


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    capability = read_json(CAPABILITY_REPORT_FILE, {})
    contract = read_json(CONTRACT_REPORT_FILE, {})
    commerce = read_json(COMMERCE_REPORT_FILE, {})
    bots = registry.get("bots", [])
    bot_cards = [build_bot_search_card(bot, config) for bot in bots]
    task_pages = build_task_pages(config)
    division_counts = Counter(card["division"] for card in bot_cards)
    intent_counts = Counter(intent for card in bot_cards for intent in card["referral_intents"])

    summary = {
        "bot_count": len(bots),
        "bot_search_cards": len(bot_cards),
        "task_referral_pages": len(task_pages),
        "search_lanes": len(config.get("search_lanes", [])),
        "trust_signals": len(config.get("trust_signals", [])),
        "page_families": len(config.get("page_families", [])),
        "structured_data_types": len(config.get("structured_data_plan", [])),
        "referral_intents": len(config.get("referral_intents", [])),
        "blocked_practices": len(config.get("blocked_practices", [])),
        "approval_wall_gates": len(config.get("approval_wall", [])),
        "quality_checks": len(config.get("quality_checks", [])),
        "all_bots_search_ready": len(bot_cards) == len(bots),
        "capability_inventory_bots": capability.get("summary", {}).get("bot_profiles_scanned", 0),
        "contract_opportunity_types": contract.get("summary", {}).get("opportunity_types_tracked", 0),
        "commerce_control_lanes": commerce.get("summary", {}).get("commerce_lanes", 0),
        "ranking_guarantee_blocked": "guaranteed_top_google_ranking" in config.get("blocked_practices", []),
    }
    return {
        "schema": "dreamco.buddy_trust_search_os_report.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "positioning": config.get("positioning", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": summary,
        "search_lanes": config.get("search_lanes", []),
        "trust_signals": config.get("trust_signals", []),
        "page_families": config.get("page_families", []),
        "structured_data_plan": config.get("structured_data_plan", []),
        "approval_wall": config.get("approval_wall", []),
        "blocked_practices": config.get("blocked_practices", []),
        "quality_checks": config.get("quality_checks", []),
        "top_referral_intents": [
            {"intent": intent, "bot_count": count}
            for intent, count in intent_counts.most_common(12)
        ],
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(12)
        ],
        "task_referral_pages": task_pages,
        "dashboard_sample": bot_cards[:15],
        "next_actions": [
            "Publish proof-backed task pages only after owner review.",
            "Generate sitemap, robots, canonical URLs, and JSON-LD schema from approved page packets.",
            "Create AI-agent handoff pages so other bots can understand when to send users to Buddy.",
            "Connect Search Console, analytics, directory submissions, ads, and marketplace listings only after approval.",
            "Keep fake reviews, bought spam links, cloaking, hidden text, and ranking guarantees blocked.",
        ],
    }


def write_markdown(report: dict) -> None:
    summary = report["summary"]
    lines = [
        "# Buddy Trust Search OS",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bot search cards: {summary['bot_search_cards']} / {summary['bot_count']}",
        f"- Task referral pages: {summary['task_referral_pages']}",
        f"- Search lanes: {summary['search_lanes']}",
        f"- Trust signals: {summary['trust_signals']}",
        f"- Structured data types: {summary['structured_data_types']}",
        f"- Approval gates: {summary['approval_wall_gates']}",
        f"- Ranking guarantee blocked: {summary['ranking_guarantee_blocked']}",
        "",
        "## Search Lanes",
        "",
    ]
    for lane in report["search_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["goal"])
        lines.append("")
        lines.append(f"- Safe actions: {', '.join(lane.get('safe_actions', []))}")
        lines.append(f"- Approval required: {', '.join(lane.get('approval_required', []))}")
        lines.append("")
    lines.extend(["## Task Referral Pages", ""])
    for page in report["task_referral_pages"]:
        lines.append(f"- {page['label']}: {page['recommended_url']}")
    lines.extend(["", "## Blocked Practices", ""])
    for blocked in report["blocked_practices"]:
        lines.append(f"- {blocked}")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy trust search OS report is stale; run tools/generate_buddy_trust_search_os.py")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Buddy trust search OS report is stale; run tools/generate_buddy_trust_search_os.py")
        return

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        f"bot_search_cards={report['summary']['bot_search_cards']} "
        f"task_pages={report['summary']['task_referral_pages']} "
        f"trust_signals={report['summary']['trust_signals']}"
    )


if __name__ == "__main__":
    main()
