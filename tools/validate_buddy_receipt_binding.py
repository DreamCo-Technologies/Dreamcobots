#!/usr/bin/env python3
"""Check a Buddy evaluation receipt against an on-disk split *metadata* manifest.

Offline and fail-closed. This only binds declared digest fields to public-safe
metadata bytes; it does NOT verify underlying examples, holdout independence,
evaluator identity, licenses, consent, model execution, or quality.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from tools.validate_buddy_dataset_splits import read_manifest, validate as validate_splits
from tools.validate_buddy_evaluation_receipt import read_receipt, validate as validate_receipt


class BindingError(ValueError):
    """Receipt and metadata manifest cannot be safely bound."""


def holdout_metadata_digest(manifest: dict[str, Any]) -> str:
    """Fingerprint sorted-key holdout *metadata*, never actual holdout content.

    Row order is significant. Producers must preserve the exact order of the
    evaluated metadata list; this function is not a dataset-content checksum.
    """
    payload = json.dumps(
        manifest["splits"]["holdout"], sort_keys=True,
        separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_binding(receipt: Any, manifest: Any, manifest_digest: str) -> dict[str, Any]:
    """Require existing strict validators before checking cross-file linkage."""
    receipt_result = validate_receipt(receipt)
    split_result = validate_splits(manifest)
    if not isinstance(manifest_digest, str) or len(manifest_digest) != 64:
        raise BindingError("missing full manifest SHA-256")
    if receipt["dataset_manifest_sha256"] != manifest_digest:
        raise BindingError("receipt dataset digest differs from manifest file bytes")
    expected_holdout = holdout_metadata_digest(manifest)
    if receipt["holdout_set_sha256"] != expected_holdout:
        raise BindingError("receipt holdout digest differs from canonical holdout metadata")
    if receipt["samples_evaluated"] > split_result["counts"]["holdout"]:
        raise BindingError("reported sample count exceeds declared holdout metadata rows")
    return {
        "schema": "dreamco.buddy_receipt_manifest_binding_preflight.v1",
        "status": "metadata_binding_only_not_independent_evaluation",
        "manifest_bytes_sha256_match": True,
        "holdout_metadata_sha256_match": True,
        "declared_holdout_rows": split_result["counts"]["holdout"],
        "reported_samples_evaluated": receipt_result["reported_samples_evaluated"],
        "raw_holdout_examples_accessed": False,
        "holdout_content_integrity_verified": False,
        "independent_evaluator_verified": False,
        "dataset_rights_and_consent_verified": False,
        "model_inference_performed": False,
        "model_quality_verified": False,
        "training_authorized": False,
        "eligible_for_model_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        # Structural validation first, before any full-file digest operation.
        receipt = read_receipt(args.receipt)
        manifest = read_manifest(args.split_manifest)
        validate_receipt(receipt)
        validate_splits(manifest)
        report = validate_binding(receipt, manifest, file_sha256(args.split_manifest))
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        parser.exit(2, f"Buddy metadata binding preflight blocked: {exc}\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
