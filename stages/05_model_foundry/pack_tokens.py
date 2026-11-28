"""Pack signed training and validation records into separate uint32 token shards."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
try:
    from .guardrails import assert_training_split, iter_authorized_records, verify_signed_manifest
except ImportError:
    from guardrails import assert_training_split, iter_authorized_records, verify_signed_manifest

def _record_text(row):
    text = row.get("content") or row.get("text") or row.get("title", "")
    if row.get("messages"):
        text = "\\n".join(
            f"{'<|tool_call|>' if message.get('role') == 'tool' else '<|' + message.get('role', 'user') + '|>'} {message.get('content', '')}"
            for message in row["messages"]
        )
    return " ".join(str(text).casefold().split())


def _token_pool(records, tokenizer):
    """Tokenize unique normalized examples once; preserve first-seen order."""
    tokens = []
    seen = set()
    for row in records:
        normalized = _record_text(row)
        if not normalized:
            continue
        digest = hashlib.sha256(normalized.encode("utf-8")).digest()
        if digest in seen:
            continue
        seen.add(digest)
        encoded = tokenizer.encode(normalized, add_special_tokens=False)
        if encoded:
            tokens.extend(encoded)
            tokens.append(tokenizer.eos_token_id)
    return tokens

def _write_shard(tokens, output: Path, prefix: str, sequence_length: int, shard_index: int = 0):
    import numpy as np
    usable = (len(tokens) // sequence_length) * sequence_length
    if usable == 0:
        return None
    path = output / f"{prefix}-{shard_index:05d}.bin"
    np.asarray(tokens[:usable], dtype=np.uint32).tofile(path)
    sequence_count = int(usable // sequence_length)
    index_path = path.with_suffix(".idx")
    index = {
        "schema": "dreamco.foundry.token_shard_index.v1",
        "bin_file": path.name,
        "dtype": "uint32",
        "sequence_length": int(sequence_length),
        "sequence_count": sequence_count,
        "token_count": int(usable),
        "offset_unit": "tokens",
        "first_token_offset": 0,
        "sequence_stride_tokens": int(sequence_length),
    }
    index_path.write_text(json.dumps(index, sort_keys=True, separators=(",", ":")) + "\\n", encoding="utf-8")
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "index_file": index_path.name,
        "index_sha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
        "tokens": int(usable),
        "sequences": sequence_count,
    }

def main():
    parser = argparse.ArgumentParser(description="Pack signed DreamCo training data")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sequence-length", type=int, default=1024)
    parser.add_argument("--shard-size-tokens", type=int, default=5_000_000)
    args = parser.parse_args()
    if args.sequence_length < 8:
        raise ValueError("sequence length must be >= 8")
    if args.shard_size_tokens < args.sequence_length:
        raise ValueError("shard size must be at least one complete sequence")
    sequences_per_shard = max(1, args.shard_size_tokens // args.sequence_length)
    import numpy as np  # noqa: F401
    from transformers import AutoTokenizer
    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key, verify_dataset_hashes=False)
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

    # Allocate an integer 60/25/15 mixture inside every fixed-length sequence.
    raw = {category: args.sequence_length * weight / 100 for category, weight in weights.items()}
    per_sequence = {category: int(value) for category, value in raw.items()}
    remainder = args.sequence_length - sum(per_sequence.values())
    for category in sorted(weights, key=lambda key: raw[key] - per_sequence[key], reverse=True)[:remainder]:
        per_sequence[category] += 1
    sequence_count = min(
        len(pools[category]) // per_sequence[category]
        for category in weights
    )
    if sequence_count < 1:
        available = {category: len(pools[category]) for category in weights}
        raise ValueError(
            f"not enough unique tokens for one complete 60/25/15 sequence; "
            f"available={available}, required={per_sequence}"
        )
    train_shards = []
    cursors = {category: 0 for category in weights}
    shard_index = 0
    for first_sequence in range(0, sequence_count, sequences_per_shard):
        shard_sequences = min(sequences_per_shard, sequence_count - first_sequence)
        shard_tokens = np.empty(shard_sequences * args.sequence_length, dtype=np.uint32)
        position = 0
        for _ in range(shard_sequences):
            for category in weights:
                pool = pools[category]
                cursor = cursors[category]
                count = per_sequence[category]
                for offset in range(count):
                    shard_tokens[position + offset] = pool[(cursor + offset) % len(pool)]
                position += count
                cursors[category] = (cursor + count) % len(pool)
        entry = _write_shard(
            shard_tokens, args.output, "train", args.sequence_length, shard_index
        )
        if entry is None:
            raise ValueError("not enough authorized tokens to form a training shard")
        train_shards.append(entry)
        shard_index += 1

    # Validation is a separate evaluation-only shard, never mixed into train data.
    validation_categories = {"study_guides", "verified_trajectories", "general_replay"}
    validation_rows = list(iter_authorized_records(
        manifest, categories=validation_categories, splits={"validation"}
    ))
    validation_tokens = _token_pool(validation_rows, tokenizer)
    validation_shards = []
    validation_sequence_count = len(validation_tokens) // args.sequence_length
    for shard_index, first_sequence in enumerate(range(0, validation_sequence_count, sequences_per_shard)):
        start_token = first_sequence * args.sequence_length
        end_token = min(
            validation_sequence_count, first_sequence + sequences_per_shard
        ) * args.sequence_length
        entry = _write_shard(
            validation_tokens[start_token:end_token], args.output,
            "validation", args.sequence_length, shard_index
        )
        if entry is not None:
            validation_shards.append(entry)
    report = {
        "schema": "dreamco.foundry.token_shards.v1", "sequence_length": args.sequence_length,
        "shard_size_tokens": args.shard_size_tokens,
        "dtype": "uint32", "training_splits": ["train"],
        "validation_splits": ["validation"] if validation_shards else [],
        "excluded_splits": ["holdout"], "mix_percent": weights,
        "train": train_shards, "validation": validation_shards,
        "source_manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
    }
    (args.output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
