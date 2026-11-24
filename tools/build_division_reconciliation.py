#!/usr/bin/env python3
"""Reconcile 55 domain divisions, preserved supplemental portfolios, and 20 shared platform MasterBots."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/division-reconciliation-policy.json"
DOMAIN_SOURCE = ROOT / "shared/division-production-contract.ts"
MASTERBOTS = ROOT / "config/masterbot-65-registry.json"
FEATURED = ROOT / "website/data/masterbot-homepage-featured.json"
OUTPUT = ROOT / "config/generated/division-reconciliation.json"


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def load_domain_names(source: str) -> list[str]:
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \{\n([\s\S]*?)^  \},?$", re.MULTILINE)
    names = []
    for match in pattern.finditer(source):
        body = match.group(2)
        if "purpose:" in body and "focusAreas:" in body and "serves:" in body and "outcome:" in body and "boundary:" in body:
            names.append(match.group(1))
    if len(names) != 55 or len({normalize(name) for name in names}) != 55:
        raise ValueError(f"Expected 55 unique complete domain profiles; found {len(names)}")
    return names


def build_reconciliation() -> dict:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    masterbot_doc = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    featured_doc = json.loads(FEATURED.read_text(encoding="utf-8"))
    domains = load_domain_names(DOMAIN_SOURCE.read_text(encoding="utf-8"))
    core_count = int(policy["core_division_count"])
    if policy.get("total_domain_division_count") != 55 or len(domains[:core_count]) != 45:
        raise ValueError("Expected 45 original divisions plus ten promoted supplemental divisions")
    if masterbot_doc.get("canonical_count") != 65 or len(masterbot_doc.get("divisions", [])) != 65:
        raise ValueError("Expected the existing 65-entry MasterBot registry")
    if {normalize(x["name"]) for x in masterbot_doc["divisions"][:45]} != {normalize(x) for x in domains[:45]}:
        raise ValueError("The first 45 MasterBot identities must continue matching the original 45 divisions")

    additions = policy.get("additional_divisions", {})
    if len(additions) != 10 or {normalize(x) for x in domains[45:]} != {normalize(x) for x in additions}:
        raise ValueError("The ten promoted supplemental divisions must match the policy exactly")
    featured = {int(x["id"]): x for x in featured_doc.get("items", [])}
    platform = masterbot_doc["divisions"][45:65]
    if [int(x["id"]) for x in platform] != list(range(46, 66)):
        raise ValueError("Platform MasterBot IDs must remain exactly 46-65")
    platform_rows = []
    for bot in platform:
        ident = int(bot["id"])
        card = featured.get(ident)
        if not card or card.get("name") != bot["name"] or not card.get("purpose"):
            raise ValueError(f"Missing or mismatched homepage purpose for platform MasterBot {ident}")
        platform_rows.append({
            "id": ident, "name": bot["name"], "purpose": card["purpose"],
            "kind": "shared_platform_service", "available_to_all_domain_divisions": True,
            "primary_domain_owner": None, "ownership_status": "shared_platform_not_a_domain_division",
            "trained_or_mastered": False,
        })

    additional_rows = []
    for name, entry in sorted(additions.items()):
        portfolio_path = ROOT / entry["portfolio"]
        fleet_path = ROOT / "website" / "data" / "bot-fleet" / f"{name}.json"
        tests_path = ROOT / "website" / "data" / "bot-capability-tests" / f"{name}.json"
        if not all(path.is_file() for path in (portfolio_path, fleet_path, tests_path)):
            raise ValueError(f"{name} is missing its portfolio, fleet manifest, or capability-test manifest")
        portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
        fleet = json.loads(fleet_path.read_text(encoding="utf-8"))
        tests = json.loads(tests_path.read_text(encoding="utf-8"))
        bots = portfolio.get("bots", [])
        if portfolio.get("division") != name or len(bots) < 5:
            raise ValueError(f"{name} must preserve its named portfolio and at least five bot profiles")
        if len({bot.get("slug") for bot in bots}) != len(bots):
            raise ValueError(f"{name} contains duplicate bot slugs")
        fleet_divisions = {bot.get("division") for bot in fleet}
        if fleet_divisions != {name}:
            raise ValueError(f"{name} fleet manifest has inconsistent division identity")
        test_divisions = {bot.get("division") for bot in tests}
        if test_divisions != {name}:
            raise ValueError(f"{name} capability tests have inconsistent division identity")
        related = entry["related_domain"]
        if normalize(related) not in {normalize(x) for x in domains[:45]}:
            raise ValueError(f"{name} related domain must refer to one of the original 45 divisions")
        additional_rows.append({
            "name": name, "kind": "first_class_domain_division",
            "source_portfolio": entry["portfolio"],
            "bot_profile_count": len(bots),
            "fleet_manifest": f"website/data/bot-fleet/{name}.json",
            "capability_test_manifest": f"website/data/bot-capability-tests/{name}.json",
            "related_domain": related,
            "proposed_collaborator_masterbot_id": int(entry["proposed_collaborator_masterbot_id"]),
            "masterbot_link_status": "proposed_requires_owner_review",
            "shared_platform_masterbot_ids": list(range(46, 66)),
            "all_ten_capability_operations_inherited": True,
            "production_ready": False,
        })

    domain_rows = []
    for index, name in enumerate(domains):
        domain_rows.append({
            "id": normalize(name), "name": name,
            "domain_tier": "original_core" if index < core_count else "promoted_supplemental",
            "shared_platform_masterbot_ids": list(range(46, 66)),
            "capability_operations": ["discover", "intake", "research", "design", "build", "simulate", "evaluate", "integrate", "operate", "improve"],
        })

    return {
        "schema": "dreamco.division_reconciliation.v2",
        "status": "55_DOMAIN_DIVISIONS_STRUCTURALLY_RECONCILED_EVIDENCE_GATES_REMAIN",
        "source_refs": [
            "shared/division-production-contract.ts", "config/division-reconciliation-policy.json",
            "config/masterbot-65-registry.json", "website/data/masterbot-homepage-featured.json",
        ],
        "counts": {
            "original_core_divisions": 45,
            "promoted_supplemental_divisions": len(additional_rows),
            "total_domain_divisions": len(domain_rows),
            "supplemental_bot_profiles": sum(x["bot_profile_count"] for x in additional_rows),
            "shared_platform_masterbots": len(platform_rows),
        },
        "rules": policy["safeguards"],
        "domain_divisions": domain_rows,
        "promoted_supplemental_divisions": additional_rows,
        "shared_platform_masterbots": platform_rows,
        "truth": "This file reconciles domain contracts and portfolio lineage only. It is not evidence of live integrations, model training, benchmark mastery, or production readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_reconciliation()
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Division reconciliation artifact is stale; regenerate and review it.")
        print("Division reconciliation is current: 55 domains, ten promoted portfolios, 20 shared platform MasterBots.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "counts": result["counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
