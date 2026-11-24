#!/usr/bin/env python3
"""Build a conservative crosswalk between 65 MasterBots and 55 domain divisions.

Only exact normalized identity matches are proposed. No keyword or fuzzy match is
promoted to ownership; unresolved entries remain explicit for owner review.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTERBOTS = ROOT / "config/masterbot-75-registry.json"
DOMAIN_SOURCE = ROOT / "shared/division-production-contract.ts"
OUTPUT = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def load_domain_names(source: str) -> list[str]:
    # Domain profiles are the only top-level objects with purpose + focusAreas.
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \{\n([\s\S]*?)^  \},?$", re.MULTILINE)
    names = []
    for match in pattern.finditer(source):
        body = match.group(2)
        if "purpose:" in body and "focusAreas:" in body:
            names.append(match.group(1))
    if len(names) != 55:
        raise ValueError(f"Expected 55 domain profiles in {DOMAIN_SOURCE}; found {len(names)}")
    if len({normalize(name) for name in names}) != len(names):
        raise ValueError("Domain profile names are not unique after normalization")
    return names


def build_crosswalk(masterbot_doc: dict, domain_names: list[str]) -> dict:
    bots = masterbot_doc.get("divisions", [])
    if masterbot_doc.get("canonical_count") != 75 or len(bots) != 75:
        raise ValueError(f"Expected 75 MasterBots; found {len(bots)}")
    ids = [str(bot.get("id", "")) for bot in bots]
    names = [str(bot.get("name", "")) for bot in bots]
    if any(not value for value in ids + names):
        raise ValueError("MasterBot IDs and names must be non-empty")
    if len(set(ids)) != 75 or len({normalize(name) for name in names}) != 75:
        raise ValueError("MasterBot IDs and normalized names must be unique")

    domain_by_key = {normalize(name): name for name in domain_names}
    bot_by_key = {normalize(name): bot for name, bot in zip(names, bots)}
    domains = []
    for domain in domain_names:
        bot = bot_by_key.get(normalize(domain))
        approved = bool(bot and bot.get("primary_domain_approved"))
        domains.append({
            "domain_id": normalize(domain),
            "domain_name": domain,
            "masterbot_id": bot.get("id") if bot else None,
            "masterbot_name": bot.get("name") if bot else None,
            "mapping_status": "owner_approved_exact_name_match" if approved else ("proposed_exact_name_match" if bot else "unresolved"),
            "evidence": ["shared/division-production-contract.ts", "config/masterbot-75-registry.json"],
            "review_required": not approved,
            "owner_approval": bot.get("approval_source") if approved else None,
        })

    masterbot_rows = []
    for bot in bots:
        domain = domain_by_key.get(normalize(str(bot["name"])))
        approved = bool(domain and bot.get("primary_domain_approved"))
        collaborators = [
            normalize(name) for name in bot.get("collaborators", [])
            if normalize(name) in domain_by_key
        ]
        shared = not domain
        masterbot_rows.append({
            "masterbot_id": bot["id"],
            "masterbot_name": bot["name"],
            "primary_domain_id": normalize(domain) if domain else None,
            "primary_domain_name": domain,
            "mapping_status": "owner_approved_primary_domain" if approved else ("shared_platform_service" if shared else "proposed_exact_name_match"),
            "collaborator_domain_ids": collaborators,
            "review_required": not (approved or shared),
            "owner_approval": bot.get("approval_source") if approved else ("not_applicable_shared_service" if shared else None),
        })

    return {
        "schema": "dreamco.masterbot_domain_crosswalk.v2",
        "status": "owner_approved_domain_routes_with_shared_platform_services",
        "source_refs": [
            "config/masterbot-75-registry.json",
            "shared/division-production-contract.ts",
        ],
        "counts": {
            "masterbots": len(masterbot_rows),
            "domain_divisions": len(domains),
            "owner_approved_domain_mappings": sum(x["mapping_status"] == "owner_approved_exact_name_match" for x in domains),
            "unresolved_domain_divisions": sum(x["masterbot_id"] is None for x in domains),
            "shared_platform_masterbots": sum(x["mapping_status"] == "shared_platform_service" for x in masterbot_rows),
            "unresolved_masterbots": sum(x["mapping_status"] == "proposed_exact_name_match" for x in masterbot_rows),
        },
        "rules": [
            "Each of the 55 canonical domains has one owner-approved domain MasterBot.",
            "MasterBots 46–65 remain shared platform services and are collaboration routes, not primary domain owners.",
            "New division MasterBots 66–75 have unique domain charters and do not replace the existing 45 domain owners.",
            "Explicit owner approval covers primary division routing only; external actions, spending, deployments, legal commitments and physical actuation remain separately gated.",
            "Each MasterBot has at most one primary domain; collaborator links are secondary routes.",
        ],
        "domains": domains,
        "masterbots": masterbot_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    masterbot_doc = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    domains = load_domain_names(DOMAIN_SOURCE.read_text(encoding="utf-8"))
    rendered = json.dumps(build_crosswalk(masterbot_doc, domains), indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("MasterBot/domain crosswalk is stale; regenerate and review it")
        print("MasterBot/domain crosswalk is current")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
