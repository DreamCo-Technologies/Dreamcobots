"""Build an auditable first-party data and Bootcamp plan for all 65 MasterBots.

This creates plans and manifests only. It never invents examples, downloads data,
approves rights, starts training, or changes model weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "masterbots": ROOT / "config/masterbot-65-registry.json",
    "tasks": ROOT / "config/huggingface-task-taxonomy.json",
    "taxonomy_routes": ROOT / "config/generated/division-huggingface-taxonomy-map.json",
    "resource_map": ROOT / "config/generated/division-resource-readiness-map.json",
    "dataset_policy": ROOT / "config/buddy-dataset-routing-policy.json",
    "provenance_policy": ROOT / "config/buddy-training-data-provenance-policy.json",
    "source_registry": ROOT / "config/dreamco-training-source-registry.json",
    "bootcamp": ROOT / "config/buddy-bootcamp-program.json",
    "curriculum": ROOT / "config/buddy-bootcamp-curriculum-v1.json",
    "serving_policy": ROOT / "config/buddy-model-serving-policy.json",
}

def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_factory_plan(configs: dict[str, dict[str, Any]], source_hashes: dict[str, str] | None = None) -> dict[str, Any]:
    bots = configs["masterbots"].get("divisions", [])
    tasks = configs["tasks"].get("task_families", [])
    taxonomy = configs["taxonomy_routes"].get("routes", [])
    resources = configs["resource_map"].get("routes", [])
    if len(bots) != 65 or len({int(x["id"]) for x in bots}) != 65:
        raise ValueError("canonical registry must contain 65 unique MasterBots")
    if len(tasks) != 37 or any(not isinstance(x, dict) or not x.get("id") for x in tasks):
        raise ValueError("37 structured task-family records with stable IDs are required")
    task_ids = [x["id"] for x in tasks]
    if len(set(task_ids)) != 37:
        raise ValueError("task-family IDs must be unique")
    if len(taxonomy) != 65 or len(resources) != 65:
        raise ValueError("taxonomy and resource maps must each contain 65 routes")
    taxonomy_by_id = {int(x["masterbot_id"]): x for x in taxonomy}
    resources_by_id = {int(x["masterbot_id"]): x for x in resources}
    bot_ids = {int(x["id"]) for x in bots}
    if set(taxonomy_by_id) != bot_ids or set(resources_by_id) != bot_ids:
        raise ValueError("all route IDs must match the canonical MasterBot registry")
    policy = configs["dataset_policy"]
    bootcamp = configs["bootcamp"]
    source_records = configs["source_registry"].get("source_families", [])
    source_ids = [record.get("id") for record in source_records if isinstance(record, dict)]
    if len(source_records) != 9 or len(source_ids) != 9 or len(set(source_ids)) != 9:
        raise ValueError("the governed source registry must contain nine uniquely identified source families")
    source_types = source_ids
    planes = policy["architecture"]["planes"]
    shared = policy["division_routing"]["shared_foundation_categories"]
    source_types = list(dict.fromkeys(source_types))
    lanes = []
    for bot in sorted(bots, key=lambda x: int(x["id"])):
        mid = int(bot["id"])
        route = taxonomy_by_id[mid]
        resource = resources_by_id[mid]
        task_records = [{
            "task_family_id": task["id"],
            "family": task.get("family", "unspecified"),
            "modality": task.get("modality", "unspecified"),
            "pipeline_tag": task.get("pipeline_tag"),
            "required": True,
            "discovery_source": "Hugging Face taxonomy reference only",
            "rights_status": "REVIEW_REQUIRED",
            "training_status": "NOT_APPROVED",
        } for task in tasks]
        lanes.append({
            "masterbot_id": mid,
            "masterbot_name": bot["name"],
            "lane_id": f"dreamco-owned-lane-{mid:03d}",
            "dataset_namespace": f"dreamco/masterbot-{mid:03d}/datasets/",
            "database_schema": f"dreamco_division_{mid:03d}",
            "model_identity": f"dreamco/{bot['name'].lower()}-mini",
            "model_status": "SPECIFIED_NOT_TRAINED",
            "taxonomy_discovery_lane": route["lane_id"],
            "domain_crosswalk_status": route.get("domain_crosswalk", {}).get("mapping_status", "UNRESOLVED"),
            "owner_review_required": bool(route.get("domain_crosswalk", {}).get("owner_review_required", True)),
            "capability_pack_ids": route.get("capability_pack_ids", []),
            "teacher_model_candidates": "See resource map; candidates require revision, license, safety and access review",
            "resource_readiness": resource.get("readiness_status", "UNKNOWN"),
            "task_families": task_records,
            "dataset_planes": {
                "private_lane": ["dreamco_owned_training", "licensed_training", "user_contributed_opt_in_training"],
                "shared_reference_only": ["public_reference_and_retrieval"],
                "isolated": ["evaluation_only_holdout"],
            },
            "shared_foundation_categories": shared,
            "shared_data_rule": "Share approved schemas, reusable lessons and public references; do not cross-copy division-private rows, labels, holdouts, customer data or weights without explicit rights and owner authorization.",
            "bootcamp_levels": [x["id"] for x in bootcamp.get("curriculum_levels", [])],
            "required_global_task_count": len(task_records),
            "training_approved": False,
            "dataset_ingestion_status": "NOT_INGESTED",
            "training_status": "NOT_RUN",
            "benchmark_status": "NOT_RUN",
            "certification_status": "NOT_CERTIFIED",
        })
    return {
        "schema": "dreamco.first_party_training_factory_plan.v1",
        "status": "PLAN_GENERATED_NO_DATA_INGESTED_NO_TRAINING_RUN",
        "source_hashes": source_hashes or {},
        "coverage": {
            "masterbots": len(lanes),
            "task_families": len(tasks),
            "division_task_assignments": len(lanes) * len(tasks),
            "bootcamp_levels": len(bootcamp.get("curriculum_levels", [])),
            "source_families": len(source_types),
            "data_planes": len(planes),
        },
        "source_families": source_types,
        "data_planes": planes,
        "bootcamp": {
            "name": bootcamp.get("name", "Buddy Bootcamp"),
            "sandbox_layers": [x["id"] for x in bootcamp.get("sandbox_layers", [])],
            "curriculum_levels": bootcamp.get("curriculum_levels", []),
            "score_dimensions": bootcamp.get("bot_scorecard", {}).get("dimensions", []),
            "mastery_requires": configs["curriculum"].get("mastery", {}).get("requires", []),
        },
        "sharing_policy": {
            "shared": ["approved original foundational lessons", "public references", "schemas", "reusable tools", "non-sensitive fixtures"],
            "isolated": ["division-specific training examples", "customer/user data", "private labels", "evaluation holdouts", "checkpoints and weights"],
            "promotion": "A cross-division copy requires provenance, rights/consent review, destination-owner approval and a new dataset version.",
        },
        "truth_boundary": {
            "candidate_discovery_is_not_rights_approval": True,
            "curriculum_is_not_training": True,
            "plan_generation_does_not_create_examples": True,
            "weights_trained": False,
            "production_resources_verified": False,
            "all_lanes_require_dataset_cards_and_split_hashes": True,
        },
        "lanes": lanes,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "artifacts/training-factory/first-party-training-factory-plan.json"))
    args = parser.parse_args()
    configs = {name: _load(path) for name, path in FILES.items()}
    hashes = {name: _hash(path) for name, path in FILES.items()}
    plan = build_factory_plan(configs, hashes)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": plan["status"], "coverage": plan["coverage"], "output": str(target)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
