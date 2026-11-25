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
    parser.add_argument("--resume-from", type=Path)
    parser.add_argument("--architecture-profile", type=Path, required=True)
    parser.add_argument("--authorize-weight-updates", action="store_true", help="explicitly approve local model weight updates for this invocation")
    parser.add_argument("--authorization-reference", required=True, help="owner approval or change-control reference")
    parser.add_argument("--approved-by", required=True, help="owner/operator authorizing this run")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.authorize_weight_updates:
        raise SystemExit("BLOCKED: pass --authorize-weight-updates only after reviewing the dataset rights and training profile")
    if len(args.authorization_reference.strip()) < 6 or len(args.approved_by.strip()) < 2:
        raise SystemExit("BLOCKED: authorization reference and approving owner are required")
    dataset_path = args.dataset_path.expanduser().resolve()
    data_root = Path(__import__("os").environ.get("DREAMCO_AUTHORIZED_DATA_ROOT", str(Path.home() / "DreamCo-private-data"))).resolve()
    if data_root not in dataset_path.parents:
        raise SystemExit("dataset path must be inside the owner-controlled private data root")
    output_path = args.output.expanduser().resolve()
    if data_root not in output_path.parents:
        raise SystemExit("checkpoint output must be inside the owner-controlled private data root")
    resume_path = args.resume_from.expanduser().resolve() if args.resume_from else None
    if resume_path is not None and data_root not in resume_path.parents:
        raise SystemExit("resume checkpoint must be inside the owner-controlled private data root")
    architecture_profile = json.loads(args.architecture_profile.read_text(encoding="utf-8"))
    if not isinstance(architecture_profile, dict):
        raise SystemExit("architecture profile must be a JSON object")
    manifest_path = ROOT / "config/authorized-training-datasets/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    from buddy.learning.model_foundry import validate_manifest
    approved = validate_manifest(manifest, data_root)
    match = next((item for item in approved if item["dataset_id"] == args.dataset_id
                  and args.division_id in item["approved_division_ids"]
                  and Path(item["_resolved_path"]) == dataset_path
                  and item["training_strategy"] == args.strategy), None)
    if match is None:
        raise SystemExit("BLOCKED: dataset is not rights-approved for this division")
    result = train_from_scratch(
        dataset_path, args.output, dataset_id=args.dataset_id,
        division_id=args.division_id, strategy=args.strategy, seed=args.seed, steps=args.steps,
        resume_from=resume_path,
        architecture_profile=architecture_profile,
        authorization_manifest=manifest,
        data_root=data_root,
        explicit_training_authorization=args.authorize_weight_updates,
        authorization_reference=args.authorization_reference,
        approved_by=args.approved_by,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
