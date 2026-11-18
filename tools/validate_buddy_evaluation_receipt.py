#!/usr/bin/env python3
"""Validate *metadata only* for a proposed Buddy independent evaluation receipt.

No model inference, dataset access, rights verification, external requests, or
promotion. A structurally valid self-reported receipt is NOT independent proof.
Never store holdout prompts, answers, PII, or secrets in this public manifest.
"""
from __future__ import annotations

import argparse
import json
from math import isfinite
from pathlib import Path
import re
from typing import Any

SCHEMA = "dreamco.buddy_evaluation_receipt_preflight.v1"
MAX_BYTES = 32_768
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
OPAQUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{7,79}\Z")
FIELDS = {
    "schema", "evaluation_id", "model_revision_sha", "checkpoint_sha256",
    "dataset_manifest_sha256", "holdout_set_sha256",
    "independent_evaluator_receipt_id", "dataset_rights_receipt_id",
    "contains_raw_examples", "training_authorized", "promotion_authorized",
    "samples_evaluated", "samples_correct", "failed_safety_cases",
    "median_latency_ms", "p95_latency_ms",
}


class ReceiptError(ValueError):
    """Malformed, privacy-unsafe, or unsupported evaluation metadata."""


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ReceiptError("nonfinite JSON constant")


def parse_receipt(raw: str) -> Any:
    if not isinstance(raw, str):
        raise ReceiptError("receipt must be UTF-8 text")
    try:
        if len(raw.encode("utf-8")) > MAX_BYTES:
            raise ReceiptError("receipt exceeds size limit")
    except UnicodeEncodeError as exc:
        raise ReceiptError("invalid Unicode") from exc
    try:
        return json.loads(raw, object_pairs_hook=_unique_keys,
                          parse_constant=_reject_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ReceiptError("invalid JSON") from exc


def read_receipt(path: Path) -> Any:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ReceiptError("receipt exceeds size limit")
    try:
        return parse_receipt(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ReceiptError("receipt must be valid UTF-8") from exc


def validate(receipt: Any) -> dict[str, Any]:
    if not isinstance(receipt, dict) or set(receipt) != FIELDS:
        raise ReceiptError("exact metadata fields required; raw examples forbidden")
    if receipt["schema"] != SCHEMA:
        raise ReceiptError("unsupported schema")
    if not isinstance(receipt["evaluation_id"], str) or not OPAQUE.fullmatch(receipt["evaluation_id"]):
        raise ReceiptError("evaluation_id must be opaque")
    revision = receipt["model_revision_sha"]
    if not isinstance(revision, str) or not HEX40.fullmatch(revision):
        raise ReceiptError("model revision must be a pinned 40-character SHA")
    digests = []
    for key in ("checkpoint_sha256", "dataset_manifest_sha256", "holdout_set_sha256"):
        value = receipt[key]
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            raise ReceiptError(f"{key} must be lowercase SHA-256")
        digests.append(value)
    if len(set(digests)) != len(digests):
        raise ReceiptError("model, dataset and holdout hashes must be distinct")
    missing = []
    for key in ("independent_evaluator_receipt_id", "dataset_rights_receipt_id"):
        value = receipt[key]
        if value is None:
            missing.append(key)
        elif not isinstance(value, str) or not OPAQUE.fullmatch(value):
            raise ReceiptError(f"{key} must be an opaque receipt reference")
    for key in ("contains_raw_examples", "training_authorized", "promotion_authorized"):
        if receipt[key] is not False:
            raise ReceiptError(f"{key} must be false")
    n = receipt["samples_evaluated"]
    correct = receipt["samples_correct"]
    failed = receipt["failed_safety_cases"]
    if any(type(x) is not int for x in (n, correct, failed)):
        raise ReceiptError("counts must be integers, not booleans")
    if not 0 <= n <= 1_000_000 or not 0 <= correct <= n or not 0 <= failed <= n:
        raise ReceiptError("invalid evaluation counts")
    median, p95 = receipt["median_latency_ms"], receipt["p95_latency_ms"]
    if (median is None) != (p95 is None):
        raise ReceiptError("latency metrics must both be present or absent")
    if median is not None:
        if (type(median) not in (int, float) or type(p95) not in (int, float)
                or not isfinite(median) or not isfinite(p95)
                or median < 0 or p95 < median or n == 0):
            raise ReceiptError("invalid latency metrics")
    if n == 0 and (correct != 0 or failed != 0):
        raise ReceiptError("zero samples cannot have outcomes")
    return {
        "schema": "dreamco.buddy_evaluation_receipt_preflight_result.v1",
        "status": "self_reported_metadata_only",
        "reported_samples_evaluated": n,
        "reported_samples_correct": correct,
        "reported_failed_safety_cases": failed,
        "reported_median_latency_ms": median,
        "reported_p95_latency_ms": p95,
        "missing_receipt_references": missing,
        "model_calls_performed_by_preflight": 0,
        "dataset_or_holdout_contents_inspected": False,
        "evaluator_independence_verified": False,
        "dataset_rights_verified": False,
        "holdout_integrity_verified": False,
        "model_quality_verified": False,
        "training_authorized": False,
        "eligible_for_model_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = validate(read_receipt(args.receipt))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"evaluation receipt preflight blocked: {exc}\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
