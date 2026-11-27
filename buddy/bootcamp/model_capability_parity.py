"""Capability-claim and parity evidence contracts for DreamCo Bootcamp."""
from __future__ import annotations
from typing import Any, Mapping

ALLOWED_STATUSES = frozenset({
    "not_assessed", "claim_catalogued", "design_complete", "implementation_in_progress",
    "implemented", "repository_tested", "sandbox_tested", "integration_tested",
    "live_verified", "unsupported",
})

def validate_capability_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a claim without promoting it unless evidence is complete."""
    required = ("capability_id", "implementation_ref", "acceptance_test_ref", "safety_test_ref", "evidence_ref", "status")
    missing = [key for key in required if not str(record.get(key, "")).strip()]
    if missing:
        raise ValueError("missing evidence fields: " + ", ".join(missing))
    status = str(record["status"])
    if status not in ALLOWED_STATUSES:
        raise ValueError("unknown capability status")
    repetitions = record.get("repetitions", 0)
    if not isinstance(repetitions, int) or repetitions < 0:
        raise ValueError("repetitions must be a nonnegative integer")
    holdout = record.get("hidden_holdout_pass") is True
    safety = record.get("safety_pass") is True
    if status == "live_verified" and (repetitions < 3 or not holdout or not safety):
        raise ValueError("live_verified requires three repetitions, hidden holdout, and safety pass")
    if status == "unsupported" and record.get("reason") is None:
        raise ValueError("unsupported capabilities require a reason")
    return {
        "capability_id": str(record["capability_id"]),
        "status": status,
        "repetitions": repetitions,
        "hidden_holdout_pass": holdout,
        "safety_pass": safety,
        "verified": status == "live_verified",
    }

def select_learner_model_path(path_id: str, registry: Mapping[str, Any]) -> dict[str, str]:
    paths = registry.get("learner_model_paths", [])
    for path in paths:
        if path.get("id") == path_id:
            return {"id": path["id"], "label": path["label"], "result": path["result"]}
    raise ValueError("unknown learner model path")
