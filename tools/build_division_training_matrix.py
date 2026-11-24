#!/usr/bin/env python3
"""Create a parallel matrix only from rights-approved, hash-verified local datasets."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from buddy.learning.model_foundry import build_parallel_plan, validate_manifest

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "config/authorized-training-datasets/manifest.json")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data/authorized")
    parser.add_argument("--registry", type=Path, default=ROOT / "config/masterbot-65-registry.json")
    parser.add_argument("--out", type=Path, default=ROOT / "config/generated/division-training-plan.json")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    approved = validate_manifest(manifest, args.data_root)
    plan = build_parallel_plan(registry, approved)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    matrix = {"include": plan["include"]}
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write("matrix=" + json.dumps(matrix, separators=(",", ":")) + "\n")
            stream.write(f"eligible={plan['eligible_divisions']}\n")
            stream.write(f"blocked={plan['blocked_divisions']}\n")
    print(f"Eligible division jobs: {plan['eligible_divisions']}; blocked pending authorized datasets: {plan['blocked_divisions']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
