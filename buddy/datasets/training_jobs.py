"""Create reproducible training job requests; never launch compute from this module."""
from __future__ import annotations
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .hub import DatasetHub, DatasetPolicyError

def create_training_job(dataset_hub: DatasetHub, dataset_id: str, masterbot_id: int,
                        model_id: str, base_model_revision: str, compute_approval_id: str = "",
                        output_dir: str | Path = "artifacts/buddy-training-jobs") -> dict[str, Any]:
    card = dataset_hub.get(dataset_id)
    if not card:
        raise DatasetPolicyError("Dataset not found")
    if card.get("training_approved") is not True or card.get("rights_status") != "VERIFIED":
        raise DatasetPolicyError("Dataset is not approved for training")
    if card.get("holdout") or card.get("data_plane") == "evaluation_only_holdout":
        raise DatasetPolicyError("Evaluation holdouts can never enter training")
    if not card.get("content_sha256") or not card.get("object_path"):
        raise DatasetPolicyError("A content-addressed dataset object is required before training")
    splits = card.get("split_manifest") or {}
    if not all(re.fullmatch(r"[0-9a-f]{64}", str(splits.get(key, ""))) for key in ("train_sha256", "validation_sha256", "test_sha256")):
        raise DatasetPolicyError("Pinned train, validation, and isolated test split hashes are required")
    if not compute_approval_id.strip():
        raise DatasetPolicyError("An explicit compute budget approval ID is required")
    if not model_id.strip() or not re.fullmatch(r"[0-9a-f]{40}", base_model_revision.strip()):
        raise DatasetPolicyError("Pin model ID and a 40-character immutable base-model commit SHA")
    payload = {
        "schema": "dreamco.model_training_job.v1", "job_id": "train-" + uuid.uuid4().hex[:16],
        "created_at": datetime.now(timezone.utc).isoformat(), "dataset_id": dataset_id,
        "dataset_version": card["version"], "dataset_sha256": card.get("content_sha256"),
        "masterbot_id": masterbot_id, "model_id": model_id,
        "base_model_revision": base_model_revision, "compute_approval_id": compute_approval_id, "split_manifest": splits,
        "status": "APPROVED_REQUEST_PENDING_REGISTERED_RUNNER",
        "execution_status": "NOT_EXECUTED", "weights_updated": False,
        "reproducibility": {"dataset_card_sha256": hashlib.sha256(json.dumps(card, sort_keys=True).encode()).hexdigest(),
            "split_manifest_required": True, "seed_required": True, "tokenizer_revision_required": True,
            "holdout_isolation_required": True, "benchmark_before_and_after_required": True},
        "promotion": {"production_weight_update": False, "requires_independent_review": True,
            "requires_separate_explicit_approval": True}
    }
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{payload['job_id']}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    payload["manifest_path"] = str(path)
    return payload
