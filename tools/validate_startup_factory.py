#!/usr/bin/env python3
"""Validate Buddy Startup Factory contracts and financing safety rules."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/startup_factory/startup_factory_contract.json"
FINANCING = ROOT / "config/startup_factory/financing_paths.json"


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    financing = json.loads(FINANCING.read_text(encoding="utf-8"))

    required_stages = {"DISCOVER", "DEFINE", "PROTOTYPE", "VALIDATE", "BUILD", "LAUNCH", "OPERATE", "SCALE", "FUND"}
    stages = set(contract.get("stages", []))
    if stages != required_stages:
        raise SystemExit(f"invalid startup stages: missing={sorted(required_stages-stages)} extra={sorted(stages-required_stages)}")

    lifecycle = ["idea", "generated", "executed", "tested", "verified", "deployed", "real_world_validated"]
    if contract.get("evidence_lifecycle") != lifecycle:
        raise SystemExit("startup evidence lifecycle is invalid")

    required_outputs = set(contract.get("required_outputs", []))
    if len(required_outputs) < 20:
        raise SystemExit("startup factory must expose a complete planning/output contract")

    archetypes = set(contract.get("startup_archetypes", []))
    if len(archetypes) < 20:
        raise SystemExit("startup archetype catalog is too small")

    paths = financing.get("decision_tree", [])
    path_names = {item.get("path") for item in paths}
    required_paths = set(contract.get("financing_paths", []))
    if path_names != required_paths:
        raise SystemExit(f"financing paths mismatch: missing={sorted(required_paths-path_names)} extra={sorted(path_names-required_paths)}")

    policy = contract.get("loan_guidance_policy", {})
    required_checks = {"eligibility_factors", "documentation", "lender_or_program_discovery", "apr_and_fees", "repayment_terms", "collateral_or_guarantees", "risks", "comparison_matrix"}
    if not required_checks.issubset(set(policy.get("must_include", []))):
        raise SystemExit("loan guidance policy is missing required decision-support checks")
    forbidden = {"guarantee_approval", "fabricate_eligibility", "represent_estimates_as_offers", "hide_fees_or_risks"}
    if not forbidden.issubset(set(policy.get("must_not", []))):
        raise SystemExit("loan safety policy is incomplete")

    fields = set(financing.get("required_comparison_fields", []))
    if not {"apr_or_effective_cost", "fees", "term", "payment_structure", "risk", "source_date", "source_url"}.issubset(fields):
        raise SystemExit("financing comparison matrix is missing cost/risk/source fields")

    print("PASS: Buddy Startup Factory stages validated")
    print(f"PASS: {len(archetypes)} startup archetypes supported")
    print(f"PASS: {len(paths)} financing paths supported")
    print("PASS: loan guidance is educational, source-aware, and non-guaranteeing")
    print("PASS: evidence lifecycle and production-readiness gates present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
