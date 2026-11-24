#!/usr/bin/env python3
"""Generate one governed small-model curriculum for each of DreamCo's 65 MasterBots."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
POLICY = ROOT / "config/division-model-competitiveness-policy.json"
CROSSWALK = ROOT / "config/generated/masterbot-45-domain-crosswalk.json"
DOMAIN_SOURCE = ROOT / "shared/division-production-contract.ts"
HF_TAXONOMY = ROOT / "config/huggingface-task-taxonomy.v1.json"
OUT = ROOT / "artifacts/division-model-fleet"

PLATFORM_SCOPES = {
    46: ["research methods", "source verification", "citation quality", "literature synthesis"],
    47: ["benchmark design", "statistical evaluation", "leaderboards", "contamination detection"],
    48: ["knowledge graphs", "retrieval", "ontology design", "knowledge quality"],
    49: ["model evolution", "adapter lifecycle", "continual-learning safeguards", "version comparison"],
    50: ["API contracts", "connector interoperability", "integration testing", "event schemas"],
    51: ["formal reasoning", "math", "logic", "calibration"],
    52: ["world models", "spatial reasoning", "environment understanding", "cross-domain simulation"],
    53: ["computer vision", "image understanding", "video understanding", "3D visual tasks"],
    54: ["speech recognition", "speech synthesis", "audio understanding", "audio generation"],
    55: ["human factors", "accessibility", "human-computer interaction", "workforce context"],
    56: ["security engineering", "privacy controls", "threat modeling", "safe tool permissions"],
    57: ["product discovery", "product analytics", "requirements", "product quality"],
    58: ["operations research", "workflow reliability", "capacity planning", "incident response"],
    59: ["strategy", "scenario planning", "decision analysis", "portfolio prioritization"],
    60: ["experiment design", "ablation studies", "reproducibility", "hypothesis testing"],
    61: ["simulation", "digital twins", "agent environments", "simulation validation"],
    62: ["discovery", "classification", "unknown-problem routing", "source discovery"],
    63: ["quality assurance", "test design", "regression analysis", "release evidence"],
    64: ["resource planning", "compute allocation", "data stewardship", "cost optimization"],
    65: ["foresight", "trend analysis", "emerging technology", "long-horizon scenarios"],
}

FREECODECAMP_SOURCES = [
    {
        "title": "Build and Train a 25M Parameter LLM From Scratch on Your CPU",
        "url": "https://www.freecodecamp.org/news/build-and-train-a-25m-parameter-llm-from-scratch-on-your-cpu/",
        "use": "Educational 25M-parameter architecture and training lab; not a production-capability guarantee.",
    },
    {
        "title": "Build and Train a GLM-5.3-Flash Model From Scratch with Python",
        "url": "https://www.freecodecamp.org/news/build-a-glm-53-flash-model-from-scratch-with-python/",
        "use": "Study reference for small-model architecture and training concepts; do not infer proprietary model weights or architecture.",
    },
    {
        "title": "Train Your Own LLM",
        "url": "https://www.freecodecamp.org/news/train-your-own-llm/",
        "use": "Study reference for data preparation, supervised fine-tuning and parameter-efficient adaptation.",
    },
]

HF_SOURCES = [
    {"name": "Hugging Face Tasks", "url": "https://huggingface.co/tasks", "purpose": "task taxonomy and model discovery"},
    {"name": "Hugging Face Datasets", "url": "https://huggingface.co/datasets", "purpose": "dataset discovery and metadata review"},
    {"name": "Hugging Face Hub documentation", "url": "https://huggingface.co/docs/hub", "purpose": "revision pins, repository metadata, dataset cards and gated access"},
    {"name": "Transformers training", "url": "https://huggingface.co/docs/transformers/main/training", "purpose": "fine-tuning workflow"},
    {"name": "Transformers PEFT", "url": "https://huggingface.co/docs/transformers/peft", "purpose": "LoRA/PEFT adapter training"},
    {"name": "Hugging Face Evaluate", "url": "https://huggingface.co/docs/evaluate", "purpose": "evaluation design and reproducibility"},
]

CURRICULUM_SEQUENCE = [
    "Python, data structures, linear algebra, probability and statistics",
    "tokenization, byte-level vocabularies, embeddings and dataset splits",
    "causal language modeling, transformer blocks, attention and positional encoding",
    "training loops, cross-entropy, optimizers, checkpoints and reproducibility",
    "instruction tuning, evaluation, calibration and error analysis",
    "retrieval-augmented generation, tools, APIs and structured outputs",
    "LoRA/QLoRA, adapter isolation, model cards and safe release practices",
    "domain projects, held-out transfer, regression tests and independent review",
]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def load_domain_profiles() -> dict[str, dict]:
    source = DOMAIN_SOURCE.read_text(encoding="utf-8")
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \\{\\n([\\s\\S]*?)^  \\},?$", re.MULTILINE)
    profiles = {}
    for match in pattern.finditer(source):
        name, body = match.group(1), match.group(2)
        if "purpose:" not in body or "focusAreas:" not in body:
            continue
        def scalar(field: str) -> str:
            found = re.search(rf'{field}:\\s*"([^"]+)"', body)
            return found.group(1) if found else ""
        focus = re.search(r"focusAreas:\\s*\\[(.*?)\\]", body, re.DOTALL)
        serves = re.search(r"serves:\\s*\\[(.*?)\\]", body, re.DOTALL)
        profiles[name] = {
            "purpose": scalar("purpose"),
            "serves": re.findall(r'"([^"]+)"', serves.group(1)) if serves else [],
            "outcome": scalar("outcome"),
            "boundary": scalar("boundary"),
            "focus_areas": re.findall(r'"([^"]+)"', focus.group(1)) if focus else [],
        }
    if len(profiles) != 45:
        raise ValueError(f"Expected 45 authoritative domain profiles; found {len(profiles)}")
    return profiles


def build_profiles() -> list[dict]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    taxonomy = json.loads(HF_TAXONOMY.read_text(encoding="utf-8"))
    bots = registry.get("divisions", [])
    if registry.get("canonical_count") != 65 or len(bots) != 65:
        raise ValueError(f"Expected exactly 65 canonical MasterBots; got {len(bots)}")
    if len(crosswalk.get("domains", [])) != 45 or len(crosswalk.get("masterbots", [])) != 65:
        raise ValueError("Expected the authoritative 45-domain/65-MasterBot crosswalk")
    domain_profiles = load_domain_profiles()
    domain_rows = {row["masterbot_id"]: row for row in crosswalk["masterbots"] if row.get("primary_domain_id")}
    domain_by_name = {name: profile for name, profile in domain_profiles.items()}
    task_rows = [task for group in taxonomy["categories"] for task in group["tasks"]]
    if taxonomy.get("counts", {}).get("tasks") != len(task_rows) or len(task_rows) < 40:
        raise ValueError("Hugging Face task taxonomy is incomplete or count-mismatched")
    ids = [str(x.get("id")) for x in bots]
    names = [x.get("name") for x in bots]
    if len(set(ids)) != 65 or len(set(names)) != 65 or any(not n for n in names):
        raise ValueError("MasterBot registry has missing or duplicate IDs/names")
    if len(domain_rows) != 45:
        raise ValueError(f"Expected 45 exact proposed domain matches; found {len(domain_rows)}")

    profiles = []
    for bot in bots:
        masterbot_id = int(bot["id"])
        name = bot["name"]
        ident = f"DCM-{masterbot_id:03d}"
        mapping = domain_rows.get(bot["id"])
        is_domain = mapping is not None
        domain = domain_by_name.get(mapping["primary_domain_name"]) if is_domain else None
        if is_domain and domain is None:
            raise ValueError(f"Crosswalk domain profile missing for {name}")
        assigned_tasks = [task for task in task_rows if task["primary_domain"] == name]
        scope = domain["focus_areas"] if domain else PLATFORM_SCOPES.get(masterbot_id, [])
        if not scope:
            raise ValueError(f"Missing platform-specialist scope for {name}")
        if not is_domain:
            assigned_tasks = [task for task in task_rows if task["shared_masterbot_id"] == masterbot_id]
        profile = {
            "schema": "dreamco.division_model_profile.v2",
            "division_model_id": ident,
            "masterbot_id": masterbot_id,
            "masterbot_name": name,
            "model_role": "domain_division_model" if is_domain else "shared_platform_specialist_model",
            "domain_crosswalk": {
                "status": "PROPOSED_EXACT_NAME_MATCH_REQUIRES_OWNER_REVIEW" if is_domain else "SHARED_PLATFORM_SPECIALIST_NOT_A_BUSINESS_DIVISION",
                "primary_domain_id": mapping["primary_domain_id"] if is_domain else None,
                "primary_domain_name": mapping["primary_domain_name"] if is_domain else None,
                "owner_approval": mapping.get("owner_approval") if is_domain else None,
                "review_required": True,
                "collaborators": [],
            },
            "domain_charter": domain,
            "specialist_scope": scope,
            "hugging_face_task_routes": assigned_tasks,
            "model_identity": {
                "version": "0.0.0",
                "status": "PROFILE_ONLY_NOT_TRAINED",
                "base_model": None,
                "base_model_revision": None,
                "base_model_license": None,
                "adapter_or_checkpoint": None,
                "model_card": None,
            },
            "architecture_plan": {
                "educational_from_scratch_lab": {
                    "target_parameters": 25000000,
                    "compute_target": "CPU_FIRST",
                    "purpose": "Teach the full GPT-style model lifecycle with a reproducible tiny student.",
                    "not_a_claim": "A 25M-parameter educational model is not equivalent to GPT-5 mini, GPT-5, or a production frontier model.",
                },
                "practical_domain_student": {
                    "selection": "benchmark_and_license_select_an_open_weight_small_base_model",
                    "candidate_size_bands": ["0.5B-3B", "3B-8B only when the domain benchmark justifies it"],
                    "adaptation": "isolated LoRA/QLoRA adapter when retrieval/tool improvements do not close a measured gap",
                    "shared_weights_allowed": True,
                    "division_owned_adapter_retrieval_permissions_benchmarks_and_release": True,
                },
                "independence": "The division model must complete its own accepted domain tasks; Buddy routes and teaches but cannot secretly solve the task for a division benchmark.",
            },
            "buddy_teacher_system": {
                "teacher_name": "Buddy Master Teacher",
                "teacher_role": "curriculum orchestrator, source verifier, Socratic tutor, lesson synthesizer, evaluator and remediation planner",
                "teacher_quality_rule": "Select external teacher models per subject only after comparable benchmark, safety, license and cost review; Buddy's teaching quality is measured by learner transfer, not model labels.",
                "sources": FREECODECAMP_SOURCES + HF_SOURCES,
                "shared_lesson_inputs": ["approved_lesson_metadata", "verified_benchmark_deltas", "reusable_test_fixtures", "verified_failure_regressions"],
            },
            "curriculum": {
                "sequence": CURRICULUM_SEQUENCE,
                "domain_objectives": scope,
                "hugging_face_task_ids": [task["id"] for task in assigned_tasks],
                "daily_rotation": "One domain objective plus one relevant Hub task or foundational module per daily lane.",
                "training_unit_contract": ["capability_id", "objective", "lesson", "practice", "sandbox_task", "transfer_task", "rubric", "benchmark", "provenance"],
            },
            "dataset_policy": {
                "discovery_source": "Hugging Face Datasets and other approved public/licensed catalogs",
                "search_queries": [f"{name} {objective} dataset" for objective in scope],
                "required_metadata": taxonomy["dataset_metadata_contract"]["required"],
                "unknown_or_incompatible_rights": "BLOCK",
                "holdout_split_enters_training": False,
                "raw_user_data_enters_shared_training": False,
            },
            "buddy_integration": {
                "orchestrator": "Buddy",
                "queue": "dependency_aware_division_model_training_queue",
                "teacher_route": "buddy_master_teacher",
                "learning_route": "evidence_backed_shared_lesson_bus_with_division_isolation",
                "benchmark_route": "shared_general_suite_plus_private_domain_holdout",
                "failure_recovery_route": "verified_incident_memory_then_sandbox_regression",
                "progress_events": ["curriculum_assigned", "source_reviewed", "lesson_completed", "sandbox_passed", "benchmark_recorded", "remediation_required"],
            },
            "benchmark_plan": {
                "shared_general_suite": policy["benchmark_policy"]["shared_general_suite"],
                "domain_suite": ["expert-authored tasks", "end-to-end workflows", "tool/runtime tasks", "private held-out tasks", "verified failure regressions"],
                "task_specific_hugging_face_suite": [task["id"] for task in assigned_tasks],
                "benchmark_status": "PLAN_DEFINED_NOT_EXECUTED",
            },
            "training": {
                "cadence": "daily_curriculum_and_evaluation_plan",
                "status": "PLAN_ONLY_NOT_TRAINED",
                "weights_trained": False,
                "training_executor_connected": False,
                "paid_compute_authorized": False,
                "default_daily_action": "build_curriculum_review_dataset_metadata_and_run_free_contract_checks",
                "weight_update_requires": ["rights_cleared_pinned_dataset", "approved_compute_budget", "reproducible_baseline", "isolated_train_validation_holdout", "human_training_approval"],
            },
            "promotion": {
                "status": "BLOCKED_NO_EVIDENCE",
                "required_gates": policy["promotion_gate"]["requires"],
                "automatic_production_update": False,
            },
            "evidence": {"tested_commit_sha": None, "baseline": None, "candidate": None, "holdout": None, "regression_run": None, "artifact_hashes": []},
            "next_actions": [
                "review proposed division ownership",
                "discover and rights-check pinned Hub datasets",
                "complete daily Buddy Bootcamp lessons and sandbox exercises",
                "select and benchmark compatible open-weight teacher/student models",
                "measure a reproducible baseline",
                "train only after separate compute and data approval",
            ],
        }
        profiles.append(profile)
    return profiles


def build_manifest() -> dict:
    profiles = build_profiles()
    canonical = json.dumps(profiles, sort_keys=True, separators=(",", ":")).encode()
    domain_count = sum(row["model_role"] == "domain_division_model" for row in profiles)
    platform_count = sum(row["model_role"] == "shared_platform_specialist_model" for row in profiles)
    taxonomy = json.loads(HF_TAXONOMY.read_text(encoding="utf-8"))
    return {
        "schema": "dreamco.division_model_fleet_manifest.v2",
        "profile_count": len(profiles),
        "domain_division_model_count": domain_count,
        "shared_platform_specialist_model_count": platform_count,
        "masterbot_count": len(profiles),
        "hugging_face_task_category_count": taxonomy["counts"]["categories"],
        "hugging_face_task_count": taxonomy["counts"]["tasks"],
        "trained_model_count": 0,
        "mastered_model_count": 0,
        "daily_training_executor_connected": False,
        "daily_curriculum_planning": True,
        "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
        "profiles": profiles,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    if manifest["profile_count"] != 65 or manifest["domain_division_model_count"] != 45 or manifest["shared_platform_specialist_model_count"] != 20:
        raise SystemExit("Expected exactly 45 domain models and 20 shared platform specialist models")
    if args.check:
        print(json.dumps({key: manifest[key] for key in ("profile_count", "domain_division_model_count", "shared_platform_specialist_model_count", "hugging_face_task_count", "trained_model_count", "mastered_model_count")}, indent=2))
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "division-model-fleet.json"
    target.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({"profile_count": manifest["profile_count"], "domain_division_model_count": manifest["domain_division_model_count"], "shared_platform_specialist_model_count": manifest["shared_platform_specialist_model_count"], "output": str(target), "trained_model_count": 0, "mastered_model_count": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
