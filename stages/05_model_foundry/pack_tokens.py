"""Pack signed training and validation records into separate uint32 token shards."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
try:
    from .guardrails import assert_training_split, iter_authorized_records, verify_signed_manifest
except ImportError:
    from guardrails import assert_training_split, iter_authorized_records, verify_signed_manifest

def _token_pool(records, tokenizer):
    tokens = []
    for row in records:
        text = row.get("content") or row.get("text") or row.get("title", "")
        if row.get("messages"):
            text = "\n".join(
                f"{'<|tool_call|>' if message.get('role') == 'tool' else '<|' + message.get('role', 'user') + '|>'} {message.get('content', '')}"
                for message in row["messages"]
            )
        encoded = tokenizer.encode(str(text), add_special_tokens=False)
        if encoded:
            tokens.extend(encoded)
            tokens.append(tokenizer.eos_token_id)
    return tokens

def _write_shard(tokens, output: Path, prefix: str, sequence_length: int):
    import numpy as np
    usable = (len(tokens) // sequence_length) * sequence_length
    if usable == 0:
        return None
    path = output / f"{prefix}-00000.bin"
    np.asarray(tokens[:usable], dtype=np.uint32).tofile(path)
    return {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "tokens": int(usable), "sequences": int(usable // sequence_length)}

def main():
    parser = argparse.ArgumentParser(description="Pack signed DreamCo training data")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sequence-length", type=int, default=1024)
    args = parser.parse_args()
    if args.sequence_length < 8:
        raise ValueError("sequence length must be >= 8")
    import numpy as np  # noqa: F401
    from transformers import AutoTokenizer
    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, trust_remote_code=False)
    if tokenizer.eos_token_id is None:
        raise ValueError("tokenizer must define EOS")
    args.output.mkdir(parents=True, exist_ok=True)

    weights = {"study_guides": 60, "verified_trajectories": 25, "general_replay": 15}
    pools = {}
    for category in weights:
        rows = list(iter_authorized_records(manifest, categories={category}, splits={"train"}))
        assert_training_split(rows)
        pools[category] = _token_pool(rows, tokenizer)
        if not pools[category]:
            raise ValueError(f"category {category} contains no authorized encodable training tokens")

    # Largest deterministic mixture preserving the requested 60/25/15 token ratio.
    target_units = min(len(pools[key]) * 100 // weight for key, weight in weights.items()) // 100
    if target_units == 0:
        raise ValueError("not enough signed training tokens to satisfy the 60/25/15 curriculum")
    train_tokens = []
    cursors = {category: 0 for category in weights}
    for _ in range(target_units):
        for category, weight in weights.items():
            pool = pools[category]
            cursor = cursors[category]
            train_tokens.extend(pool[(cursor + offset) % len(pool)] for offset in range(weight))
            cursors[category] = (cursor + weight) % len(pool)
    train_shard = _write_shard(train_tokens, args.output, "train", args.sequence_length)
    if train_shard is None:
        raise ValueError("not enough authorized tokens to form one training sequence")

    # Validation is a separate evaluation-only shard, never mixed into train data.
    validation_categories = {"study_guides", "verified_trajectories", "general_replay"}
    validation_rows = list(iter_authorized_records(
        manifest, categories=validation_categories, splits={"validation"}
    ))
    validation_tokens = _token_pool(validation_rows, tokenizer)
    validation_shard = _write_shard(validation_tokens, args.output, "validation", args.sequence_length)
    report = {
        "schema": "dreamco.foundry.token_shards.v1", "sequence_length": args.sequence_length,
        "dtype": "uint32", "training_splits": ["train"],
        "validation_splits": ["validation"] if validation_shard else [],
        "excluded_splits": ["holdout"], "mix_percent": weights,
        "train": train_shard, "validation": validation_shard,
        "source_manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
    }
    (args.output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
