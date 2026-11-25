"""Build governed, user-customizable dataset profiles and learning plans.

Profiles are planning artifacts. Only approved, rights-evidenced content can enter
learning plans; a URL or self-declared license never grants training permission.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import re
from typing import Any

SCHEMA = "dreamco.buddy.dataset_profile.v1"
METHODS = {
    "retrieval", "skill_pack", "prompt_policy", "sft", "lora", "qlora",
    "preference_optimization", "distillation", "continued_pretraining",
}
SOURCE_STATES = {"approved", "pending_review", "blocked"}
RIGHTS_ALLOWED = {"owned", "open_license", "public_domain", "licensed", "user_authorized"}
RIGHTS_STATES = RIGHTS_ALLOWED | {"unknown", "restricted"}
CONTENT_STATES = {"content_available", "metadata_only", "not_ingested"}
LICENSED_RIGHTS = {"open_license", "public_domain", "licensed"}
DEFAULT_MIX = {
    "official_docs": 0.25, "courses": 0.20, "papers": 0.15,
    "datasets": 0.15, "code_examples": 0.15, "user_material": 0.10,
}
OWNER_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_profile(owner_id: str, name: str, goal: str, **overrides: Any) -> dict:
    """Create a conservative starter profile; owner_id is an opaque app-scoped ID."""
    profile = {
        "schema": SCHEMA,
        "profile_id": "dataset-" + sha256(f"{owner_id}:{name}:{goal}".encode()).hexdigest()[:12],
        "owner_id": owner_id,
        "name": name.strip(),
        "goal": goal.strip(),
        "status": "draft",
        "target_model": {"provider": "user_choice", "model_id": None, "base_model_revision": None},
        "training_methods": ["retrieval", "skill_pack"],
        "capabilities": [],
        "sources": [],
        "source_mix": deepcopy(DEFAULT_MIX),
        "quality": {"deduplicate": True, "min_quality_score": 0.70, "require_provenance": True,
                    "holdout_fraction": 0.15, "validation_fraction": 0.10},
        "privacy": {"allow_personal_data": False, "pii_policy": "exclude_or_redact",
                    "allow_external_provider_upload": False},
        "training": {"max_examples": 5000, "max_compute_usd": 0, "max_runtime_minutes": 20,
                     "max_gpu_hours": 0, "checkpoint_every_steps": 100, "seed": 42},
        "evaluation": {"baseline_required": True, "holdout_required": True,
                       "transfer_tasks": 3, "regression_required": True,
                       "minimum_improvement": 0.02},
        "created_at": _now(),
        "updated_at": _now(),
    }
    profile.update(overrides)
    return profile


def _source_rights_verified(source: dict) -> bool:
    rights = source.get("rights")
    if (source.get("status") != "approved" or rights not in RIGHTS_ALLOWED
            or source.get("training_permission_verified") is not True
            or not source.get("rights_evidence")
            or not isinstance(source.get("provenance"), dict) or not source["provenance"]):
        return False
    if rights in LICENSED_RIGHTS and not (source.get("license_url") and source.get("license_id")):
        return False
    if rights == "owned" and not (source.get("owner_attestation_id") or source.get("owner_approval_id")):
        return False
    if rights == "user_authorized" and not source.get("owner_approval_id"):
        return False
    return True


def validate_profile(profile: dict) -> list[str]:
    errors: list[str] = []
    if profile.get("schema") != SCHEMA:
        errors.append("unsupported schema")
    for field in ("owner_id", "name", "goal"):
        if not isinstance(profile.get(field), str) or not profile[field].strip():
            errors.append(f"{field} is required")
    owner_id = profile.get("owner_id")
    if isinstance(owner_id, str) and not OWNER_ID_PATTERN.fullmatch(owner_id):
        errors.append("owner_id must be an opaque app-scoped ID, not an email or secret")
    methods = profile.get("training_methods")
    if not isinstance(methods, list) or not methods:
        errors.append("at least one training method is required")
        methods = []
    elif set(methods) - METHODS:
        errors.append("unsupported training method")
    mix = profile.get("source_mix", {})
    if not isinstance(mix, dict) or not mix or any(not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0 for v in mix.values()):
        errors.append("source_mix must contain non-negative numeric weights")
        mix = {}
    elif abs(sum(mix.values()) - 1.0) > 1e-6:
        errors.append("source_mix weights must sum to 1.0")
    quality = profile.get("quality", {})
    if not isinstance(quality, dict):
        errors.append("quality must be an object")
        quality = {}
    holdout = quality.get("holdout_fraction", 0)
    validation = quality.get("validation_fraction", 0)
    if not (0 < holdout < 0.5 and 0 < validation < 0.5 and holdout + validation < 0.8):
        errors.append("validation and holdout fractions must be positive and leave training data")
    training = profile.get("training", {})
    if not isinstance(training, dict):
        errors.append("training must be an object")
        training = {}
    for key in ("max_examples", "max_runtime_minutes", "max_gpu_hours", "max_compute_usd"):
        value = training.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            errors.append(f"training.{key} must be a non-negative number")
    sources = profile.get("sources", [])
    if not isinstance(sources, list):
        errors.append("sources must be a list")
        sources = []
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source entries must be objects")
            continue
        source_id = source.get("id", "<unknown>")
        for field in ("id", "uri", "category"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                errors.append(f"source {source_id}: {field} is required")
        if source.get("status") not in SOURCE_STATES:
            errors.append(f"source {source_id}: invalid status")
        if source.get("rights") not in RIGHTS_STATES:
            errors.append(f"source {source_id}: invalid rights state")
        if source.get("content_state") not in CONTENT_STATES:
            errors.append(f"source {source_id}: invalid content_state")
        if source.get("category") not in mix:
            errors.append(f"source {source_id}: category must have a source_mix weight")
        if source.get("status") == "approved" and not _source_rights_verified(source):
            errors.append(f"source {source_id}: approved training use requires verified rights evidence and permission")
        if source.get("content_state") == "content_available":
            if not source.get("content_ref") or not source.get("content_hash"):
                errors.append(f"source {source_id}: content_ref and content_hash required")
            if not isinstance(source.get("provenance"), dict) or not source["provenance"]:
                errors.append(f"source {source_id}: provenance required")
    if "continued_pretraining" in methods and not training.get("advanced_training_approved", False):
        errors.append("continued_pretraining requires explicit advanced_training_approved")
    if "distillation" in methods and not training.get("teacher_license_reviewed", False):
        errors.append("distillation requires teacher_license_reviewed")
    return errors


def eligible_sources(profile: dict) -> list[dict]:
    """Return only approved, rights-evidenced sources with ingested content."""
    return [
        deepcopy(source) for source in profile.get("sources", [])
        if _source_rights_verified(source)
        and source.get("content_state") == "content_available"
        and source.get("content_ref") and source.get("content_hash")
    ]


def build_learning_plan(profile: dict) -> dict:
    errors = validate_profile(profile)
    if errors:
        raise ValueError("; ".join(errors))
    sources = eligible_sources(profile)
    mix = profile["source_mix"]
    selected = []
    for source in sources:
        category = source.get("category", "official_docs")
        selected.append({
            "source_id": source["id"], "content_ref": source["content_ref"],
            "category": category, "weight": mix.get(category, 0.0),
            "rights": source["rights"], "provenance": source["provenance"],
            "content_hash": source["content_hash"], "rights_evidence": source["rights_evidence"],
        })
    total = sum(row["weight"] for row in selected)
    if total:
        for row in selected:
            row["normalized_weight"] = round(row["weight"] / total, 8)
    stages = [
        "fetch_or_read_permitted_content", "extract_structured_concepts",
        "create_original_lessons_and_examples", "deduplicate_and_quality_filter",
        "redact_or_exclude_personal_data", "create_train_validation_holdout_splits",
        "index_retrieval_and_skill_cards", "generate_training_examples",
        "run_baseline", "run_bounded_training_or_adapter_job",
        "evaluate_holdout_and_transfer", "run_regression", "publish_versioned_artifacts",
    ]
    return {
        "schema": "dreamco.buddy.learning_plan.v1",
        "profile_id": profile["profile_id"], "created_at": _now(),
        "sources_with_content": len(selected),
        "metadata_only_or_unavailable_sources": len(profile.get("sources", [])) - len(selected),
        "source_manifest": selected, "stages": stages,
        "training_methods": profile["training_methods"],
        "target_model": profile["target_model"], "budget": profile["training"],
        "must_not_claim_weights_changed_until_checkpoint_receipt": True,
        "requires_worker_execution": True,
    }


def build_training_manifest(profile: dict, plan: dict) -> dict:
    """Describe trainable artifacts and guardrails for an execution adapter."""
    errors = validate_profile(profile)
    if errors:
        raise ValueError("; ".join(errors))
    if plan.get("profile_id") != profile.get("profile_id"):
        raise ValueError("plan/profile mismatch")
    expected_plan = build_learning_plan(profile)
    if plan.get("source_manifest") != expected_plan.get("source_manifest"):
        raise ValueError("plan source manifest does not match currently eligible profile sources")
    if (plan.get("must_not_claim_weights_changed_until_checkpoint_receipt") is not True
            or plan.get("requires_worker_execution") is not True):
        raise ValueError("plan execution truth guardrails are required")
    return {
        "schema": "dreamco.buddy.training_manifest.v1",
        "profile_id": profile["profile_id"],
        "dataset_version": sha256(repr(plan["source_manifest"]).encode()).hexdigest()[:16],
        "target_model": deepcopy(profile["target_model"]),
        "methods": list(profile["training_methods"]),
        "source_ids": [source["source_id"] for source in plan["source_manifest"]],
        "limits": deepcopy(profile["training"]),
        "splits": deepcopy(profile["quality"]),
        "privacy": deepcopy(profile["privacy"]),
        "evaluation": deepcopy(profile["evaluation"]),
        "artifact_outputs": ["dataset_card.json", "train.jsonl", "validation.jsonl",
                             "holdout.jsonl", "lesson_pack.json", "evaluation_receipt.json"],
        "execution_state": "planned_not_executed",
        "checkpoint_state": "not_created",
        "weight_change_claim": False,
    }
