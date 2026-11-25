"""Build an auditable first-party data and Bootcamp plan for all 65 MasterBots.

This creates plans and manifests only. It never invents examples, downloads data,
approves rights, starts training, or changes model weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "masterbots": ROOT / "config/masterbot-65-registry.json",
    "tasks": ROOT / "config/huggingface-task-taxonomy.json",
    "taxonomy_routes": ROOT / "config/generated/division-huggingface-taxonomy-map.json",
    "resource_map": ROOT / "config/generated/division-resource-readiness-map.json",
    "dataset_policy": ROOT / "config/buddy-dataset-routing-policy.json",
    "source_registry": ROOT / "config/dreamco-training-source-registry.json",
    "provenance_policy": ROOT / "config/buddy-training-data-provenance-policy.json",
    "university": ROOT / "config/buddy-university-curriculum.json",
    "freecodecamp": ROOT / "config/freecodecamp-complete-learning-path.json",
    "workforce": ROOT / "config/buddy-workforce-entrepreneurship-bootcamp.json",
    "government": ROOT / "config/buddy-government-community-enterprise-curriculum.json",
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
    source_registry = configs["source_registry"]
    bootcamp = configs["bootcamp"]
    university = configs.get("university", {})
    university_domains = university.get("knowledge_domains", [])
    university_levels = university.get("academic_structure", {}).get("levels", [])
    shared_core = university.get("shared_core", {}).get("required_for_all_divisions", [])
    if university and (len(university_domains) != 45 or len(university_levels) != 4 or len(shared_core) != 10):
        raise ValueError("Buddy University must define 45 domains, four levels and ten shared foundation courses")
    domain_ids = {str(x.get("id")) for x in university_domains}
    university_course_ids = [f"UNI-{str(domain.get('id')).upper()}-{str(level.get('level'))}"
                             for domain in university_domains for level in university_levels]
    shared_core_course_ids = ["CORE-" + __import__("re").sub(r"[^A-Z0-9]+", "-", str(x).upper()).strip("-")
                              for x in shared_core]
    fcc = configs.get("freecodecamp", {})
    fcc_inventory = fcc.get("official_platform_inventory", {})
    fcc_track_count = len(fcc.get("specialist_track_details", [])) + len(fcc_inventory.get("core_certifications", [])) + len(fcc_inventory.get("additional_certifications", []))
    fcc_video_categories = fcc.get("video_learning_tracks", [])
    workforce_tracks = configs.get("workforce", {}).get("training_paths", [])
    government = configs.get("government", {})
    def _tokens(value: str) -> set[str]:
        expanded = re.sub(r"([a-z])([A-Z])", r"\\1 \\2", value)
        return {x.lower() for x in re.findall(r"[a-z0-9]+", expanded.lower())
                if len(x) > 2 and x.lower() not in {"dream", "and", "the", "for", "with", "from"}}
    def _domain_routes(bot: dict[str, Any], route: dict[str, Any]) -> list[dict[str, Any]]:
        lane_terms = " ".join([bot.get("name", ""), *route.get("subject_terms", []), *route.get("search_queries", [])])
        lane_tokens = _tokens(lane_terms)
        ranked = []
        for domain in university_domains:
            domain_tokens = _tokens(str(domain.get("id", "")) + " " + str(domain.get("scope", "")))
            score = len(lane_tokens & domain_tokens)
            if score:
                ranked.append((score, str(domain.get("id"))))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [{"domain_id": domain_id, "score": score, "mapping_status": "suggested_requires_owner_review",
                 "course_ids": [f"UNI-{domain_id.upper()}-{str(level.get('level'))}" for level in university_levels]}
                for score, domain_id in ranked[:3]]
    source_records = configs["source_registry"].get("source_families", [])
    source_ids = [record.get("id") for record in source_records if isinstance(record, dict)]
    if len(source_records) != 9 or len(source_ids) != 9 or len(set(source_ids)) != 9:
        raise ValueError("the governed source registry must contain nine uniquely identified source families")
    source_types = source_ids
    planes = policy["architecture"]["planes"]
    shared = policy["division_routing"]["shared_foundation_categories"]
    source_types = list(dict.fromkeys(source_types))
    source_family_records = source_registry.get("source_families", [])
    source_family_ids = [item.get("id") for item in source_family_records]
    if not source_family_ids or any(not isinstance(item, str) or not item for item in source_family_ids):
        raise ValueError("source registry requires stable source-family IDs")
    if len(source_family_ids) != len(set(source_family_ids)):
        raise ValueError("source registry source-family IDs must be unique")
    adapter_coverage = source_registry.get("adapter_coverage", {})
    active_adapters = adapter_coverage.get("metadata_discovery_implemented", {})
    if not isinstance(active_adapters, dict) or not active_adapters:
        raise ValueError("source registry must distinguish implemented metadata adapters")
    from buddy.datasets import sources as dataset_sources
    for source_id, function_names in active_adapters.items():
        if not isinstance(function_names, list) or not function_names:
            raise ValueError(f"metadata adapter list is invalid for {source_id}")
        for function_name in function_names:
            if not callable(getattr(dataset_sources, function_name, None)):
                raise ValueError(f"source registry adapter {source_id}:{function_name} is not implemented")
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
        crosswalk = route.get("domain_crosswalk", {})
        domain_id = str(crosswalk.get("domain_id", ""))
        university_routes = _domain_routes(bot, route)
        domain_courses = [course_id for item in university_routes for course_id in item["course_ids"]]
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
            "university_domain_id": domain_id if domain_id in domain_ids else None,
            "university_domain_routes": university_routes,
            "university_course_ids": sorted(set(shared_core_course_ids + domain_courses)),
            "shared_core_course_ids": shared_core_course_ids,
            "university_domain_course_ids": domain_courses,
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
            "university_domains": len(university_domains),
            "university_levels": len(university_levels),
            "university_course_blueprints": len(university_course_ids) + len(shared_core_course_ids),
            "shared_core_courses": len(shared_core_course_ids),
            "freecodecamp_tracks": fcc_track_count,
            "freecodecamp_video_subject_categories": len(fcc_video_categories),
            "workforce_venture_tracks": len(workforce_tracks),
            "government_official_sources": len(government.get("official_sources", [])),
            "bootcamp_levels": len(bootcamp.get("curriculum_levels", [])),
            "source_families": len(source_family_records),
            "source_catalog_items": len(source_types),
            "implemented_metadata_adapters": sum(len(items) for items in active_adapters.values()),
            "data_planes": len(planes),
        },
        "source_families": source_types,
        "university": {
            "title": university.get("title"),
            "teacher": university.get("instructional_model", {}).get("teacher", {}),
            "student": university.get("instructional_model", {}).get("student", {}),
            "knowledge_domains": university_domains,
            "academic_levels": university_levels,
            "shared_core_courses": shared_core,
            "course_blueprint_ids": university_course_ids + shared_core_course_ids,
            "course_blueprints_are_not_authored_lessons": True,
        },
        "career_and_public_service": {
            "workforce_tracks": workforce_tracks,
            "government_official_sources": government.get("official_sources", []),
            "procurement_pipeline": government.get("procurement_pipeline", []),
            "grant_pipeline": government.get("grant_pipeline", []),
            "benefit_protections": government.get("benefit_protections", {}),
        },
        "freecodecamp_coverage": {
            "certification_track_count": fcc_track_count,
            "video_subject_categories": fcc_video_categories,
            "full_video_catalog_is_separate_and_must_be_verified": True,
        },
        "source_registry": {
            "version": source_registry.get("version"),
            "source_family_ids": source_family_ids,
            "implemented_metadata_adapters": active_adapters,
            "catalogued_reference_only": adapter_coverage.get("catalogued_reference_only", []),
            "external_file_download": adapter_coverage.get("external_file_download"),
            "external_training_ingestion": adapter_coverage.get("external_training_ingestion"),
        },
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
