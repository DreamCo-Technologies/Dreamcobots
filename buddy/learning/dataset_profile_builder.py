"""Build governed, user-customizable dataset profiles and learning plans.

This module plans real ingestion/training work from permitted content. It does not
pretend that a URL visit, catalog entry, or generated plan changed model weights.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

SCHEMA = "dreamco.buddy.dataset_profile.v1"
METHODS = {
    "retrieval", "skill_pack", "prompt_policy", "sft", "lora", "qlora",
    "preference_optimization", "distillation", "continued_pretraining",
}
SOURCE_STATES = {"approved", "pending_review", "blocked"}
RIGHTS_ALLOWED = {"owned", "open_license", "public_domain", "licensed", "user_authorized"}
CONTENT_STATES = {"content_available", "metadata_only", "not_ingested"}
DEFAULT_MIX = {
    "official_docs": 0.25, "courses": 0.20, "papers": 0.15,
    "datasets": 0.15, "code_examples": 0.15, "user_material": 0.10,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_id(value: str) -> str:
    return "-".join((value or "").strip().lower().split())


def create_profile(owner_id: str, name: str, goal: str, **overrides: Any) -> dict:
    """Create a conservative starter profile; owner_id is an app-scoped opaque ID."""
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


def validate_profile(profile: dict) -> list[str]:
    errors: list[str] = []
    if profile.get("schema") != SCHEMA:
        errors.append("unsupported schema")
    for field in ("owner_id", "name", "goal"):
        if not isinstance(profile.get(field), str) or not profile[field].strip():
            errors.append(f"{field} is required")
    methods = profile.get("training_methods", [])
    if not isinstance(methods, list) or not methods:
        errors.append("at least one training method is required")
    elif set(methods) - METHODS:
        errors.append("unsupported training method")
    mix = profile.get("source_mix", {})
    if not isinstance(mix, dict) or not mix or any(not isinstance(v, (int, float)) or v < 0 for v in mix.values()):
        errors.append("source_mix must contain non-negative numeric weights")
    elif abs(sum(mix.values()) - 1.0) > 1e-6:
        errors.append("source_mix weights must sum to 1.0")
    quality = profile.get("quality", {})
    holdout = quality.get("holdout_fraction", 0)
    validation = quality.get("validation_fraction", 0)
    if not (0 < holdout < 0.5 and 0 < validation < 0.5 and holdout + validation < 0.8):
        errors.append("validation and holdout fractions must be positive and leave training data")
    training = profile.get("training", {})
    for key in ("max_examples", "max_runtime_minutes", "max_gpu_hours"):
        if not isinstance(training.get(key), (int, float)) or training[key] < 0:
            errors.append(f"training.{key} must be non-negative")
    if training.get("max_compute_usd", -1) < 0:
        errors.append("training.max_compute_usd must be non-negative")
    for source in profile.get("sources", []):
        if source.get("status") not in SOURCE_STATES:
            errors.append(f"source {source.get('id', '<unknown>')}: invalid status")
        if source.get("rights") not in RIGHTS_ALLOWED:
            errors.append(f"source {source.get('id', '<unknown>')}: rights must be reviewed")
        if source.get("content_state") not in CONTENT_STATES:
            errors.append(f"source {source.get('id', '<unknown>')}: invalid content_state")
        if source.get("status") == "approved" and source.get("rights") not in RIGHTS_ALLOWED:
            errors.append(f"source {source.get('id', '<unknown>')}: approved source lacks rights")
        if source.get("content_state") == "content_available" and not source.get("content_ref"):
            errors.append(f"source {source.get('id', '<unknown>')}: content_ref required")
    if "continued_pretraining" in methods and not profile.get("training", {}).get("advanced_training_approved", False):
        errors.append("continued_pretraining requires explicit advanced_training_approved")
    if "distillation" in methods and not profile.get("training", {}).get("teacher_license_reviewed", False):
        errors.append("distillation requires teacher_license_reviewed")
    return errors


def eligible_sources(profile: dict) -> list[dict]:
    """Return only approved, rights-cleared sources with actual content, not URL visits."""
    return [
        deepcopy(s) for s in profile.get("sources", [])
        if s.get("status") == "approved"
        and s.get("rights") in RIGHTS_ALLOWED
        and s.get("content_state") == "content_available"
        and s.get("content_ref")
        and s.get("provenance")
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
            "content_hash": source.get("content_hash"),
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
    if plan.get("profile_id") != profile.get("profile_id"):
        raise ValueError("plan/profile mismatch")
    return {
        "schema": "dreamco.buddy.training_manifest.v1",
        "profile_id": profile["profile_id"],
        "dataset_version": sha256(repr(plan["source_manifest"]).encode()).hexdigest()[:16],
        "target_model": deepcopy(profile["target_model"]),
        "methods": list(profile["training_methods"]),
        "source_ids": [s["source_id"] for s in plan["source_manifest"]],
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
