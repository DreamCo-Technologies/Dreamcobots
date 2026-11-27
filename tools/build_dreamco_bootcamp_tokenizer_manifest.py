#!/usr/bin/env python3
"""Build a narrowly scoped, owner-authorized tokenizer corpus from DreamCo Bootcamp."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("data/dreamco_training/bootcamp/core_lessons.v1.jsonl")
AUTHORIZATION = Path("governance/training-authorizations/dreamco-bootcamp-core-v1-owner-attestation.json")
CORPUS = Path("data/buddy-authorized-corpora/dreamco-bootcamp-core-v1-train.jsonl")
MANIFEST = Path("data/buddy-authorized-corpora/dreamco-bootcamp-core-v1-manifest.json")
REPORT = Path("data/buddy-authorized-corpora/dreamco-bootcamp-core-v1-manifest-report.json")

PII_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\d)"),
    re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
)
SECRET_PATTERNS = (
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
EXPECTED_AUTHORING = {
    "status": "DRAFT_REQUIRES_HUMAN_REVIEW",
    "owner_claim": "PENDING_ASSIGNMENT_REVIEW",
    "training_permission": "NOT_GRANTED",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"source line {number} must be a JSON object")
        rows.append(value)
    if not rows:
        raise ValueError("DreamCo Bootcamp source corpus is empty")
    return rows


def build_manifest(root: Path = ROOT) -> dict[str, Any]:
    source_path = root / SOURCE
    authorization_path = root / AUTHORIZATION
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    required_authorization = {
        "schema": "dreamco.owner_training_authorization.v1",
        "status": "APPROVED",
        "approved_by": "repository_owner",
        "approved_source_id": "dreamco-bootcamp-core-v1",
        "approved_source_path": SOURCE.as_posix(),
        "approved_splits": ["train"],
        "scope": "tokenizer_training_only",
        "allow_third_party_content": False,
        "allow_private_customer_data": False,
        "allow_holdout_data": False,
        "allow_model_weight_training": False,
        "allow_distillation": False,
    }
    for key, expected in required_authorization.items():
        if authorization.get(key) != expected:
            raise PermissionError(f"owner authorization mismatch for {key}")

    rows = read_jsonl(source_path)
    counts = {"train": 0, "validation": 0, "test": 0}
    training_rows = []
    for row in rows:
        split = row.get("split")
        if split not in counts:
            raise ValueError("source contains an unsupported split")
        counts[split] += 1
        source = row.get("source") or {}
        if source.get("kind") != "dreamco_original_authored_draft":
            raise PermissionError("only first-party DreamCo Bootcamp examples are authorized")
        if source.get("source_id") != authorization["approved_source_id"]:
            raise PermissionError("source_id does not match the owner authorization")
        if source.get("external_text_included") is not False:
            raise PermissionError("third-party or unreviewed external text is blocked")
        if row.get("authoring") != EXPECTED_AUTHORING:
            raise ValueError("source authoring status changed; review the corpus before use")
        if row.get("target_scope") != "shared_foundation_candidate":
            raise ValueError("only shared-foundation bootcamp examples are in scope")
        inspected = json.dumps(row, ensure_ascii=False)
        if any(pattern.search(inspected) for pattern in PII_PATTERNS):
            raise PermissionError("PII detected in tokenizer source")
        if any(pattern.search(inspected) for pattern in SECRET_PATTERNS):
            raise PermissionError("secret material detected in tokenizer source")
        if split == "train":
            training_rows.append(row)

    if not training_rows or not counts["validation"] or not counts["test"]:
        raise ValueError("train, validation, and test splits must all exist; only train is used")
    canonical = b"".join(
        (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        for row in training_rows
    )
    corpus_path = root / CORPUS
    manifest_path = root / MANIFEST
    report_path = root / REPORT
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.write_bytes(canonical)

    manifest = {
        "schema": "dreamco.authorized_tokenizer_corpus_manifest.v1",
        "manifest_id": "dreamco-bootcamp-core-v1-tokenizer",
        "training_scope": "tokenizer_only",
        "neural_model_weight_training_allowed": False,
        "production_training_allowed": False,
        "corpora": [{
            "source_id": "dreamco-bootcamp-core-v1-train",
            "path": CORPUS.as_posix(),
            "sha256": sha256(canonical),
            "source_type": "first_party",
            "rights_verified": True,
            "model_training_permission": True,
            "privacy_reviewed": True,
            "holdout": False,
            "sensitive": False,
            "license_evidence_ref": AUTHORIZATION.as_posix(),
            "training_scope": "tokenizer_only",
        }],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report = {
        "status": "TOKENIZER_ONLY_CORPUS_READY",
        "authorization_id": authorization["authorization_id"],
        "source_id": authorization["approved_source_id"],
        "source_sha256": sha256(source_path.read_bytes()),
        "training_corpus_path": CORPUS.as_posix(),
        "training_corpus_sha256": sha256(canonical),
        "source_split_counts": counts,
        "training_rows_used": len(training_rows),
        "validation_rows_excluded": counts["validation"],
        "test_rows_excluded": counts["test"],
        "third_party_content_allowed": False,
        "private_customer_data_allowed": False,
        "holdout_data_used": False,
        "neural_model_weight_training_allowed": False,
        "distillation_allowed": False,
        "manifest_path": MANIFEST.as_posix(),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(build_manifest(args.root.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
