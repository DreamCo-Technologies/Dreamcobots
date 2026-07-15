#!/usr/bin/env python3
"""Generate contract discovery coverage for every DreamCo bot."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "bot_contract_discovery_system.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "reports" / "bot_contract_discovery_report.json"
OUTPUT_MD = ROOT / "reports" / "BOT_CONTRACT_DISCOVERY_REPORT.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def words(value):
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def opportunity_mix(bot, config):
    division = str(bot.get("division") or "").lower()
    category = str(bot.get("category") or "").lower()
    base = ["client_service_opportunity", "private_rfp", "partnership_opportunity"]
    if "transport" in division or "logistics" in category:
        base.extend(["trucking_route_contract", "supplier_contract", "local_procurement"])
    elif "construction" in division or "real" in division:
        base.extend(["government_contract", "local_procurement", "subcontracting_opportunity"])
    elif "education" in division or "health" in division:
        base.extend(["grant", "local_procurement", "vendor_registration"])
    elif "code" in division or "ai" in division or "data" in division:
        base.extend(["enterprise_software_contract", "app_store_service_opportunity", "government_contract"])
    elif "sales" in division or "market" in division:
        base.extend(["private_rfp", "vendor_registration", "enterprise_software_contract"])
    else:
        base.extend(["government_contract", "vendor_registration", "grant"])
    seen = []
    for item in base:
        if item in config.get("opportunity_types", []) and item not in seen:
            seen.append(item)
    return seen[:6]


def build_bot_packet(bot, config):
    slug = bot.get("slug") or bot.get("id")
    name = bot.get("name") or words(slug).title()
    division = bot.get("division") or "DreamCo"
    opportunities = opportunity_mix(bot, config)
    return {
        "slug": slug,
        "name": name,
        "division": division,
        "category": bot.get("category") or "business",
        "contract_roles": config.get("bot_contract_roles", []),
        "opportunity_types": opportunities,
        "search_cadence": config.get("search_cadence", {}),
        "matching_fields": config.get("matching_fields", []),
        "approval_gates": config.get("approval_gates", []),
        "sample_search_prompt": (
            f"Search public and owner-approved sources for {name} contract opportunities in "
            f"{division}. Score fit, risk, deadline, requirements, proof needed, and next approval step."
        ),
        "dashboard_status": "ready_for_contract_discovery",
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    packets = [build_bot_packet(bot, config) for bot in bots]
    opportunity_counts = Counter(opportunity for packet in packets for opportunity in packet["opportunity_types"])
    division_counts = Counter(packet["division"] for packet in packets)

    summary = {
        "bot_count": len(bots),
        "bots_with_contract_discovery": len(packets),
        "opportunity_types_tracked": len(config.get("opportunity_types", [])),
        "source_categories_tracked": len(config.get("source_categories", [])),
        "approval_gates_declared": len(config.get("approval_gates", [])),
        "blocked_actions_declared": len(config.get("blocked_without_review", [])),
        "matching_fields": len(config.get("matching_fields", [])),
        "bot_contract_roles": len(config.get("bot_contract_roles", [])),
        "sample_opportunities_ready": len(packets[:12]),
        "all_bots_ready_for_contract_search": len(packets) == len(bots),
    }

    return {
        "schema": "dreamco.bot_contract_discovery_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "search_cadence": config.get("search_cadence", {}),
        "summary": summary,
        "opportunity_types": config.get("opportunity_types", []),
        "source_categories": config.get("source_categories", []),
        "approval_gates": config.get("approval_gates", []),
        "blocked_without_review": config.get("blocked_without_review", []),
        "fit_scoring": config.get("fit_scoring", []),
        "top_opportunity_types": [
            {"opportunity_type": opportunity, "bot_count": count}
            for opportunity, count in opportunity_counts.most_common(12)
        ],
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(12)
        ],
        "dashboard_sample": packets[:12],
        "next_actions": [
            "Connect public-source search adapters after rate limits and source terms are reviewed.",
            "Create a weekly owner approval digest for bid, registration, outreach, and pricing decisions.",
            "Keep all submissions, buyer contact, supplier contact, signatures, and spending blocked until approved.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Bot Contract Discovery Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bots with contract discovery: {summary['bots_with_contract_discovery']} / {summary['bot_count']}",
        f"- Opportunity types tracked: {summary['opportunity_types_tracked']}",
        f"- Source categories tracked: {summary['source_categories_tracked']}",
        f"- Approval gates declared: {summary['approval_gates_declared']}",
        f"- Blocked actions declared: {summary['blocked_actions_declared']}",
        f"- Bot contract roles: {summary['bot_contract_roles']}",
        "",
        "## Approval Gates",
        "",
    ]
    for gate in report["approval_gates"]:
        lines.append(f"- {gate}")
    lines.extend(["", "## Source Categories", ""])
    for source in report["source_categories"]:
        lines.append(f"### {source['label']}")
        lines.append("")
        lines.append(f"- Examples: {', '.join(source.get('examples', []))}")
        lines.append(f"- Allowed actions: {', '.join(source.get('allowed_actions', []))}")
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
            raise SystemExit("bot contract discovery report is stale; run tools/generate_bot_contract_discovery_report.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("bot contract discovery report is stale; run tools/generate_bot_contract_discovery_report.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"bots={report['summary']['bots_with_contract_discovery']} "
        f"opportunity_types={report['summary']['opportunity_types_tracked']} "
        f"approval_gates={report['summary']['approval_gates_declared']}"
    )


if __name__ == "__main__":
    main()
