#!/usr/bin/env python3
"""Generate auditable 45M-class architecture blueprints for the 65 divisions.

This produces configuration metadata only. It does not train weights or approve
any dataset. Parameter counts are calculated from the explicit architecture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"

ARCHITECTURE = {
    "family": "decoder_only_transformer",
    "hidden_size": 384,
    "layers": 19,
    "attention_heads": 6,
    "head_dimension": 64,
    "intermediate_size": 1536,
    "vocabulary_size": 512,
    "max_sequence_length": 1024,
    "attention": "fused_qkv_multi_head_self_attention_with_rope",
    "feed_forward": "swiglu",
    "normalization": "rmsnorm_pre_norm",
    "linear_biases": False,
    "tied_token_embedding_and_lm_head": True,
    "trainable_absolute_position_embeddings": False,
    "parameter_count_formula": (
        "vocab*hidden + layers*(4*hidden^2 + 3*hidden*intermediate + "
        "2*hidden) + hidden"
    ),
}


def count_parameters(config: dict) -> int:
    h = int(config["hidden_size"])
    layers = int(config["layers"])
    intermediate = int(config["intermediate_size"])
    vocab = int(config["vocabulary_size"])
    if h <= 0 or layers <= 0 or intermediate <= 0 or vocab <= 0:
        raise ValueError("architecture dimensions must be positive")
    if h % int(config["attention_heads"]) != 0:
        raise ValueError("hidden_size must be divisible by attention_heads")
    # Q/K/V/O projections: 4*h*h. SwiGLU gate/up/down: 3*h*intermediate.
    # Two RMSNorm vectors per block and one final RMSNorm vector.
    block = 4 * h * h + 3 * h * intermediate + 2 * h
    embeddings = vocab * h
    final_norm = h
    return embeddings + layers * block + final_norm


def build(registry: dict, registry_bytes: bytes) -> dict:
    divisions = registry.get("divisions", [])
    if len(divisions) != 65:
        raise ValueError("canonical MasterBot registry must contain exactly 65 divisions")
    ids = [row.get("id") for row in divisions]
    if sorted(ids) != list(range(1, 66)):
        raise ValueError("division IDs must be unique and cover 1 through 65")
    parameters = count_parameters(ARCHITECTURE)
    digest = hashlib.sha256(json.dumps(ARCHITECTURE, sort_keys=True).encode()).hexdigest()
    rows = []
    for division in sorted(divisions, key=lambda item: item["id"]):
        rows.append({
            "division_id": division["id"],
            "division_name": division["name"],
            "model_id": f"buddy-{division['id']:02d}-{division['name'].lower()}-45m-research",
            "architecture": ARCHITECTURE,
            "parameter_count": parameters,
            "parameter_count_millions": round(parameters / 1_000_000, 6),
            "architecture_sha256": digest,
            "training_status": "design_only_not_trained",
            "weights_sha256": None,
            "tokenizer_sha256": None,
            "authorized_dataset_manifest": None,
            "training_approved": False,
            "required_before_training": [
                "item_level_dataset_rights_evidence",
                "division_owner_data_scope_review",
                "train_validation_test_holdout_split_hashes",
                "approved_compute_budget",
                "reproducible_training_config",
            ],
        })
    return {
        "schema": "dreamco.division_45m_model_blueprints.v1",
        "status": "architecture_blueprints_only",
        "source_registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
        "target_parameter_count": 45_000_000,
        "actual_parameter_count": parameters,
        "actual_parameter_count_millions": round(parameters / 1_000_000, 6),
        "division_count": len(rows),
        "trained_model_count": 0,
        "blueprints": rows,
        "truth_boundary": (
            "These are architecture blueprints only. No model weights, tokenizer, "
            "authorized training corpus, training run, or mastery result is implied. "
            "45M parameters does not imply GPT-5 equivalence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "config/generated/division-45m-model-blueprints.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = REGISTRY.read_bytes()
    output = build(json.loads(raw.decode("utf-8")), raw)
    rendered = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("45M division model blueprint output is stale; regenerate it")
        print(f"Validated {output['division_count']} blueprints at {output['actual_parameter_count']:,} parameters each.")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(f"Wrote {output['division_count']} design-only blueprints; no weights trained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
