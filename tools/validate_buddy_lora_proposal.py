#!/usr/bin/env python3
"""Offline, read-only Buddy LoRA proposal preflight (never authorizes training).

Checks proposal structure and evidence references, not the truth of consent,
licensing, hardware, holdout isolation or approvals. Never reads referenced
files, makes network requests, trains, or uploads.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "dreamco.buddy_lora_experiment_proposal.v1"
REQUIRED = (
    "base_model", "base_revision_full_commit_sha", "base_license_and_notice_review_receipt",
    "dataset_sha256", "dataset_consent_and_rights_receipt", "train_split_sha256",
    "validation_split_sha256", "sealed_holdout_receipt", "target_modules",
    "hardware_and_memory_preflight_receipt", "checkpoint_artifact_sha256",
    "baseline_evaluation_receipt", "post_training_evaluation_receipt",
    "rollback_artifact_sha256", "human_release_approval_receipt",
)
BOOL_FLAGS = ("execution_authorized", "download_authorized", "publish_weights_authorized")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
REVISION = re.compile(r"[0-9a-f]{40}\Z")
REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#@+-]{7,255}\Z")
MODEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
ALLOWED = {"schema", *BOOL_FLAGS, *REQUIRED, "method", "seed", "rank", "alpha",
           "dropout", "learning_rate", "micro_batch_size", "gradient_accumulation_steps",
           "max_sequence_length", "epochs", "compute_budget_usd"}
HASH_FIELDS = {"dataset_sha256", "train_split_sha256", "validation_split_sha256",
               "checkpoint_artifact_sha256", "rollback_artifact_sha256"}


class ProposalError(ValueError):
    """Unsafe or malformed proposed configuration."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous JSON objects, including nested duplicate keys."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProposalError("duplicate JSON key in LoRA proposal")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> None:
    """Python's JSON decoder accepts NaN/Infinity by default; proposals do not."""
    raise ProposalError(f"nonfinite JSON constant in LoRA proposal: {value}")


def parse_proposal(text: str) -> Any:
    """Parse a proposal without silently overriding duplicate security fields."""
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_constant,
        )
    except json.JSONDecodeError as exc:
        raise ProposalError("invalid LoRA proposal JSON") from exc


def validate(proposal: Any) -> dict:
    if not isinstance(proposal, dict) or set(proposal) != ALLOWED:
        raise ProposalError("proposal must contain exactly the defined schema fields")
    if proposal["schema"] != SCHEMA:
        raise ProposalError("unexpected proposal schema")
    for field in BOOL_FLAGS:
        if type(proposal[field]) is not bool:
            raise ProposalError(f"{field} must be boolean")
        if proposal[field]:
            raise ProposalError(f"{field} must remain false in review-only proposal")
    if proposal["method"] != "LoRA":
        raise ProposalError("only a disabled LoRA proposal is supported")
    for field, low, high in (("seed", 0, 2**32 - 1), ("rank", 1, 256),
                             ("alpha", 1, 1024), ("micro_batch_size", 1, 64),
                             ("gradient_accumulation_steps", 1, 1024),
                             ("max_sequence_length", 1, 65536), ("epochs", 1, 100)):
        value = proposal[field]
        if type(value) is not int or not low <= value <= high:
            raise ProposalError(f"invalid {field}")
    for field, low, high in (("dropout", 0, 1), ("learning_rate", 0, 1)):
        value = proposal[field]
        if type(value) not in (int, float) or not low <= value <= high or (field == "learning_rate" and value == 0):
            raise ProposalError(f"invalid {field}")
    if type(proposal["compute_budget_usd"]) not in (int, float) or proposal["compute_budget_usd"] != 0:
        raise ProposalError("review-only proposal requires zero-dollar compute budget")
    blockers = []
    for field in REQUIRED:
        value = proposal[field]
        if value is None:
            blockers.append(field)
            continue
        if field in HASH_FIELDS:
            valid = isinstance(value, str) and HEX64.fullmatch(value) is not None
        elif field == "base_revision_full_commit_sha":
            valid = isinstance(value, str) and REVISION.fullmatch(value) is not None
        elif field == "base_model":
            valid = isinstance(value, str) and MODEL.fullmatch(value) is not None
        elif field == "target_modules":
            valid = isinstance(value, list) and 0 < len(value) <= 32 and all(
                isinstance(m, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", m)
                for m in value) and len(set(value)) == len(value)
        else:
            valid = isinstance(value, str) and REF.fullmatch(value) is not None
        if not valid:
            raise ProposalError(f"invalid {field} format")
    if all(proposal[f] is not None for f in ("train_split_sha256", "validation_split_sha256")):
        if proposal["train_split_sha256"] == proposal["validation_split_sha256"]:
            raise ProposalError("training and validation split hashes must differ")
    # Even fully populated metadata is not verified evidence or permission.
    return {
        "schema": "dreamco.buddy_lora_proposal_preflight.v1",
        "status": "review_only_no_training_authorized",
        "missing_evidence_fields": sorted(blockers),
        "missing_evidence_count": len(blockers),
        "evidence_contents_verified": False,
        "holdout_isolation_verified": False,
        "rights_and_consent_verified": False,
        "hardware_and_cost_verified": False,
        "training_authorized": False,
        "model_quality_verified": False,
        "eligible_for_model_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    args = parser.parse_args()
    try:
        proposal = parse_proposal(args.proposal.read_text(encoding="utf-8"))
        report = validate(proposal)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"LoRA proposal preflight blocked: {exc}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
