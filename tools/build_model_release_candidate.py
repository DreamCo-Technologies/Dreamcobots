#!/usr/bin/env python3
"""Build a private, evidence-linked release candidate from a real DreamCo checkpoint.

This tool never edits the public storefront catalog and never marks a model for sale.
It requires explicit redistribution permission plus a separately authored evaluation
report. The resulting JSON is a review artifact, not a purchase entitlement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HASH = re.compile(r"^[a-f0-9]{64}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_candidate(checkpoint: Path, metadata_path: Path, tokenizer_path: Path,
                    manifest: dict[str, Any], evaluation_path: Path,
                    training_run_id: str, code_revision: str) -> dict[str, Any]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    datasets = manifest.get("datasets", [])
    match = next((row for row in datasets if row.get("dataset_id") == metadata.get("dataset_id")), None)
    if not match:
        raise ValueError("checkpoint dataset is absent from the authorized dataset manifest")
    permissions = match.get("permissions") or {}
    if match.get("rights_status") != "APPROVED":
        raise ValueError("dataset rights are not APPROVED")
    if permissions.get("training") is not True or permissions.get("commercial_model_use") is not True:
        raise ValueError("training and commercial model-use permissions must both be true")
    if permissions.get("derivative_models") is not True or permissions.get("redistribution") is not True:
        raise ValueError("derivative-model and model-weight redistribution permissions must both be true")
    if not match.get("license_id") or not match.get("license_evidence_ref") or not match.get("owner_attestation_ref"):
        raise ValueError("license and owner evidence references are required")
    if not checkpoint.is_file() or not metadata_path.is_file() or not tokenizer_path.is_file():
        raise ValueError("checkpoint, metadata and tokenizer files must all exist")
    actual_weights_hash = sha256(checkpoint)
    actual_tokenizer_hash = sha256(tokenizer_path)
    if metadata.get("weights_sha256") != actual_weights_hash:
        raise ValueError("checkpoint SHA-256 does not match training metadata")
    if metadata.get("tokenizer_sha256") != actual_tokenizer_hash:
        raise ValueError("tokenizer SHA-256 does not match training metadata")
    if metadata.get("training_status") != "trained_experimental_checkpoint_not_certified":
        raise ValueError("checkpoint is not a recognized experimental training output")
    if metadata.get("initialization") != "random" or metadata.get("parameter_count", 0) < 1:
        raise ValueError("candidate must have a real from-scratch model and positive parameter count")
    if not training_run_id.strip() or not code_revision.strip():
        raise ValueError("training run ID and code revision are required")
    if evaluation.get("status") != "PASSED" or evaluation.get("holdout_independent") is not True:
        raise ValueError("an independent evaluation report with status PASSED is required")
    if evaluation.get("dataset_sha256") != metadata.get("dataset_sha256"):
        raise ValueError("evaluation dataset hash does not match the trained dataset")
    if evaluation.get("checkpoint_sha256") != actual_weights_hash:
        raise ValueError("evaluation checkpoint hash does not match the actual checkpoint")
    if not evaluation.get("suite_id") or not evaluation.get("report_id"):
        raise ValueError("evaluation suite_id and report_id are required")
    architecture_json = json.dumps(metadata.get("architecture", {}), sort_keys=True, separators=(",", ":")).encode()
    config_hash = hashlib.sha256(architecture_json).hexdigest()
    return {
        "schema": "dreamco.model_release_candidate.v1",
        "model_id": metadata["model_id"],
        "version": f"0.1.0-run-{training_run_id}",
        "division_id": metadata["division_id"],
        "parameter_count": metadata["parameter_count"],
        "architecture": metadata["architecture"],
        "weights_sha256": actual_weights_hash,
        "tokenizer_sha256": actual_tokenizer_hash,
        "config_sha256": config_hash,
        "dataset_provenance": {
            "dataset_id": match["dataset_id"],
            "dataset_sha256": match["sha256"],
            "owner": match["owner"],
            "owner_attestation_ref": match["owner_attestation_ref"],
            "license_id": match["license_id"],
            "license_evidence_ref": match["license_evidence_ref"]
        },
        "permissions": {
            "training": True,
            "commercial_model_use": True,
            "derivative_models": True,
            "redistribution": True
        },
        "training": {
            "training_run_id": training_run_id,
            "code_revision": code_revision,
            "seed": metadata["seed"],
            "optimizer": metadata["optimizer"],
            "learning_rate": metadata["learning_rate"],
            "batch_size": metadata["batch_size"],
            "steps": metadata["total_steps"],
            "initialization": "random"
        },
        "evaluation": {
            "status": "PASSED",
            "suite_id": evaluation["suite_id"],
            "report_id": evaluation["report_id"],
            "report_sha256": sha256(evaluation_path),
            "holdout_independent": True,
            "holdout_loss": metadata["holdout_loss"]
        },
        "artifact_integrity": {
            "checkpoint_sha256": actual_weights_hash,
            "tokenizer_sha256": actual_tokenizer_hash,
            "config_sha256": config_hash
        },
        "release_status": "candidate_requires_human_release_review",
        "storefront_listing": False,
        "checkout_enabled": False,
        "source_data_included": False
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=ROOT / "config/authorized-training-datasets/manifest.json")
    parser.add_argument("--evaluation-report", type=Path, required=True)
    parser.add_argument("--training-run-id", required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        candidate = build_candidate(
            args.checkpoint.resolve(), args.metadata.resolve(), args.tokenizer.resolve(),
            json.loads(args.manifest.read_text(encoding="utf-8")),
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
