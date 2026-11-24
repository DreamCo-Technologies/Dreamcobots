#!/usr/bin/env python3
"""Build a private, evidence-linked candidate; never publish or enable checkout."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from buddy.learning.model_foundry import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_candidate(checkpoint: Path, metadata_path: Path, tokenizer_path: Path,
                    manifest: dict[str, Any], data_root: Path, evaluation_path: Path,
                    training_run_id: str, code_revision: str) -> dict[str, Any]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    approved = validate_manifest(manifest, data_root)
    match = next((row for row in approved if row["dataset_id"] == metadata.get("dataset_id")), None)
    if match is None:
        raise ValueError("checkpoint dataset is not rights-approved with verified local evidence")
    if match["sha256"] != metadata.get("dataset_sha256"):
        raise ValueError("checkpoint dataset hash does not match the authorized manifest")
    permissions = match.get("permissions") or {}
    if permissions.get("redistribution") is not True:
        raise ValueError("model-weight redistribution permission must be explicitly true")
    if not all(permissions.get(key) is True for key in ("training", "commercial_model_use", "derivative_models")):
        raise ValueError("training, commercial use and derivative model permissions must be explicitly true")
    if not all(path.is_file() for path in (checkpoint, metadata_path, tokenizer_path)):
        raise ValueError("checkpoint, metadata and tokenizer files must all exist")
    weights_hash, tokenizer_hash = sha256(checkpoint), sha256(tokenizer_path)
    if metadata.get("weights_sha256") != weights_hash:
        raise ValueError("checkpoint SHA-256 does not match training metadata")
    if metadata.get("tokenizer_sha256") != tokenizer_hash:
        raise ValueError("tokenizer SHA-256 does not match training metadata")
    if metadata.get("training_status") != "trained_experimental_checkpoint_not_certified":
        raise ValueError("checkpoint is not a recognized experimental training output")
    if metadata.get("initialization") != "random" or not isinstance(metadata.get("parameter_count"), int) or metadata["parameter_count"] < 1:
        raise ValueError("candidate must be a real from-scratch model with a positive parameter count")
    if not training_run_id.strip() or not code_revision.strip():
        raise ValueError("training run ID and code revision are required")
    if evaluation.get("status") != "PASSED" or evaluation.get("holdout_independent") is not True:
        raise ValueError("an independent evaluation report with status PASSED is required")
    if evaluation.get("dataset_sha256") != metadata.get("dataset_sha256"):
        raise ValueError("evaluation dataset hash does not match the trained dataset")
    if evaluation.get("checkpoint_sha256") != weights_hash:
        raise ValueError("evaluation checkpoint hash does not match the actual checkpoint")
    if not evaluation.get("suite_id") or not evaluation.get("report_id"):
        raise ValueError("evaluation suite_id and report_id are required")
    architecture = metadata.get("architecture", {})
    config_hash = hashlib.sha256(json.dumps(architecture, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "dreamco.model_release_candidate.v1",
        "model_id": metadata["model_id"],
        "version": f"0.1.0-run-{training_run_id}",
        "division_id": metadata["division_id"],
        "parameter_count": metadata["parameter_count"],
        "architecture": architecture,
        "weights_sha256": weights_hash,
        "tokenizer_sha256": tokenizer_hash,
        "config_sha256": config_hash,
        "dataset_provenance": {
            "dataset_id": match["dataset_id"], "dataset_sha256": match["sha256"],
            "owner": match["owner"], "owner_attestation_ref": match["owner_attestation_ref"],
            "license_id": match["license_id"], "license_evidence_ref": match["license_evidence_ref"]
        },
        "permissions": {"training": True, "commercial_model_use": True, "derivative_models": True, "redistribution": True},
        "training": {
            "training_run_id": training_run_id, "code_revision": code_revision,
            "seed": metadata["seed"], "optimizer": metadata["optimizer"],
            "learning_rate": metadata["learning_rate"], "batch_size": metadata["batch_size"],
            "steps": metadata["total_steps"], "initialization": "random"
        },
        "evaluation": {
            "status": "PASSED", "suite_id": evaluation["suite_id"], "report_id": evaluation["report_id"],
            "report_sha256": sha256(evaluation_path), "holdout_independent": True,
            "holdout_loss": metadata["holdout_loss"]
        },
        "artifact_integrity": {"checkpoint_sha256": weights_hash, "tokenizer_sha256": tokenizer_hash, "config_sha256": config_hash},
        "release_status": "candidate_requires_human_release_review",
        "storefront_listing": False, "checkout_enabled": False, "source_data_included": False
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=ROOT / "config/authorized-training-datasets/manifest.json")
    parser.add_argument("--data-root", type=Path, default=Path.home() / "DreamCo-private-data")
    parser.add_argument("--evaluation-report", type=Path, required=True)
    parser.add_argument("--training-run-id", required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        candidate = build_candidate(
            args.checkpoint.resolve(), args.metadata.resolve(), args.tokenizer.resolve(),
            json.loads(args.manifest.read_text(encoding="utf-8")), args.data_root.resolve(),
            args.evaluation_report.resolve(), args.training_run_id, args.code_revision
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"BLOCKED: {exc}") from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    print(f"Candidate evidence written: {args.output}; not listed for sale.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
