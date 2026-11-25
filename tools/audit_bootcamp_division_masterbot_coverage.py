"""Audit 55-division and 65-MasterBot Bootcamp delivery without guessing ownership."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def audit(registry: dict[str, Any], crosswalk: dict[str, Any], course: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    bots = registry.get("divisions")
    domains = crosswalk.get("domains")
    mapped_bots = crosswalk.get("masterbots")
    delivery = course.get("delivery", {})
    division_assignments = delivery.get("division_assignments")
    masterbot_assignments = delivery.get("masterbot_assignments")
    modules = course.get("modules")

    if not isinstance(bots, list) or len(bots) != 65:
        errors.append("canonical MasterBot registry must contain exactly 65 records")
        bots = bots if isinstance(bots, list) else []
    if not isinstance(domains, list) or len(domains) != 55:
        errors.append("division crosswalk must contain exactly 55 domain records")
        domains = domains if isinstance(domains, list) else []
    if not isinstance(mapped_bots, list) or len(mapped_bots) != 65:
        errors.append("crosswalk must contain exactly 65 MasterBot ownership records")
        mapped_bots = mapped_bots if isinstance(mapped_bots, list) else []
    if not isinstance(division_assignments, list) or len(division_assignments) != 55:
        errors.append("course must assign shared foundation to exactly 55 divisions")
        division_assignments = division_assignments if isinstance(division_assignments, list) else []
    if not isinstance(masterbot_assignments, list) or len(masterbot_assignments) != 65:
        errors.append("course must assign shared foundation to exactly 65 MasterBot lanes")
        masterbot_assignments = masterbot_assignments if isinstance(masterbot_assignments, list) else []

    bot_by_id = {row.get("id"): row for row in bots if isinstance(row, dict)}
    domain_by_id = {row.get("domain_id"): row for row in domains if isinstance(row, dict)}
    owner_by_id = {row.get("masterbot_id"): row for row in mapped_bots if isinstance(row, dict)}
    division_by_id = {row.get("domain_id"): row for row in division_assignments if isinstance(row, dict)}
    assignment_by_id = {row.get("masterbot_id"): row for row in masterbot_assignments if isinstance(row, dict)}

    if len(bot_by_id) != len(bots):
        errors.append("MasterBot registry contains duplicate or missing IDs")
    if len(domain_by_id) != len(domains):
        errors.append("division crosswalk contains duplicate or missing domain IDs")
    if len(owner_by_id) != len(mapped_bots):
        errors.append("crosswalk MasterBot rows contain duplicate or missing IDs")
    if len(division_by_id) != len(division_assignments):
        errors.append("division assignment rows contain duplicate or missing domain IDs")
    if len(assignment_by_id) != len(masterbot_assignments):
        errors.append("MasterBot assignment rows contain duplicate or missing IDs")

    for bot_id, bot in bot_by_id.items():
        owner = owner_by_id.get(bot_id)
        assignment = assignment_by_id.get(bot_id)
        if owner is None or assignment is None:
            errors.append(f"MasterBot {bot_id} is missing crosswalk or course assignment")
            continue
        if owner.get("masterbot_name") != bot.get("name") or assignment.get("masterbot_name") != bot.get("name"):
            errors.append(f"MasterBot {bot_id} name mismatch across registry/crosswalk/course")
        if assignment.get("shared_foundation") is not True:
            errors.append(f"MasterBot {bot_id} is missing shared AI/model foundation")
        if owner.get("mapping_status") != assignment.get("mapping_status"):
            errors.append(f"MasterBot {bot_id} mapping status differs from reviewed crosswalk")
        approved = owner.get("owner_approval") is True
        if not approved and assignment.get("specialist_ownership_review_required") is not True:
            errors.append(f"MasterBot {bot_id} bypasses owner review without approval")
        if approved and not str(owner.get("approval_evidence_ref", "")).strip():
            errors.append(f"MasterBot {bot_id} approval lacks evidence reference")

    for domain_id, domain in domain_by_id.items():
        assignment = division_by_id.get(domain_id)
        if assignment is None:
            errors.append(f"division {domain_id} is missing shared foundation assignment")
            continue
        if assignment.get("domain_name") != domain.get("domain_name"):
            errors.append(f"division {domain_id} name mismatch across crosswalk/course")
        if assignment.get("delivery") != "shared_ai_model_literacy_foundation":
            errors.append(f"division {domain_id} is missing shared AI/model foundation")
        approved = domain.get("owner_approval") is True
        if not approved and assignment.get("specialist_assignment") != "review_required_before_owner_specific_work":
            errors.append(f"division {domain_id} bypasses specialist owner review without approval")
        if approved and not str(domain.get("approval_evidence_ref", "")).strip():
            errors.append(f"division {domain_id} approval lacks evidence reference")

    if not isinstance(modules, list) or not modules:
        errors.append("course modules must be a non-empty ordered array")
        modules = modules if isinstance(modules, list) else []
    module_ids = [row.get("id") for row in modules if isinstance(row, dict)]
    if len(module_ids) != len(modules) or len(module_ids) != len(set(module_ids)):
        errors.append("course module IDs must be present and unique")
    if module_ids and module_ids != [f"LLM25-{i:02d}" for i in range(1, len(module_ids) + 1)]:
        errors.append("course modules must be in contiguous LLM25 order")

    approved_domains = sum(1 for row in domains if isinstance(row, dict) and row.get("owner_approval") is True)
    approved_bots = sum(1 for row in mapped_bots if isinstance(row, dict) and row.get("owner_approval") is True)
    unresolved_domains = sum(1 for row in domains if isinstance(row, dict) and row.get("mapping_status") == "unresolved")
    unresolved_bots = sum(1 for row in mapped_bots if isinstance(row, dict) and row.get("mapping_status") == "unresolved")
    if approved_domains < len(domains) or approved_bots < len(mapped_bots):
        warnings.append("specialist ownership remains pending; shared foundations may be taught, but owner-specific routing must remain gated")

    return {
        "schema": "dreamco.bootcamp_division_masterbot_coverage_audit.v1",
        "status": "structural_errors" if errors else ("coverage_present_ownership_pending" if warnings else "coverage_and_ownership_verified"),
        "canonical_divisions": len(domains),
        "division_foundation_assignments": len(division_assignments),
        "masterbot_lanes": len(bots),
        "masterbot_foundation_assignments": len(masterbot_assignments),
        "course_modules": len(modules),
        "approved_division_owners": approved_domains,
        "unresolved_divisions": unresolved_domains,
        "approved_masterbot_owners": approved_bots,
        "unresolved_masterbots": unresolved_bots,
        "errors": errors,
        "warnings": warnings,
        "specialist_routing_authorized_by_audit": False,
        "mastery_claim": False,
        "truth_boundary": "This audit verifies curriculum assignment and ownership-gate integrity only. It does not certify domain-specific lessons, assessments, execution adapters, competence, or mastery.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "config/masterbot-65-registry.json")
    parser.add_argument("--crosswalk", type=Path, default=ROOT / "config/generated/masterbot-55-domain-crosswalk.json")
    parser.add_argument("--course", type=Path, default=ROOT / "config/buddy-25m-cpu-llm-course.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(*(json.loads(path.read_text(encoding="utf-8")) for path in (args.registry, args.crosswalk, args.course)))
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
