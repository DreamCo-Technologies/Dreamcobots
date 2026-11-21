#!/usr/bin/env python3
"""Generate a reproducible random-initialization baseline report; never train."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.modeling.tiny_gpt import TinyGPTConfig, write_baseline_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/buddy-gpt-baseline/baseline.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--block-size", type=int, default=32)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=2)
    parser.add_argument("--embedding-dim", type=int, default=32)
    args = parser.parse_args()
    config = TinyGPTConfig(
        block_size=args.block_size,
        n_layer=args.layers,
        n_head=args.heads,
        n_embd=args.embedding_dim,
    )
    report = write_baseline_report(args.output, seed=args.seed, config=config)
    print(json.dumps({
        "report_path": args.output,
        "report_sha256": report["report_sha256"],
        "initial_loss": report["evaluation"]["initial_loss"],
        "parameter_count": report["parameter_count"],
        "training_performed": report["training_performed"],
        "weights_updated": report["weights_updated"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
