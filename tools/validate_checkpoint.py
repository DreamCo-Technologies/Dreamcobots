#!/usr/bin/env python3
"""Fail-closed checkpoint evidence validator and HMAC signer; does not train models."""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def finite_positive(value: Any, name: str, allow_zero: bool = False) -> float:
    number = float(value)
    if not math.isfinite(number) or (number < 0 if allow_zero else number <= 0):
        raise ValueError(f"{name} must be a finite {'non-negative' if allow_zero else 'positive'} number")
    return number


def build_manifest(checkpoint: Path, evaluation_path: Path, training_config_path: Path,
                   dataset_manifest_path: Path, metrics_path: Path, expected_parameters: int,
                   signing_key: str) -> dict[str, Any]:
    if not signing_key or len(signing_key) < 32:
        raise ValueError("DREAMCO_CHECKPOINT_SIGNING_KEY must contain at least 32 characters")
    evaluation = read_json(evaluation_path)
    config = read_json(training_config_path)
    dataset = read_json(dataset_manifest_path)
    metrics = read_json(metrics_path)
    if evaluation.get("split") != "private_independent_holdout" or evaluation.get("training_use") != "NEVER_TRAIN":
        raise ValueError("checkpoint promotion requires a private independent holdout report; public smoke suites are insufficient")
    if evaluation.get("passed") is not True or float(evaluation.get("accuracy", 0)) < float(evaluation.get("required_accuracy", 0.85)):
        raise ValueError("held-out evaluation did not pass")
    if dataset.get("training_authorized") is not True or dataset.get("rights_review_status") != "APPROVED":
        raise ValueError("dataset rights and explicit training authorization are not approved")
    if not config.get("seed") is not None or not config.get("code_revision") or not config.get("base_model"):
        raise ValueError("training config must record seed, code_revision and base_model")
    if not checkpoint.is_file() or checkpoint.stat().st_size == 0:
        raise ValueError("checkpoint artifact is missing or empty")
    parameter_count = int(metrics.get("parameter_count", 0))
    if parameter_count != expected_parameters:
        raise ValueError(f"measured parameter_count {parameter_count} != expected {expected_parameters}")
    perplexity = finite_positive(metrics.get("validation_perplexity"), "validation_perplexity")
    throughput = finite_positive(metrics.get("tokens_per_second"), "tokens_per_second")
    peak_ram = finite_positive(metrics.get("peak_ram_mb"), "peak_ram_mb")
    peak_vram = metrics.get("peak_vram_mb")
    if peak_vram is not None:
        peak_vram = finite_positive(peak_vram, "peak_vram_mb", allow_zero=True)
    payload = {
        "schema": "dreamco.signed_checkpoint_manifest.v1",
        "status": "VERIFIED_CHECKPOINT_EVIDENCE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint": {"path_name": checkpoint.name, "sha256": sha256_file(checkpoint), "bytes": checkpoint.stat().st_size},
        "model": {"base_model": config["base_model"], "parameter_count_measured": parameter_count},
        "training": {"seed": config["seed"], "code_revision": config["code_revision"],
                     "training_config_sha256": sha256_file(training_config_path),
                     "dataset_manifest_sha256": sha256_file(dataset_manifest_path)},
        "evaluation": {"report_sha256": sha256_file(evaluation_path), "suite_id": evaluation["suite_id"],
                       "suite_sha256": evaluation["suite_sha256"], "accuracy": evaluation["accuracy"],
                       "required_accuracy": evaluation["required_accuracy"], "passed": True},
        "metrics": {"validation_perplexity": perplexity, "tokens_per_second": throughput,
                    "peak_ram_mb": peak_ram, "peak_vram_mb": peak_vram},
        "signature": {"algorithm": "HMAC-SHA256", "key_id": os.environ.get("DREAMCO_CHECKPOINT_SIGNING_KEY_ID", "local-unmanaged"),
                      "value": ""},
    }
    payload["signature"]["value"] = hmac.new(signing_key.encode(), json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--training-config", type=Path, required=True)
    parser.add_argument("--dataset-manifest", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-parameters", type=int, default=45_000_000)
    args = parser.parse_args()
    manifest = build_manifest(args.checkpoint, args.evaluation, args.training_config,
                              args.dataset_manifest, args.metrics, args.expected_parameters,
                              os.environ.get("DREAMCO_CHECKPOINT_SIGNING_KEY", ""))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "checkpoint_sha256": manifest["checkpoint"]["sha256"],
                      "signature_algorithm": manifest["signature"]["algorithm"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
