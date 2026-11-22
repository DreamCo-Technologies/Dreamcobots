#!/usr/bin/env python3
"""Prepare deterministic synthetic-only Day 2 split artifacts; never train weights."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.gpt_baseline import prepare_synthetic_splits
from buddy.gpt_baseline.data_pipeline import DataPreparationError


def load_config(path: str | Path) -> dict:
    raw = Path(path).read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if data.get("schema") != "dreamco.buddy.synthetic_dataset_fixture.v1":
        raise DataPreparationError("unsupported Day 2 synthetic dataset schema")
    policy = data.get("training_policy") or {}
    if policy != {
        "training_enabled": False,
        "weight_updates_authorized": False,
        "external_data_allowed": False,
        "paid_compute_authorized": False,
    }:
        raise DataPreparationError("Day 2 fixture must keep training, weight updates, external data, and paid compute disabled")
    if set(data.get("split_ratios", {})) != {"train", "validation", "test"}:
        raise DataPreparationError("exact train, validation, and test ratios are required")
    if not isinstance(data.get("examples"), list):
        raise DataPreparationError("examples must be a list")
    if not isinstance(data.get("dataset_id"), str) or not data["dataset_id"].strip():
        raise DataPreparationError("dataset_id must be a non-empty string")
    data["_config_sha256"] = hashlib.sha256(raw).hexdigest()
    return data


def build_artifacts(config_path: str | Path, output_dir: str | Path, commit_sha: str | None = None) -> dict:
    data = load_config(config_path)
    provenance = data.get("provenance")
    records = [
        {"id": row.get("id"), "text": row.get("text"), "provenance": provenance}
        for row in data["examples"]
    ]
    result = prepare_synthetic_splits(
        records,
        seed=data["seed"],
        train_ratio=data["split_ratios"]["train"],
        validation_ratio=data["split_ratios"]["validation"],
        test_ratio=data["split_ratios"]["test"],
    )
    manifest = result["manifest"]
    manifest["dataset_id"] = data["dataset_id"]
    manifest["config_sha256"] = data["_config_sha256"]
    manifest["run"] = {
        "commit_sha": commit_sha or os.environ.get("GITHUB_SHA", "local-uncommitted"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "python_version": platform.python_version(),
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in result["splits"].items():
        with (output / f"{name}.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    (output / "split-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/buddy-gpt-day2-synthetic-data.json")
    parser.add_argument("--output-dir", default="artifacts/buddy-gpt-day2-data-pipeline")
    parser.add_argument("--commit-sha", default=None)
    args = parser.parse_args()
    manifest = build_artifacts(args.config, args.output_dir, args.commit_sha)
    print(json.dumps({
        "status": manifest["status"],
        "dataset_id": manifest["dataset_id"],
        "split_counts": manifest["split_counts"],
        "duplicate_rows_removed": manifest["quality"]["duplicate_rows_removed_before_split"],
        "split_hashes": manifest["split_hashes"],
        "training_execution": manifest["training_execution"],
        "weights_updated": manifest["weights_updated"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
