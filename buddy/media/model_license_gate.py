"""Fail-closed commercial model license gate.

A model is not approved merely because its code or repository is described as open source.
This gate requires checkpoint-specific license evidence and a reviewed dependency inventory.
It does not provide legal advice or determine rights in training data or generated outputs.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, Mapping

PERMISSIVE_LICENSES = {"MIT", "Apache-2.0"}

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def verify_model_record(record: Mapping[str, Any], evidence_root: str | Path) -> dict[str, Any]:
    """Return approved only when checkpoint, license evidence and all dependency records pass."""
    reasons: list[str] = []
    required = (
        "model_id", "checkpoint_path", "checkpoint_sha256", "license_id", "license_evidence_path",
        "license_evidence_sha256", "model_card_url", "commercial_use_allowed",
        "redistribution_allowed", "dependencies",
    )
    for key in required:
        if key not in record or record[key] in (None, ""):
            reasons.append(f"missing:{key}")
    if reasons:
        return {"decision": "blocked", "reasons": reasons}

    checkpoint_hash = str(record["checkpoint_sha256"]).lower()
    if len(checkpoint_hash) != 64 or any(c not in "0123456789abcdef" for c in checkpoint_hash):
        reasons.append("invalid:checkpoint_sha256")

    checkpoint_path = (root / str(record["checkpoint_path"])).resolve()
    if root not in checkpoint_path.parents:
        reasons.append("checkpoint_path_escapes_evidence_root")
    elif not checkpoint_path.is_file():
        reasons.append("checkpoint_file_missing")
    elif len(checkpoint_hash) == 64 and _sha256(checkpoint_path) != checkpoint_hash:
        reasons.append("checkpoint_hash_mismatch")

    license_id = str(record["license_id"])
    if license_id not in PERMISSIVE_LICENSES:
        reasons.append(f"license_not_allowlisted:{license_id}")
    if record["commercial_use_allowed"] is not True:
        reasons.append("commercial_use_not_explicitly_allowed")
    if record["redistribution_allowed"] is not True:
        reasons.append("redistribution_not_explicitly_allowed")

    card_url = str(record["model_card_url"])
    if not card_url.startswith("https://"):
        reasons.append("model_card_url_must_use_https")

    root = Path(evidence_root).resolve()
    evidence = (root / str(record["license_evidence_path"])).resolve()
    if root not in evidence.parents:
        reasons.append("license_evidence_path_escapes_evidence_root")
    elif not evidence.is_file():
        reasons.append("license_evidence_file_missing")
    elif _sha256(evidence) != str(record["license_evidence_sha256"]).lower():
        reasons.append("license_evidence_hash_mismatch")

    dependencies = record.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        reasons.append("dependencies_must_be_a_non_empty_reviewed_list")
    else:
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, Mapping):
                reasons.append(f"dependency_{index}_invalid_record")
                continue
            dep_license = dependency.get("license_id")
            if not isinstance(dep_license, str) or dep_license not in PERMISSIVE_LICENSES:
                reasons.append(f"dependency_{index}_license_not_allowlisted:{dep_license}")
            if dependency.get("reviewed") is not True:
                reasons.append(f"dependency_{index}_not_reviewed")

    return {
        "decision": "approved" if not reasons else "blocked",
        "model_id": record.get("model_id"),
        "license_id": license_id,
        "checkpoint_sha256": checkpoint_hash,
        "reasons": reasons,
        "scope_note": "Model license approval does not clear datasets, likenesses, outputs, trademarks, or customer content.",
    }
