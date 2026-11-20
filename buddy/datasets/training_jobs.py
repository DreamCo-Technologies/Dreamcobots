"""Create reproducible training job requests for the registered local Transformers runner."""
from __future__ import annotations
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .hub import DatasetHub, DatasetPolicyError

ROOT = Path(__file__).resolve().parents[2]

def create_training_job(dataset_hub: DatasetHub, dataset_id: str, masterbot_id: int,
                        model_id: str, base_model_revision: str, compute_approval_id: str = "",
                        model_license: str = "", model_license_url: str = "",
                        model_license_status: str = "UNKNOWN", model_license_evidence: str = "",
                        training_method: str = "sft", max_steps: int = 100,
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
    registry = json.loads((ROOT / "config/masterbot-65-registry.json").read_text(encoding="utf-8"))
    valid_masterbots = {int(item["id"]) for item in registry.get("divisions", [])}
    if int(masterbot_id) not in valid_masterbots:
        raise DatasetPolicyError("MasterBot ID is not present in the canonical registry")
    allowed_owners = {int(card.get("primary_masterbot_id"))} | {int(item) for item in card.get("collaborating_masterbot_ids", [])}
    if int(masterbot_id) not in allowed_owners:
        raise DatasetPolicyError("Dataset is not assigned to this MasterBot lane")
    if not model_id.strip() or not re.fullmatch(r"[0-9a-f]{40}", base_model_revision.strip()):
        raise DatasetPolicyError("Pin model ID and a 40-character immutable base-model commit SHA")
    if not model_license.strip() or not model_license_url.startswith("https://") or model_license_status != "VERIFIED" or not model_license_evidence.strip():
        raise DatasetPolicyError("The base model license, HTTPS terms URL, verified status, and evidence reference are required")
    if training_method not in {"sft", "lora"}:
        raise DatasetPolicyError("Supported first-run methods are sft and lora")
    if not 1 <= int(max_steps) <= 100000:
        raise DatasetPolicyError("max_steps must be between 1 and 100000")
    payload = {
        "schema": "dreamco.model_training_job.v1", "job_id": "train-" + uuid.uuid4().hex[:16],
        "created_at": datetime.now(timezone.utc).isoformat(), "dataset_id": dataset_id,
        "dataset_version": card["version"], "dataset_sha256": card["content_sha256"],
        "dataset_hub_path": str(dataset_hub.home.resolve()), "dataset_object_path": card["object_path"],
        "masterbot_id": masterbot_id, "model_id": model_id,
        "base_model_revision": base_model_revision, "model_license": model_license,
        "model_license_url": model_license_url, "model_license_status": model_license_status,
        "model_license_evidence": model_license_evidence, "compute_approval_id": compute_approval_id,
        "training_method": training_method, "training_config": {"max_steps": int(max_steps), "per_device_train_batch_size": 1, "gradient_accumulation_steps": 4, "learning_rate": 0.0002, "max_seq_length": 512, "seed": 42},
        "split_manifest": splits, "dataset_card_sha256": hashlib.sha256(json.dumps(card, sort_keys=True).encode()).hexdigest(),
        "status": "APPROVED_REQUEST_READY_FOR_EXPLICIT_RUN",
        "execution_status": "NOT_EXECUTED", "weights_updated": False,
        "reproducibility": {"split_manifest_required": True, "seed_required": True, "tokenizer_revision_required": True,
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
