#!/usr/bin/env python3
"""Generate a reproducible, synthetic-only, forward-pass GPT baseline report."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.gpt_baseline import ByteTokenizer, TinyGPT, TinyGPTConfig, sequence_cross_entropy


def load_config(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != "dreamco.buddy.tiny_gpt_baseline_config.v1":
        raise ValueError("Unsupported tiny GPT baseline config schema")
    model_config = data.get("model", {})
    fixtures = data.get("synthetic_fixtures", {})
    if set(fixtures) != {"train", "validation", "test"}:
        raise ValueError("Expected train, validation, and test synthetic fixtures")
    if data.get("training_policy", {}).get("weight_updates_authorized") is not False:
        raise ValueError("This Day 1 runner is forward-only and must not authorize weight updates")
    if data.get("training_policy", {}).get("enabled") is not False:
        raise ValueError("Training must remain disabled in the Day 1 baseline config")
    if not all(isinstance(value, str) and len(value) >= 2 for value in fixtures.values()):
        raise ValueError("Every synthetic fixture must contain at least two characters")
    hashes = [hashlib.sha256(value.encode("utf-8")).hexdigest() for value in fixtures.values()]
    if len(set(hashes)) != len(hashes):
        raise ValueError("Synthetic train/validation/test fixtures must be distinct")
    return data


def build_evidence(config_path: str | Path, commit_sha: str | None = None) -> tuple[dict, dict]:
    data = load_config(config_path)
    cfg = TinyGPTConfig(**data["model"])
    model = TinyGPT(cfg)
    tokenizer = ByteTokenizer()
    fixtures = data["synthetic_fixtures"]
    encoded = {name: tokenizer.encode(value) for name, value in fixtures.items()}
    fixture_evidence = {
        name: {
            "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            "utf8_bytes": len(value.encode("utf-8")),
            "role": name,
            "source": "generated_synthetic_fixture",
            "used_for_training": False,
        }
        for name, value in fixtures.items()
    }
    run_config = {
        "model_id": data["model_id"],
        "model": asdict(cfg),
        "tokenizer": tokenizer.name,
        "fixtures": fixture_evidence,
        "training_enabled": False,
    }
    run_config_sha = hashlib.sha256(
        json.dumps(run_config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    report = {
        "schema": "dreamco.buddy.tiny_gpt_baseline_evidence.v1",
        "status": "BASELINE_MEASURED_UNTRAINED",
        "model_id": data["model_id"],
        "architecture": data["architecture"],
        "model": {
            **asdict(cfg),
            "parameter_count": model.parameter_count,
            "deterministic_initialization_sha256": model.fingerprint(),
        },
        "tokenizer": {
            "name": tokenizer.name,
            "vocab_size": tokenizer.vocab_size,
            "fingerprint_sha256": tokenizer.fingerprint(),
            "round_trip_contract": "UTF-8 bytes encode/decode exactly",
        },
        "fixtures": fixture_evidence,
        "metrics": {
            "validation_cross_entropy_nats": round(sequence_cross_entropy(model, encoded["validation"]), 8),
            "test_cross_entropy_nats": round(sequence_cross_entropy(model, encoded["test"]), 8),
            "metric_scope": "untrained next-byte forward-pass baseline; not a quality or capability score",
        },
        "run": {
            "commit_sha": commit_sha or os.environ.get("GITHUB_SHA", "local-uncommitted"),
            "workflow_sha": os.environ.get("GITHUB_SHA", "local-uncommitted"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "event_name": os.environ.get("GITHUB_EVENT_NAME", "local"),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "run_config_sha256": run_config_sha,
        },
        "training": {
            "executed": False,
            "weights_trained": False,
            "weight_updates": 0,
            "checkpoint_created": False,
            "paid_compute_used": False,
            "reason": "Training is disabled; this run measures deterministic initialization and forward-pass behavior only.",
        },
        "data_rights": {
            "source": "synthetic_fixtures_only",
            "external_data_used": False,
            "rights_status": "SYNTHETIC_ONLY",
            "dataset_downloads": 0,
        },
        "limitations": [
            "This is a tiny educational decoder baseline, not a trained assistant or production model.",
            "The untrained loss is a reproducibility reference, not evidence of useful language capability.",
            "No external course, customer, private, or user data was ingested.",
            "No model weights were updated and no checkpoint was created.",
        ],
    }
    model_card = {
        "schema": "dreamco.buddy.model_card.v1",
        "model_id": data["model_id"],
        "name": "Buddy Tiny GPT Baseline",
        "status": "UNTRAINED_REFERENCE_IMPLEMENTATION",
        "architecture": data["architecture"],
        "parameter_count": model.parameter_count,
        "tokenizer": tokenizer.name,
        "context_size_bytes": cfg.context_size,
        "initialization_seed": cfg.seed,
        "weights_sha256": model.fingerprint(),
        "training_data": "none; synthetic fixtures are used only for forward-pass evaluation",
        "training_status": "NOT_RUN",
        "intended_use": "educational unit tests and deterministic baseline harness",
        "out_of_scope": [
            "production inference",
            "general-purpose assistant use",
            "frontier model parity",
            "GPT-5 architecture or weight reproduction",
        ],
        "safety_and_rights": {
            "external_data_used": False,
            "weight_updates_authorized": False,
            "paid_compute_authorized": False,
        },
    }
    return report, model_card


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/buddy-tiny-gpt-baseline.json")
    parser.add_argument("--output-dir", default="artifacts/buddy-gpt-baseline")
    parser.add_argument("--commit-sha", default=None)
    args = parser.parse_args()
    report, model_card = build_evidence(args.config, args.commit_sha)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "baseline-evidence.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "model-card.json").write_text(json.dumps(model_card, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "model_id": report["model_id"],
        "parameter_count": report["model"]["parameter_count"],
        "validation_cross_entropy_nats": report["metrics"]["validation_cross_entropy_nats"],
        "test_cross_entropy_nats": report["metrics"]["test_cross_entropy_nats"],
        "weights_trained": report["training"]["weights_trained"],
        "run_config_sha256": report["run"]["run_config_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
