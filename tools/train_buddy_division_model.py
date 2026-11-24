#!/usr/bin/env python3
"""Train one rights-approved DreamCo division model from random initialization."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from buddy.learning.model_foundry import train_from_scratch

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--division-id", type=int, required=True, choices=range(1, 66))
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--dataset-path", type=Path, required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dataset_path = args.dataset_path.resolve()
    data_root = Path(__import__("os").environ.get("DREAMCO_AUTHORIZED_DATA_ROOT", str(Path.home() / "DreamCo-private-data"))).resolve()
    if data_root not in dataset_path.parents:
        raise SystemExit("dataset path must be inside data/authorized")
    manifest_path = ROOT / "config/authorized-training-datasets/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    from buddy.learning.model_foundry import validate_manifest
    approved = validate_manifest(manifest, data_root)
    match = next((item for item in approved if item["dataset_id"] == args.dataset_id
                  and args.division_id in item["approved_division_ids"]
                  and Path(item["_resolved_path"]) == dataset_path), None)
    if match is None:
        raise SystemExit("BLOCKED: dataset is not rights-approved for this division")
    result = train_from_scratch(
        dataset_path, args.output, dataset_id=args.dataset_id,
        division_id=args.division_id, strategy=args.strategy, seed=args.seed, steps=args.steps
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
