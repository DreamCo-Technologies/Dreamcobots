#!/usr/bin/env python3
"""Reconcile 45 canonical DreamCo divisions, 10 legacy portfolios, and 20 platform MasterBots."""
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
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \\{\\n([\\s\\S]*?)^  \\},?$", re.MULTILINE)
    names = []
    for match in pattern.finditer(source):
        body = match.group(2)
        if "purpose:" in body and "focusAreas:" in body:
            names.append(match.group(1))
    if len(names) != 45 or len({normalize(name) for name in names}) != 45:
        raise ValueError(f"Expected 45 unique canonical domain profiles; found {len(names)}")
    return names


def build_reconciliation() -> dict:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    masterbot_doc = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    featured_doc = json.loads(FEATURED.read_text(encoding="utf-8"))
    domains = load_domain_names(DOMAIN_SOURCE.read_text(encoding="utf-8"))
    if policy.get("canonical_division_count") != 45:
        raise ValueError("Policy must preserve exactly 45 canonical divisions")
    if masterbot_doc.get("canonical_count") != 65 or len(masterbot_doc.get("divisions", [])) != 65:
        raise ValueError("Expected the existing 65-entry MasterBot registry")
    if {normalize(x["name"]) for x in masterbot_doc["divisions"][:45]} != {normalize(x) for x in domains}:
        raise ValueError("The first 45 MasterBot identities must match the 45 canonical domain names")
    domain_by_key = {normalize(name): name for name in domains}

    aliases = policy.get("supplemental_portfolios", {})
    if len(aliases) != 10:
        raise ValueError(f"Expected ten supplemental source portfolios; found {len(aliases)}")
    alias_rows = []
    for source_name, entry in sorted(aliases.items()):
        target = entry.get("target", "")
        if normalize(source_name) in domain_by_key:
            raise ValueError(f"Supplemental source {source_name} duplicates a canonical division")
        if normalize(target) not in domain_by_key:
            raise ValueError(f"Alias target for {source_name} is not canonical: {target}")
        source_file = ROOT / "App_bots" / f"{source_name}.json"
        target_file = ROOT / "App_bots" / f"{target}.json"
        if not source_file.is_file() or not target_file.is_file():
            raise ValueError(f"Missing source or target App_bots portfolio for {source_name} -> {target}")
        alias_rows.append({
            "source_portfolio": source_name,
            "source_path": f"App_bots/{source_name}.json",
            "canonical_division": domain_by_key[normalize(target)],
            "target_path": f"App_bots/{target}.json",
            "reason": entry.get("reason", ""),
            "preserve_source_identity": True,
            "counts_as_new_division": False,
        })

    platform = masterbot_doc["divisions"][45:65]
    if [int(x["id"]) for x in platform] != list(range(46, 66)):
        raise ValueError("Platform MasterBot IDs must remain exactly 46-65")
    featured = {int(x["id"]): x for x in featured_doc.get("items", [])}
    platform_rows = []
    for bot in platform:
        ident = int(bot["id"])
        card = featured.get(ident)
        if not card or card.get("name") != bot["name"] or not card.get("purpose"):
            raise ValueError(f"Missing or mismatched homepage purpose for platform MasterBot {ident}")
        platform_rows.append({
            "id": ident,
            "name": bot["name"],
            "purpose": card["purpose"],
            "kind": "shared_platform_service",
            "available_to_all_domain_divisions": True,
            "primary_domain_owner": None,
            "ownership_status": "platform_shared_not_a_business_division",
            "trained_or_mastered": False,
        })

    domain_rows = []
    for name in domains:
        domain_rows.append({
            "id": normalize(name),
            "name": name,
            "supplemental_sources": [row["source_portfolio"] for row in alias_rows
                                    if normalize(row["canonical_division"]) == normalize(name)],
            "shared_platform_masterbot_ids": list(range(46, 66)),
        })

    return {
        "schema": "dreamco.division_reconciliation.v1",
        "status": "STRUCTURE_RECONCILED_EVIDENCE_GATES_REMAIN",
        "source_refs": [
            "shared/division-production-contract.ts",
            "config/division-reconciliation-policy.json",
            "config/masterbot-65-registry.json",
            "website/data/masterbot-homepage-featured.json",
        ],
        "counts": {
            "canonical_business_divisions": len(domain_rows),
            "supplemental_source_portfolios": len(alias_rows),
            "shared_platform_masterbots": len(platform_rows),
            "canonical_division_total_after_reconciliation": len(domain_rows),
        },
        "rules": policy["safeguards"],
        "domain_divisions": domain_rows,
        "supplemental_portfolio_aliases": alias_rows,
        "shared_platform_masterbots": platform_rows,
        "truth": "This file reconciles ownership and routing structure only. It is not evidence of runtime completeness, training, benchmark mastery, or production readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_reconciliation(), indent=2, ensure_ascii=False) + "\\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Division reconciliation artifact is stale; regenerate and review it.")
        print("Division reconciliation is current: 45 domains, 10 supplemental aliases, 20 shared platform MasterBots.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "counts": build_reconciliation()["counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
