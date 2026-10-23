#!/usr/bin/env python3
"""Read-only, fail-closed inventory of Buddy model and division evaluation gaps.

No model inference, training, network calls, credentials, or workflow dispatches.
Registry declarations are never counted as completed independent evaluations.
"""
from __future__ import annotations

import argparse
import json
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
    "safety": ("safety_boundary",),
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


def _unique(rows: list, key: str, source: str) -> list:
    if not isinstance(rows, list):
        raise AuditError(f"{source}: expected a list")
    values = []
    for row in rows:
        value = row.get(key) if isinstance(row, dict) else row if key == "self" else None
        if not isinstance(value, str) or not value.strip():
            raise AuditError(f"{source}: missing {key}")
        values.append(value)
    if len(values) != len(set(values)):
        raise AuditError(f"{source}: duplicate {key}")
    return values


def audit(root: Path = ROOT) -> dict:
    data = {}
    for name, relative in SOURCES.items():
        path = root / relative
        try:
            data[name] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise AuditError(f"{relative}: {exc}") from exc
    divisions = _unique(data["production"]["divisions"], "name", SOURCES["production"])
    masterbots = _unique(data["masterbots"]["divisions"], "name", SOURCES["masterbots"])
    tasks = _unique(data["tasks"]["tasks"], "self", SOURCES["tasks"])
    suites = _unique(data["suites"]["suites"], "id", SOURCES["suites"])
    models = _unique(data["models"]["models"], "id", SOURCES["models"])
    students = _unique(data["students"]["adapters"], "id", SOURCES["students"])
    if not isinstance(data["tasks"].get("runs"), int) or data["tasks"]["runs"] < 0:
        raise AuditError("benchmark runs must be a nonnegative integer")
    if data["students"]["truth"].get("trained_weights_exist") and not students:
        raise AuditError("trained weights claimed without any registered student adapter")
    if data["distill"].get("status") == "contract_draft_no_runs" and data["distill"].get("truth", {}).get("distill_runs_exist"):
        raise AuditError("distillation run claim contradicts no-runs contract status")
    catalog_types = set()
    for model in data["models"]["models"]:
        model_types = model.get("task_types", [])
        if not isinstance(model_types, list) or any(not isinstance(x, str) or not x.strip() for x in model_types):
            raise AuditError("model task_types must be a list of nonempty strings")
        catalog_types.update(model_types)
    summary = data["production"]["summary"]
    if summary["real_divisions"] != len(divisions):
        raise AuditError("production ledger division count disagrees with entries")
    if data["masterbots"]["canonical_count"] != len(masterbots):
        raise AuditError("MasterBot registry count disagrees with entries")
    if summary["production_ready_divisions"] != sum(bool(d["production_ready"]) for d in data["production"]["divisions"]):
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
    division_rows = []
    for division in sorted(divisions):
        seed = SEEDS.get(division)
        division_rows.append({
            "division": division,
            "suggested_task_family": seed[0] if seed else None,
            "suggested_fixture": seed[1] if seed else None,
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
            "masterbot_only_names": sorted(set(masterbots) - set(divisions)),
            "actual_only_names": sorted(set(divisions) - set(masterbots)),
            "representative_fixture_suggestions": sum(d["suggested_fixture"] is not None for d in division_rows),
            "divisions_needing_fixture_design": sum(d["suggested_fixture"] is None for d in division_rows),
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
            "trained_weights_claimed": data["students"]["truth"].get("trained_weights_exist", False),
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
