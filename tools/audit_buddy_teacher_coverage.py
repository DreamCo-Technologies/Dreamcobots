#!/usr/bin/env python3
"""Read-only, fail-closed inventory of Buddy model and division evaluation gaps.

No model inference, training, network calls, credentials, or workflow dispatches.
Registry declarations are never counted as completed independent evaluations.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "production": "config/generated/production-evidence-ledger.json",
    "masterbots": "config/masterbot-65-registry.json",
    "tasks": "config/buddy-benchmark-task-registry.json",
    "suites": "config/buddy-model-benchmarks.json",
    "models": "config/buddy-model-selection-registry.json",
    "students": "config/buddy-student-adapter-registry.json",
    "distill": "config/buddy-distill-contract.json",
}

# Proposed fixtures, not tests, training examples, or independently graded holdouts.
# A human must approve rights, leakage controls and scoring before evaluation.
SEEDS = {
    "DreamCodeLab": ("coding", "Repair a bug in an original toy Python package with hidden regression tests."),
    "DreamOps": ("debugging", "Diagnose a synthetic CI failure and propose a minimal reversible patch."),
    "DreamData": ("sql_data", "Answer a SQL aggregation question against a synthetic schema."),
    "DreamFinance": ("finance", "Reconcile a fictional cash-flow table and show arithmetic."),
    "DreamRealEstate": ("real_estate", "Calculate a fictional rental property's cap rate and assumptions."),
    "DreamSalesPro": ("sales", "Draft permissioned outreach for a fictional opt-in customer."),
    "DreamMarket": ("marketing", "Compare two fictional campaign plans without inventing results."),
    "DreamEducation": ("education", "Score a synthetic answer with a fixed rubric and explain errors."),
    "DreamScience": ("science", "Check units and uncertainty in an original lab calculation."),
    "DreamAIInfra": ("tool_calling", "Select a simulated tool from an allowlist and validate arguments."),
    "DreamAgents": ("orchestration", "Plan a multi-step sandbox task with approval checkpoints."),
    "DreamCyber": ("security", "Identify an injection flaw in a purpose-built toy example."),
    "DreamArts": ("multimedia", "Describe a rights-cleared synthetic image with uncertainty."),
    "DreamContent": ("language", "Summarize an original short passage without unsupported facts."),
    "DreamHealth": ("safety", "Distinguish general education from personal medical advice."),
    "DreamLegal": ("research", "Identify when a hypothetical legal question needs current sources."),
    "DreamRobotics": ("devices", "Reject an unauthorized simulated actuator command."),
    "DreamAgriculture": ("science", "Calculate irrigation volume from fictional field measurements."),
    "DreamPayments": ("finance", "Detect mismatches in synthetic transaction ledger rows."),
    "DreamPersonalCare": ("accessibility", "Rewrite a synthetic instruction in plain accessible language."),
    "CommandCore": ("orchestration", "Route a fictional three-step support request to simulated approved adapters with stop conditions."),
    "DreamAdmin": ("reasoning", "Prioritize fictional administrative tickets using an explicit impact-and-urgency rubric."),
    "DreamAffiliate": ("marketing", "Compare disclosure-compliant affiliate copy for a fictional, consented campaign."),
    "DreamAgency": ("sales", "Prepare a fictional service proposal with scope, deliverables, and transparent pricing."),
    "DreamAutomation": ("tool_calling", "Reject a simulated automation step that lacks an exact-action approval token."),
    "DreamBizLaunch": ("business", "Calculate break-even sales for a fictional low-cost business using stated assumptions."),
    "DreamConstruction": ("math", "Estimate fictional material quantities with unit conversions and waste allowances."),
    "DreamCrypto": ("finance", "Explain volatility and custody risks using synthetic historical-looking price data."),
    "DreamCustIntel": ("research", "Cluster synthetic consented customer feedback without exposing personal identifiers."),
    "DreamDecision": ("reasoning", "Compare three fictional options with a weighted decision matrix and sensitivity check."),
    "DreamEmpire": ("orchestration", "Allocate a fictional compute budget across simulated divisions with explicit caps."),
    "DreamEntFinance": ("finance", "Reconcile a synthetic departmental budget and flag unsupported expense assumptions."),
    "DreamFlow": ("orchestration", "Detect a dependency cycle in a toy workflow graph and propose a reversible correction."),
    "DreamFood": ("safety", "Identify missing allergy labels in a fictional menu without making medical claims."),
    "DreamFoundry": ("science", "Rank fictional invention hypotheses by testability and evidence requirements."),
    "DreamFranchise": ("business", "Check a fictional franchise cash-flow projection for unrealistic growth assumptions."),
    "DreamGlobal": ("language", "Translate an original fictional customer notice while preserving safety caveats."),
    "DreamInfluence": ("marketing", "Evaluate fictional creator-campaign disclosures and non-deceptive claims."),
    "DreamIntegrations": ("tool_calling", "Map a toy API response into a schema and reject unknown permission scopes."),
    "DreamLicensing": ("legal", "Classify fictional asset license clauses and flag when expert review is needed."),
    "DreamLoans": ("finance", "Calculate a fictional amortization schedule and show APR assumptions."),
    "DreamMaintenance": ("debugging", "Diagnose a simulated equipment-alert log and recommend non-destructive checks."),
    "DreamMilitary": ("safety", "Plan non-operational disaster-relief inventory distribution using fictional supplies."),
    "DreamPlanetary": ("science", "Check units in a fictional orbital-period calculation and report uncertainty."),
    "DreamProServices": ("accessibility", "Rewrite a fictional client onboarding checklist for plain-language accessibility."),
    "DreamProduction": ("multimedia", "Produce a shot list from an original rights-cleared fictional script."),
    "DreamProtection": ("security", "Spot insecure default settings in a toy configuration without live exploitation."),
    "DreamRetail": ("finance", "Reconcile a fictional inventory ledger and calculate gross margin."),
    "DreamSaaS": ("coding", "Implement a small toy REST endpoint with input validation and offline tests."),
    "DreamSocial": ("safety", "Moderate synthetic community posts using a transparent non-discriminatory rubric."),
    "DreamStreaming": ("multimedia", "Create accessible captions for an original synthetic transcript."),
    "DreamTrade": ("finance", "Explain a simulated import invoice including fictional exchange-rate assumptions."),
    "DreamTransport": ("math", "Estimate route fuel use for fictional deliveries with unit and capacity constraints."),
    "DreamTravel": ("research", "Compare fictional itineraries under a budget with explicit accessibility needs."),
    "GameTitan": ("coding", "Fix a deterministic toy game-state bug and verify replay consistency."),
}

# Design crosswalk only. These are plausible starting suites, NOT proven task
# coverage: a generic code or research suite cannot certify a specialist.
TASK_SUITE_DESIGN_LINKS = {
    "reasoning": ("arithmetic_reasoning",),
    "coding": ("code_generation", "code_repair"),
    "python": ("code_generation", "code_repair"),
    "tool_use": ("tool_selection",),
    "retrieval": ("long_context_retrieval", "grounded_research"),
    "long_context": ("long_context_retrieval",),
    "factuality": ("grounded_research",),
    "orchestration": ("orchestration_approval",),
    "sales": ("sales_opt_out",),
    "marketing": ("marketing_claim_evidence",),
    "education": ("education_feedback",),
    "science": ("science_lab_units",),
    "safety": ("safety_boundary",),
    "sql": ("sql_result_reasoning",),
    "sql_data": ("sql_result_reasoning",),
}

# Human-reviewable vocabulary proposals, not executable or validated routes.
MODEL_TYPE_ALIAS_PROPOSALS = {
    "coding": ("code",), "python": ("code",),
    "sql": ("data",), "spreadsheets": ("data",),
    "retrieval": ("research",), "factuality": ("research",),
    "agentic_completion": ("plan",),
}


class AuditError(ValueError):
    """A registry cannot be safely audited."""


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict:
    """Reject duplicate registry keys, including nested truth/receipt fields.

    Standard json.loads silently uses the final value, hiding contradictory
    declarations such as trained_weights_exist=true followed by false.
    """
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditError("duplicate JSON key in registry")
        result[key] = value
    return result


def _identifier_fold(value: str) -> str:
    """Detect visually equivalent identifiers without rewriting stored IDs."""
    return unicodedata.normalize("NFKC", value.strip()).casefold()


def _reject_nonfinite_constant(value: str) -> None:
    """Python's JSON parser otherwise accepts NaN and Infinity as extensions."""
    raise AuditError(f"non-finite JSON constant {value} in registry")


def _unique(rows: list, key: str, source: str) -> list:
    if not isinstance(rows, list):
        raise AuditError(f"{source}: expected a list")
    values = []
    for row in rows:
        value = row.get(key) if isinstance(row, dict) else row if key == "self" else None
        if not isinstance(value, str) or not value.strip():
            raise AuditError(f"{source}: missing {key}")
        values.append(value)
    if len(values) != len({_identifier_fold(value) for value in values}):
        raise AuditError(f"{source}: duplicate {key} after normalization")
    return values


def _has_pinned_gate_receipt(root: Path, gate: dict) -> bool:
    """Require an in-repository, content-addressed receipt before readiness.

    This verifies receipt bytes, NOT the underlying test's independence or
    validity. A matching digest is necessary, never sufficient, for promotion.
    """
    relative = gate.get("evidence")
    digest = gate.get("receipt_sha256")
    if (not isinstance(relative, str) or not relative.strip()
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None):
        return False
    try:
        root_path = root.resolve()
        receipt = (root_path / relative).resolve()
        if not receipt.is_relative_to(root_path) or not receipt.is_file():
            return False
        if receipt.stat().st_size > 10_000_000:
            return False
        return sha256(receipt.read_bytes()).hexdigest() == digest.lower()
    except OSError:
        return False


def audit(root: Path = ROOT) -> dict:
    data = {}
    for name, relative in SOURCES.items():
        path = root / relative
        try:
            data[name] = json.loads(path.read_text(encoding="utf-8"),
                                    object_pairs_hook=_reject_duplicate_json_keys,
                                    parse_constant=_reject_nonfinite_constant)
        except (OSError, ValueError) as exc:
            raise AuditError(f"{relative}: {exc}") from exc
    divisions = _unique(data["production"]["divisions"], "name", SOURCES["production"])
    masterbots = _unique(data["masterbots"]["divisions"], "name", SOURCES["masterbots"])
    tasks = _unique(data["tasks"]["tasks"], "self", SOURCES["tasks"])
    suites = _unique(data["suites"]["suites"], "id", SOURCES["suites"])
    models = _unique(data["models"]["models"], "id", SOURCES["models"])
    students = _unique(data["students"]["adapters"], "id", SOURCES["students"])
    runs = data["tasks"].get("runs")
    if type(runs) is not int or runs < 0:
        raise AuditError("benchmark runs must be a nonnegative integer")
    student_truth = data["students"]["truth"]
    distill_truth = data["distill"].get("truth", {})
    for label, value in (
        ("student trained_weights_exist", student_truth.get("trained_weights_exist")),
        ("distill trained_weights_exist", distill_truth.get("trained_weights_exist", False)),
        ("distill distill_runs_exist", distill_truth.get("distill_runs_exist", False)),
    ):
        if type(value) is not bool:
            raise AuditError(f"{label} must be a boolean")
    if student_truth["trained_weights_exist"] and not students:
        raise AuditError("trained weights claimed without any registered student adapter")
    if data["distill"].get("status") == "contract_draft_no_runs" and distill_truth.get("distill_runs_exist"):
        raise AuditError("distillation run claim contradicts no-runs contract status")
    catalog_types = set()
    for model in data["models"]["models"]:
        model_types = model.get("task_types", [])
        if not isinstance(model_types, list) or any(not isinstance(x, str) or not x.strip() for x in model_types):
            raise AuditError("model task_types must be a list of nonempty strings")
        if len(model_types) != len({_identifier_fold(value) for value in model_types}):
            raise AuditError("duplicate model task_type after normalization")
        catalog_types.update(model_types)
    summary = data["production"]["summary"]
    if type(summary["real_divisions"]) is not int or summary["real_divisions"] != len(divisions):
        raise AuditError("production ledger division count disagrees with entries")
    if "canonical_divisions" in summary and "supplemental_divisions" in summary:
        canonical, supplemental = summary["canonical_divisions"], summary["supplemental_divisions"]
        if any(type(n) is not int or n < 0 for n in (canonical, supplemental)):
            raise AuditError("production ledger division subtotals must be nonnegative integers")
        if canonical + supplemental != len(divisions):
            raise AuditError("production ledger division subtotals disagree with entries")
    for division in data["production"]["divisions"]:
        if type(division.get("production_ready")) is not bool:
            raise AuditError("division production_ready must be a boolean")
        if division["production_ready"]:
            # A readiness flag alone is not evidence: every gate must have
            # explicitly passed, carry pinned receipts, and have no blockers.
            gates = division.get("gates")
            if (not isinstance(gates, list) or not gates
                    or any(not isinstance(gate, dict) or gate.get("passed") is not True
                           or not _has_pinned_gate_receipt(root, gate)
                           for gate in gates)
                    or division.get("blockers") != []):
                raise AuditError("production_ready division has missing or failed gates or blockers")
    ledger_weights = summary.get("trained_weight_artifacts")
    if ledger_weights is not None:
        if type(ledger_weights) is not int or ledger_weights < 0:
            raise AuditError("trained_weight_artifacts must be a nonnegative integer")
        if ledger_weights == 0 and (
            student_truth["trained_weights_exist"] or distill_truth.get("trained_weights_exist")
        ):
            raise AuditError("trained weights claimed while production ledger reports zero artifacts")
    if (type(data["masterbots"]["canonical_count"]) is not int
            or data["masterbots"]["canonical_count"] != len(masterbots)):
        raise AuditError("MasterBot registry count disagrees with entries")
    if (type(summary["production_ready_divisions"]) is not int
            or summary["production_ready_divisions"] != sum(
                d["production_ready"] for d in data["production"]["divisions"])):
        raise AuditError("production readiness count disagrees with entries")

    # Declared catalog routes are not proof of availability, quality, or successful calls.
    routes = []
    for task in sorted(tasks):
        candidates = sorted(m["id"] for m in data["models"]["models"] if task in m.get("task_types", []))
        aliases = MODEL_TYPE_ALIAS_PROPOSALS.get(task, ())
        suggested = sorted(m["id"] for m in data["models"]["models"]
                           if any(alias in m.get("task_types", []) for alias in aliases))
        proposed_suites = [suite for suite in TASK_SUITE_DESIGN_LINKS.get(task, ())
                           if suite in suites]
        routes.append({
            "task": task,
            "declared_candidate_model_ids": candidates,
            "suggested_alias_model_ids_unverified": suggested,
            "candidate_suite_ids_design_only": proposed_suites,
            "needs_dedicated_suite_design": not bool(proposed_suites),
            "independently_verified_model_ids": [],
            "status": "unverified",
        })
    # Reconcile independently maintained registries by normalized identity.
    # Cosmetic casing, surrounding whitespace and Unicode width differences
    # are not evidence of a missing division. Preserve source spellings in
    # the report so maintainers can review and standardize them deliberately.
    actual_by_fold = {_identifier_fold(name): name for name in divisions}
    masterbot_by_fold = {_identifier_fold(name): name for name in masterbots}
    shared_folds = sorted(set(actual_by_fold) & set(masterbot_by_fold))
    identifier_variants = [
        {"actual_division": actual_by_fold[key], "masterbot_division": masterbot_by_fold[key]}
        for key in shared_folds if actual_by_fold[key] != masterbot_by_fold[key]
    ]
    division_rows = []
    for division in sorted(divisions):
        seed = SEEDS.get(division)
        family = seed[0] if seed else None
        # Exact spelling only: a plausible domain-to-task mapping is not an
        # executable route, and an alias must not silently count as coverage.
        exact_model_ids = sorted(
            model["id"] for model in data["models"]["models"]
            if family is not None and family in model.get("task_types", [])
        )
        division_rows.append({
            "division": division,
            "suggested_task_family": family,
            "suggested_fixture": seed[1] if seed else None,
            "task_family_has_exact_benchmark_label": family in tasks if family else False,
            "declared_exact_catalog_model_ids_unverified": exact_model_ids,
            "independent_holdout_receipt": None,
            "evaluated_model_revision": None,
            "status": "fixture_design_only" if seed else "representative_task_needed",
        })
    return {
        "schema": "dreamco.buddy_teacher_coverage_audit.v1",
        "scope": "Read-only registry inventory, not execution or model performance evidence",
        "sources": SOURCES,
        "summary": {
            "actual_divisions": len(divisions),
            "masterbot_taxonomy_entries": len(masterbots),
            "masterbot_only_names": sorted(name for key, name in masterbot_by_fold.items()
                                           if key not in actual_by_fold),
            "actual_only_names": sorted(name for key, name in actual_by_fold.items()
                                        if key not in masterbot_by_fold),
            "cross_registry_identifier_variants": identifier_variants,
            "representative_fixture_suggestions": sum(d["suggested_fixture"] is not None for d in division_rows),
            "divisions_needing_fixture_design": sum(d["suggested_fixture"] is None for d in division_rows),
            "division_task_families_without_exact_benchmark_label": sorted({
                d["suggested_task_family"] for d in division_rows
                if d["suggested_task_family"] and not d["task_family_has_exact_benchmark_label"]
            }),
            "divisions_without_exact_benchmark_task_label": sorted(
                d["division"] for d in division_rows
                if not d["task_family_has_exact_benchmark_label"]
            ),
            "divisions_without_exact_declared_model_route": sorted(
                d["division"] for d in division_rows
                if not d["declared_exact_catalog_model_ids_unverified"]
            ),
            "registered_benchmark_task_labels": len(tasks),
            "benchmark_suite_definitions": len(suites),
            "catalog_model_ids": len(models),
            "catalog_model_task_types_not_in_benchmark_registry": sorted(catalog_types - set(tasks)),
            "benchmark_tasks_without_exact_catalog_type": sorted(set(tasks) - catalog_types),
            "benchmark_tasks_without_candidate_suite_design": sorted(
                task for task in tasks if not any(s in suites for s in TASK_SUITE_DESIGN_LINKS.get(task, ()))
            ),
            "student_adapter_entries": len(students),
            "reported_benchmark_runs": data["tasks"]["runs"],
            "trained_weights_claimed": student_truth["trained_weights_exist"],
            "distill_trained_weights_claimed": distill_truth.get("trained_weights_exist", False),
            "distill_runs_claimed": distill_truth.get("distill_runs_exist", False),
            "ledger_trained_weight_artifacts": ledger_weights,
            "distill_contract_status": data["distill"].get("status", "unknown"),
            "independently_verified_routes_in_this_audit": 0,
            "independent_holdout_receipts_in_this_audit": 0,
            "production_ready_divisions_in_ledger": summary["production_ready_divisions"],
        },
        "task_routes": routes,
        "division_coverage": division_rows,
        "promotion_policy": "No promotion without consent, source rights, isolated holdout, independent grading, safety regression, artifact hashes, and owner approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="Optional report path (never writes into a model registry)")
    args = parser.parse_args()
    try:
        report = audit(args.root)
    except (AuditError, KeyError, TypeError) as exc:
        parser.exit(2, f"coverage audit blocked: {exc}\n")
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
