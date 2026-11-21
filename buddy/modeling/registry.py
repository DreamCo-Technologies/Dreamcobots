"""Read-only Buddy model registry, lineage validation, and safe routing gates."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class ModelRegistryError(ValueError):
    pass


def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else ROOT / "config" / "buddy-model-registry.json"
    return validate_registry(json.loads(target.read_text(encoding="utf-8")))


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if registry.get("schema") != "dreamco.buddy.model_registry.v1":
        raise ModelRegistryError("Unsupported Buddy model registry schema")
    models = registry.get("models")
    if not isinstance(models, list):
        raise ModelRegistryError("models must be a list")
    ids = [model.get("model_id") for model in models]
    if any(not model_id for model_id in ids) or len(ids) != len(set(ids)):
        raise ModelRegistryError("model IDs must be present and unique")
    for model in models:
        required = ("model_id", "lifecycle_status", "model_card", "code_path",
                    "capabilities", "lineage", "weights", "route_policy")
        if any(key not in model for key in required):
            raise ModelRegistryError(f"{model.get('model_id')}: incomplete model record")
        if not isinstance(model["capabilities"], list):
            raise ModelRegistryError(f"{model['model_id']}: capabilities must be a list")
        lineage = model["lineage"]
        weights = model["weights"]
        route = model["route_policy"]
        if not lineage.get("dataset_card"):
            raise ModelRegistryError(f"{model['model_id']}: dataset card reference is required")
        if not isinstance(weights.get("trained"), bool):
            raise ModelRegistryError(f"{model['model_id']}: weights.trained must be boolean")
        if not isinstance(route.get("enabled"), bool):
            raise ModelRegistryError(f"{model['model_id']}: route_policy.enabled must be boolean")
        if weights["trained"]:
            if not SHA256_RE.fullmatch(str(weights.get("artifact_sha256", ""))) or not weights.get("artifact_path"):
                raise ModelRegistryError(f"{model['model_id']}: trained weights require an artifact path and SHA-256 hash")
            if not lineage.get("training_run_id") or not COMMIT_RE.fullmatch(str(lineage.get("base_model_revision", ""))):
                raise ModelRegistryError(f"{model['model_id']}: trained weights require a run ID and immutable base revision")
        elif weights.get("artifact_sha256") or weights.get("artifact_path"):
            raise ModelRegistryError(f"{model['model_id']}: untrained model cannot claim a weight artifact")
        if route.get("enabled") is True and not weights["trained"]:
            raise ModelRegistryError(f"{model['model_id']}: untrained model cannot be route-enabled")
    return registry


def _eligibility_reasons(model: dict[str, Any], capability: str) -> list[str]:
    reasons = []
    if capability not in model.get("capabilities", []):
        reasons.append("capability_not_registered")
    if model.get("route_policy", {}).get("enabled") is not True:
        reasons.append("route_disabled")
    if model.get("lifecycle_status") != "PRODUCTION_VERIFIED":
        reasons.append("model_not_production_verified")
    weights = model.get("weights", {})
    if weights.get("trained") is not True or not SHA256_RE.fullmatch(str(weights.get("artifact_sha256", ""))):
        reasons.append("verified_weight_artifact_missing")
    if not weights.get("artifact_path"):
        reasons.append("weight_artifact_path_missing")
    lineage = model.get("lineage", {})
    if lineage.get("dataset_rights_status") != "VERIFIED":
        reasons.append("dataset_rights_not_verified")
    if not lineage.get("training_authorization_id"):
        reasons.append("separate_training_authorization_missing")
    if not lineage.get("training_run_id") or not COMMIT_RE.fullmatch(str(lineage.get("base_model_revision", ""))):
        reasons.append("training_lineage_incomplete")
    if not SHA256_RE.fullmatch(str(lineage.get("dataset_card_sha256", ""))):
        reasons.append("dataset_card_hash_missing")
    evidence = model.get("benchmark_evidence", [])
    if not evidence:
        reasons.append("benchmark_evidence_missing")
    for item in evidence:
        if not isinstance(item.get("baseline_score"), (int, float)) or not isinstance(item.get("candidate_score"), (int, float)):
            reasons.append("benchmark_scores_missing")
            continue
        if item["candidate_score"] < item["baseline_score"]:
            reasons.append("benchmark_regression")
        for key in ("holdout_passed", "regression_passed", "provenance_verified",
                    "dataset_rights_verified", "independent_review_approved"):
            if item.get(key) is not True:
                reasons.append(f"benchmark_gate_failed:{key}")
        if not COMMIT_RE.fullmatch(str(item.get("tested_commit_sha", ""))):
            reasons.append("benchmark_tested_commit_missing")
    return sorted(set(reasons))


def route_model(registry: dict[str, Any], capability: str) -> dict[str, Any]:
    """Return the best eligible model or an explicit blocked decision."""
    registry = validate_registry(registry)
    candidates = []
    blocked = []
    for model in registry["models"]:
        reasons = _eligibility_reasons(model, capability)
        if reasons:
            blocked.append({"model_id": model["model_id"], "reasons": reasons})
            continue
        score = max(float(item["candidate_score"]) for item in model["benchmark_evidence"])
        candidates.append((score, model["model_id"]))
    if not candidates:
        return {
            "schema": "dreamco.buddy.model_route_decision.v1",
            "status": "BLOCKED_NO_ELIGIBLE_MODEL",
            "capability": capability,
            "selected_model_id": None,
            "blocked_candidates": blocked,
            "production_side_effects": False,
        }
    score, model_id = max(candidates, key=lambda item: (item[0], item[1]))
    return {
        "schema": "dreamco.buddy.model_route_decision.v1",
        "status": "ELIGIBLE_FOR_ROUTING",
        "capability": capability,
        "selected_model_id": model_id,
        "benchmark_score": score,
        "blocked_candidates": blocked,
        "production_side_effects": False,
    }
