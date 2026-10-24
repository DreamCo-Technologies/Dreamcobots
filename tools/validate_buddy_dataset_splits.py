#!/usr/bin/env python3
"""Offline structural preflight for privacy-minimized Buddy dataset split manifests.

Only accepts opaque IDs and SHA-256 digests; it does not inspect training data,
verify rights/consent, unseal holdouts, run models, or authorize training.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "dreamco.buddy_dataset_split_manifest.v1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
OPAQUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{7,79}\Z")
SPLITS = ("train", "validation", "holdout")
TOP_KEYS = {"schema", "dataset_id", "contains_raw_examples", "training_authorized",
            "provenance_review_receipt", "license_review_receipt",
            "consent_review_receipt", "privacy_review_receipt", "splits"}
RECORD_KEYS = {"example_id", "content_sha256", "group_id"}


class SplitManifestError(ValueError):
    """A dataset manifest is malformed or cannot establish structural isolation."""


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SplitManifestError("duplicate JSON key")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise SplitManifestError("nonfinite JSON constant")


def parse_manifest(raw: str) -> Any:
    try:
        return json.loads(raw, object_pairs_hook=_unique_keys,
                          parse_constant=_reject_nonfinite)
    except json.JSONDecodeError as exc:
        raise SplitManifestError("invalid JSON") from exc


def validate(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict) or set(manifest) != TOP_KEYS:
        raise SplitManifestError("unexpected manifest fields")
    if manifest["schema"] != SCHEMA:
        raise SplitManifestError("unexpected manifest schema")
    if not isinstance(manifest["dataset_id"], str) or not OPAQUE.fullmatch(manifest["dataset_id"]):
        raise SplitManifestError("dataset_id must be opaque")
    if manifest["contains_raw_examples"] is not False or manifest["training_authorized"] is not False:
        raise SplitManifestError("raw examples and training authorization prohibited")
    # Receipt IDs are pointers, NOT evidence that the documents were verified.
    missing_receipts = []
    for key in ("provenance_review_receipt", "license_review_receipt",
                "consent_review_receipt", "privacy_review_receipt"):
        receipt = manifest[key]
        if receipt is None:
            missing_receipts.append(key)
        elif not isinstance(receipt, str) or not OPAQUE.fullmatch(receipt):
            raise SplitManifestError(f"{key} must be an opaque receipt ID")
    splits = manifest["splits"]
    if not isinstance(splits, dict) or set(splits) != set(SPLITS):
        raise SplitManifestError("exact train, validation, holdout splits required")
    all_ids: set[str] = set()
    all_hashes: set[str] = set()
    group_owner: dict[str, str] = {}
    counts: dict[str, int] = {}
    for split in SPLITS:
        rows = splits[split]
        if not isinstance(rows, list) or not rows or len(rows) > 100000:
            raise SplitManifestError(f"{split} must contain 1..100000 metadata records")
        counts[split] = len(rows)
        for row in rows:
            if not isinstance(row, dict) or set(row) != RECORD_KEYS:
                raise SplitManifestError("unexpected record fields; raw text forbidden")
            example_id, digest, group_id = (row[k] for k in ("example_id", "content_sha256", "group_id"))
            if not isinstance(example_id, str) or not OPAQUE.fullmatch(example_id):
                raise SplitManifestError("example_id must be opaque")
            if not isinstance(group_id, str) or not OPAQUE.fullmatch(group_id):
                raise SplitManifestError("group_id must be opaque")
            if not isinstance(digest, str) or not HEX64.fullmatch(digest):
                raise SplitManifestError("content_sha256 must be lowercase SHA-256")
            if example_id in all_ids or digest in all_hashes:
                raise SplitManifestError("duplicate example ID or content hash across splits")
            if group_id in group_owner and group_owner[group_id] != split:
                raise SplitManifestError("group leakage across splits")
            all_ids.add(example_id)
            all_hashes.add(digest)
            group_owner[group_id] = split
    return {
        "schema": "dreamco.buddy_dataset_split_preflight.v1",
        "status": "metadata_only_not_verified_for_training",
        "counts": counts,
        "duplicate_content_hashes_detected": False,
        "cross_split_group_leakage_detected": False,
        "missing_review_receipt_ids": missing_receipts,
        "rights_and_consent_verified": False,
        "privacy_verified": False,
        "independent_holdout_verified": False,
        "training_authorized": False,
        "eligible_for_model_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = validate(parse_manifest(args.manifest.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"dataset split preflight blocked: {exc}\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
