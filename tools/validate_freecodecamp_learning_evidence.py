"""Validate auditable freeCodeCamp study evidence without ingesting lesson content."""
from __future__ import annotations

from typing import Any, Mapping
import re

SHA256 = re.compile(r"^[a-f0-9]{64}$")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evaluate_learning_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate evidence gates; never infer learning from catalog presence."""
    if record.get("schema") != "dreamco.freecodecamp_learning_evidence.v1":
        raise ValueError("unsupported learning evidence schema")
    if not _nonempty(record.get("video_id")) or not _nonempty(record.get("source_url")):
        raise ValueError("video_id and source_url are required")
    division_id = record.get("division_id")
    if not isinstance(division_id, int) or not 1 <= division_id <= 65:
        raise ValueError("division_id must identify one of the 65 canonical divisions")

    rights = record.get("rights") or {}
    study = record.get("study") or {}
    sandbox = record.get("sandbox") or {}
    benchmark = record.get("benchmark") or {}

    rights_ok = rights.get("verified") is True and _nonempty(rights.get("evidence_ref"))
    study_hash = study.get("original_notes_sha256")
    study_ok = (
        study.get("completed") is True
        and isinstance(study.get("minutes"), int) and study["minutes"] > 0
        and _nonempty(study.get("attestation_ref"))
        and isinstance(study_hash, str) and SHA256.fullmatch(study_hash) is not None
    )
    sandbox_hash = sandbox.get("result_sha256")
    sandbox_ok = (
        sandbox.get("passed") is True
        and _nonempty(sandbox.get("exercise_id"))
        and isinstance(sandbox_hash, str) and SHA256.fullmatch(sandbox_hash) is not None
    )
    benchmark_ok = (
        benchmark.get("target_passed") is True
        and benchmark.get("holdout_passed") is True
        and benchmark.get("regression_passed") is True
        and _nonempty(benchmark.get("target_run_id"))
        and _nonempty(benchmark.get("holdout_run_id"))
        and _nonempty(benchmark.get("regression_run_id"))
    )

    if not rights_ok:
        status = "rights_pending"
    elif not study_ok:
        status = "study_pending"
    elif not sandbox_ok or not benchmark_ok:
        status = "studied_unverified"
    else:
        status = "mastered"

    return {
        "schema": "dreamco.freecodecamp_learning_evidence_result.v1",
        "video_id": record["video_id"],
        "division_id": division_id,
        "status": status,
        "gates": {
            "rights_verified": rights_ok,
            "study_evidence_complete": study_ok,
            "sandbox_passed": sandbox_ok,
            "target_holdout_regression_passed": benchmark_ok,
        },
        "model_training_authorized": False,
        "training_note": "Learning evidence does not grant copyright, dataset, transcript, or model-training rights.",
    }
