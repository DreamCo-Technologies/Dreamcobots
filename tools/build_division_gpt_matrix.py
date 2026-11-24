#!/usr/bin/env python3
"""Generate one auditable GPT-style model profile per canonical DreamCo division.

This creates configuration metadata only. It does not allocate weights, download
training data, or start a GPU job.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
MODEL_CONFIG = ROOT / "config/division-gpt-45m-training.json"


def parameter_count(cfg: dict[str, Any]) -> int:
    vocab = int(cfg["vocab_size"])
    width = int(cfg["d_model"])
    layers = int(cfg["n_layers"])
    heads = int(cfg["n_heads"])
    ff = int(cfg["d_ff"])
    if width % heads:
        raise ValueError("d_model must be divisible by n_heads")
    # Token embeddings are tied to the output projection. RoPE has no learned
    # position table. Each block has biased QKV + output projections, biased
    # two-layer MLP, and two affine LayerNorms. One final affine LayerNorm.
    embedding = vocab * width
    attention = (width * 3 * width + 3 * width) + (width * width + width)
    mlp = (width * ff + ff) + (ff * width + width)
    norms_per_block = 4 * width
    final_norm = 2 * width
    return embedding + layers * (attention + mlp + norms_per_block) + final_norm


def build_matrix(registry: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    divisions = registry.get("divisions")
    if not isinstance(divisions, list) or len(divisions) != 65:
        raise ValueError("canonical registry must contain exactly 65 divisions")
    ids = [item.get("id") for item in divisions]
    if sorted(ids) != list(range(1, 66)):
        raise ValueError("division IDs must be unique and cover 1 through 65")

    cfg = model["architecture"]
    actual = parameter_count(cfg)
    expected = model["parameter_count"]["expected"]
    tolerance = model["parameter_count"].get("tolerance", 0)
    if abs(actual - expected) > tolerance:
        raise ValueError(f"parameter-count mismatch: expected {expected}, calculated {actual}")

    profiles = []
    for division in sorted(divisions, key=lambda item: item["id"]):
        division_id = division["id"]
        profiles.append({
            "division_id": division_id,
            "division_name": division["name"],
            "model_id": f"dreamco-division-{division_id:02d}-gpt45m",
            "model_version": "0.1.0-config-only",
            "architecture": cfg,
            "parameter_count": actual,
            "training_status": "not_started",
            "training_enabled": False,
            "blocked_reasons": [
                "rights_approved_division_training_corpus_missing",
                "training_runtime_and_compute_budget_not_registered"
            ]
        })
    return {
        "schema": "dreamco.division_gpt_model_matrix.v1",
        "division_count": len(profiles),
        "unique_model_profiles": len({p["model_id"] for p in profiles}),
        "parameters_per_model": actual,
        "aggregate_parameters_if_all_checkpoints_are_materialized": actual * len(profiles),
        "weights_created": False,
        "training_started": False,
        "profiles": profiles
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--model-config", type=Path, default=MODEL_CONFIG)
    parser.add_argument("--output", type=Path, default=ROOT / "config/generated/division-gpt-45m-matrix.json")
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    model = json.loads(args.model_config.read_text(encoding="utf-8"))
    result = build_matrix(registry, model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "profiles"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
