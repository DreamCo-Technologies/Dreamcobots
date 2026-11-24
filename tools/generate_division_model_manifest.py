#!/usr/bin/env python3
"""Generate an honest registry-derived inventory and lifecycle plan for every division model."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "masterbot-65-registry.json"
POLICY = ROOT / "config" / "division-model-training-policy.json"
OUTPUT = ROOT / "config" / "generated" / "division-model-manifest.json"


def build_manifest(registry: dict, source_text: str, policy: dict | None = None) -> dict:
    divisions = registry.get("divisions")
    if not isinstance(divisions, list) or not divisions:
        raise ValueError("canonical registry must contain a non-empty divisions array")
    ids = [item.get("id") for item in divisions]
    names = [item.get("name") for item in divisions]
    if any(not isinstance(value, int) or value <= 0 for value in ids):
        raise ValueError("every division must have a positive integer id")
    if any(not isinstance(value, str) or not value.strip() for value in names):
        raise ValueError("every division must have a non-empty name")
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        raise ValueError("division ids and names must be unique")
    if registry.get("canonical_count") != len(divisions):
        raise ValueError("canonical_count does not match the registry divisions array")
    if policy is None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if policy.get("schema") != "dreamco.division_model_training_policy.v1":
        raise ValueError("unsupported division model training policy schema")

    records = []
    for division in divisions:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in division["name"]).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        model_id = f"dreamco.division.{slug}"
        checkpoint_template = policy["training"]["checkpoint_key_template"]
        checkpoint_template = checkpoint_template.replace("{division_id:03d}", f"{division['id']:03d}").replace("{model_id}", model_id)
        records.append({
            "division_id": division["id"],
            "division_name": division["name"],
            "resource_bundle_id": policy["resource_bundle"]["id_template"].replace("{division_id:03d}", f"{division['id']:03d}"),
            "resource_bundle_status": policy["resource_bundle"]["status"],
            "required_resource_services": policy["resource_bundle"]["required_services"],
            "model_id": model_id,
            "model_version": policy["identity"]["current_manifest_version"],
            "planned_model_version": policy["identity"]["planned_first_release_version"],
            "lifecycle_state": "planned",
            "ownership_class": "dreamco_first_party_candidate",
            "base_model": None,
            "base_model_selection_status": "PENDING_LICENSE_COMPUTE_AND_BENCHMARK_REVIEW",
            "tokenizer": {
                "mode": policy["tokenizer"]["default_mode"],
                "reference": policy["tokenizer"]["reference_rule"],
                "status": "PENDING_BASE_MODEL_SELECTION",
                "tokenizer_sha256": None,
                "required_evidence": policy["tokenizer"]["required_evidence"]
            },
            "training": {
                "dataset_manifest": None,
                "recipe": policy["training"]["strategy"],
                "checkpoint": None,
                "checkpoint_sha256": None,
                "checkpoint_key_template": checkpoint_template,
                "weights_trained": False,
                "paid_compute_authorized": False,
                "schedule": policy["training"]["schedule"],
                "required_lineage": policy["training"]["required_lineage"],
                "status": "PLAN_ONLY_NOT_STARTED"
            },
            "reverse_engineering_plan": {
                "allowed_practices": policy["reverse_engineering"]["allowed_practices"],
                "blocked_practices": policy["reverse_engineering"]["blocked_practices"],
                "required_output": policy["reverse_engineering"]["required_output"]
            },
            "teacher_plan": {
                "coordinator": policy["teacher_policy"]["coordinator"],
                "teacher_candidates": policy["teacher_policy"]["teacher_candidates"],
                "requirements": policy["teacher_policy"]["requirements"],
                "status": "TEACHER_SELECTION_PENDING_LICENSE_AND_DOMAIN_EVALUATION"
            },
            "evaluation": {
                "suite": policy["evaluation"]["required_suites"],
                "last_result": None,
                "benchmark_status": "NOT_RUN",
                "test_split_used_for_training": False
            },
            "serving": {
                "endpoint": None,
                "deployment_revision": None,
                "runtime_candidates": policy["runtime"]["candidate_modes"],
                "status": "NOT_DEPLOYED"
            },
            "release_evidence": {
                "model_card": None,
                "license_review": None,
                "approval_record": None,
                "independent_review_required": True
            },
            "independence_contract": {
                "division_owned_task_runner": True,
                "division_owned_trainable_weights_or_adapter": True,
                "division_owned_checkpoint_and_optimizer_state": True,
                "division_owned_benchmarks_and_private_holdout": True,
                "tokenizer_policy": "shared only with the pinned base model unless benchmarked division-specific override is approved",
                "buddy_is_coordinator_not_hidden_solver": True
            },
            "truth": "Plan only; no base model selected, no weights trained, no checkpoint created, no endpoint deployed."
        })
    git_blob = f"blob {len(source_text.encode('utf-8'))}\0".encode("ascii") + source_text.encode("utf-8")
    policy_text = json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "dreamco.division_model_manifest.v1",
        "status": "inventory_and_lifecycle_plan_only_not_trained",
        "source_of_truth": "config/masterbot-65-registry.json",
        "source_blob_sha": hashlib.sha1(git_blob).hexdigest(),
        "training_policy_source": "config/division-model-training-policy.json",
        "training_policy_sha256": hashlib.sha256(policy_text).hexdigest(),
        "division_count": len(records),
        "records": records,
        "truth": "Generated per-division lifecycle plans only. Planned model versions, tokenizer rules, schedules, training recipes and evaluation suites do not assert selected base models, actual weights, executed training, benchmark passes, or deployment."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the committed manifest is stale")
    args = parser.parse_args()
    source_text = SOURCE.read_text(encoding="utf-8")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    manifest = build_manifest(json.loads(source_text), source_text, policy)
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("division model manifest is stale; run tools/generate_division_model_manifest.py")
        print(f"division model manifest current: {manifest['division_count']} division lifecycle plans")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} for {manifest['division_count']} division lifecycle plans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
