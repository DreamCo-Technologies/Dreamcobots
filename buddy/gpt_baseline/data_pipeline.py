"""Deterministic, synthetic-only data preparation for Buddy's Day 2 lab.

This module is an in-memory preparation helper. It does not download, ingest,
persist, or authorize training data or model-weight updates.
"""
from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any

from .tiny_gpt import ByteTokenizer


class DataPreparationError(ValueError):
    """A synthetic fixture violates the Day 2 data-preparation contract."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_ratios(train_ratio: float, validation_ratio: float, test_ratio: float) -> None:
    ratios = (train_ratio, validation_ratio, test_ratio)
    if any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0 for value in ratios):
        raise DataPreparationError("split ratios must be finite positive numbers")
    if not math.isclose(sum(ratios), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise DataPreparationError("train, validation, and test ratios must sum to 1.0")


def _validate_record(record: Mapping[str, Any], seen_ids: set[str]) -> tuple[str, str, dict[str, Any]]:
    if set(record) != {"id", "text", "provenance"}:
        raise DataPreparationError("each example must contain exactly id, text, and provenance")
    example_id = record.get("id")
    if not isinstance(example_id, str) or not example_id.strip() or len(example_id) > 100:
        raise DataPreparationError("example id must be a non-empty string of at most 100 characters")
    if example_id in seen_ids:
        raise DataPreparationError(f"duplicate example id: {example_id}")
    text = record.get("text")
    if not isinstance(text, str):
        raise DataPreparationError("example text must be a string")
    normalized = unicodedata.normalize("NFC", text)
    if not normalized.strip():
        raise DataPreparationError("example text must not be empty")
    provenance = record.get("provenance")
    if not isinstance(provenance, Mapping) or set(provenance) != {
        "source_kind", "source_ref", "rights_status", "contains_personal_data"
    }:
        raise DataPreparationError("provenance must declare source_kind, source_ref, rights_status, and contains_personal_data")
    if provenance.get("source_kind") != "synthetic":
        raise DataPreparationError("Day 2 accepts synthetic fixtures only; external sources are blocked")
    source_ref = provenance.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.startswith("urn:dreamco:synthetic:"):
        raise DataPreparationError("synthetic provenance requires a DreamCo synthetic URN")
    if provenance.get("rights_status") != "SYNTHETIC_ONLY":
        raise DataPreparationError("synthetic fixtures must declare SYNTHETIC_ONLY rights status")
    if provenance.get("contains_personal_data") is not False:
        raise DataPreparationError("personal or unknown data classification is blocked")
    return example_id, normalized, dict(provenance)


def _split_hash(rows: Sequence[Mapping[str, Any]]) -> str:
    payload = [
        {"id": row["id"], "content_sha256": row["content_sha256"], "token_count": row["token_count"]}
        for row in rows
    ]
    return _sha256(_canonical_json(payload).encode("utf-8"))


def prepare_synthetic_splits(
    records: Sequence[Mapping[str, Any]],
    *,
    seed: int,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    test_ratio: float = 0.1,
    tokenizer: ByteTokenizer | None = None,
) -> dict[str, Any]:
    """Deduplicate synthetic examples before deterministic train/validation/test splitting.

    The returned train split is a preparation artifact only. The manifest always
    records training execution as NOT_TRAINED and weight updates as false.
    """
    if type(seed) is not int:
        raise DataPreparationError("seed must be an integer")
    _validate_ratios(train_ratio, validation_ratio, test_ratio)
    if isinstance(records, (str, bytes, Mapping)):
        raise DataPreparationError("records must be a sequence of example mappings")
    rows = list(records)
    if not rows:
        raise DataPreparationError("at least three unique synthetic examples are required")

    tokenizer = tokenizer or ByteTokenizer()
    seen_ids: set[str] = set()
    seen_content: dict[str, str] = {}
    unique: list[dict[str, Any]] = []
    duplicate_count = 0
    source_refs: set[str] = set()

    for raw in rows:
        if not isinstance(raw, Mapping):
            raise DataPreparationError("each example must be a mapping")
        example_id, text, provenance = _validate_record(raw, seen_ids)
        seen_ids.add(example_id)
        encoded = tokenizer.encode(text)
        if tokenizer.decode(encoded) != text:
            raise DataPreparationError("tokenizer UTF-8 round-trip failed")
        content_hash = _sha256(text.encode("utf-8"))
        prior_text = seen_content.get(content_hash)
        if prior_text is not None:
            if prior_text != text:
                raise DataPreparationError("content hash collision detected")
            duplicate_count += 1
            continue
        seen_content[content_hash] = text
        source_refs.add(provenance["source_ref"])
        unique.append({
            "id": example_id,
            "text": text,
            "provenance": provenance,
            "content_sha256": content_hash,
            "token_count": len(encoded),
        })

    count = len(unique)
    if count < 3:
        raise DataPreparationError("at least three unique synthetic examples are required after deduplication")

    validation_count = max(1, math.floor(count * validation_ratio + 0.5))
    test_count = max(1, math.floor(count * test_ratio + 0.5))
    if validation_count + test_count >= count:
        raise DataPreparationError("split ratios leave no training examples; provide more unique examples or adjust ratios")
    train_count = count - validation_count - test_count

    ranked = sorted(
        unique,
        key=lambda row: (
            _sha256(f"{seed}:{row['content_sha256']}".encode("utf-8")),
            row["id"],
        ),
    )
    splits = {
        "train": ranked[:train_count],
        "validation": ranked[train_count:train_count + validation_count],
        "test": ranked[train_count + validation_count:],
    }

    split_ids = {name: [row["id"] for row in split] for name, split in splits.items()}
    split_hashes = {f"{name}_sha256": _split_hash(split) for name, split in splits.items()}
    id_sets = [set(values) for values in split_ids.values()]
    hash_sets = [{row["content_sha256"] for row in split} for split in splits.values()]
    if any(id_sets[i] & id_sets[j] for i in range(3) for j in range(i + 1, 3)):
        raise DataPreparationError("example ID leakage detected across splits")
    if any(hash_sets[i] & hash_sets[j] for i in range(3) for j in range(i + 1, 3)):
        raise DataPreparationError("duplicate content leakage detected across splits")

    manifest = {
        "schema": "dreamco.buddy.synthetic_data_split_manifest.v1",
        "status": "SYNTHETIC_SPLITS_PREPARED_NOT_TRAINED",
        "seed": seed,
        "split_ratios": {
            "train": train_ratio,
            "validation": validation_ratio,
            "test": test_ratio,
        },
        "tokenizer": {
            "name": tokenizer.name,
            "vocab_size": tokenizer.vocab_size,
            "fingerprint_sha256": tokenizer.fingerprint(),
            "token_count_total": sum(row["token_count"] for row in unique),
            "byte_count_total": sum(len(row["text"].encode("utf-8")) for row in unique),
        },
        "provenance": {
            "source_kind": "synthetic",
            "source_references": sorted(source_refs),
            "rights_status": "SYNTHETIC_ONLY",
            "personal_data_scan": "NOT_PERFORMED; non-synthetic data requires separate privacy review",
        },
        "quality": {
            "input_rows": len(rows),
            "unique_rows": count,
            "duplicate_rows_removed_before_split": duplicate_count,
            "deduplication": "Unicode NFC normalized exact-text SHA-256 before split assignment",
            "cross_split_id_overlap": 0,
            "cross_split_content_overlap": 0,
        },
        "split_counts": {name: len(split) for name, split in splits.items()},
        "split_ids": split_ids,
        "split_hashes": split_hashes,
        "dataset_sha256": _sha256(_canonical_json(sorted(row["content_sha256"] for row in unique)).encode("utf-8")),
        "intended_use": "synthetic tokenizer and split-isolation contract tests only",
        "training_authorized": False,
        "training_execution": "NOT_RUN",
        "weights_updated": False,
        "checkpoint_created": False,
        "external_data_used": False,
    }
    return {"splits": splits, "manifest": manifest}
