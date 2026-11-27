#!/usr/bin/env python3
"""Fail-closed buyer training preflight; no training backend is enabled."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    from .dreamco_hardware_detector import detect
except ImportError:
    from dreamco_hardware_detector import detect

ROOT = Path(__file__).resolve().parents[1]
SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")


def _resolve_local_snapshot(repository_root: Path, reference: str):
    reference = str(reference or "").strip()
    if not reference:
        return None
    relative = Path(reference.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        return None
    resolved = (repository_root / relative).resolve()
    if repository_root not in resolved.parents or not resolved.is_file():
        return None
    return resolved


def _approved_dataset(entry, repository_root: Path):
    """Validate rights, privacy, retention, and the actual local snapshot bytes."""
    if not isinstance(entry, dict) or entry.get("training_approved") is not True:
        return False, "training_approved is not explicitly true"
    if entry.get("rights_status") not in {"APPROVED", "VERIFIED"}:
        return False, "rights_status is not APPROVED or VERIFIED"
    if entry.get("content_rights_verified") is not True:
        return False, "content rights are not explicitly verified"
    if entry.get("privacy_review") != "PASSED":
        return False, "privacy_review is not PASSED"
    if not str(entry.get("retention_policy") or "").strip():
        return False, "retention_policy is missing"
    if not str(entry.get("retention_evidence") or "").strip():
        return False, "retention_evidence is missing"
    if not str(entry.get("rights_evidence_reference") or "").strip():
        return False, "rights_evidence_reference is missing"

    expected_hash = str(entry.get("sha256") or "").strip()
    if not SHA256_PATTERN.fullmatch(expected_hash):
        return False, "sha256 is not a valid 64-character digest"

    snapshot = _resolve_local_snapshot(repository_root, entry.get("evidence_reference"))
    if snapshot is None:
        return False, "evidence_reference does not resolve to a local repository file"

    actual_hash = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    if actual_hash.lower() != expected_hash.lower():
        return False, "snapshot SHA-256 does not match the approved manifest"
    return True, ""


def preflight(
    kit,
    execute=False,
    *,
    dataset_manifest_path=None,
    repository_root=ROOT,
    hardware_info=None,
):
    kit = Path(kit)
    repository_root = Path(repository_root).resolve()
    manifest_path = kit / "BUYER_MANIFEST.json"
    config_path = kit / "blueprint" / "config.json"
    if not manifest_path.is_file() or not config_path.is_file():
        raise ValueError("Incomplete buyer kit")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    blockers = []

    if manifest.get("weights_status") != "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" or manifest.get("weights_included") is not False:
        blockers.append("Buyer kit weight-status contract failed")
    if config.get("weights_status") != "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" or config.get("initialization") != "random":
        blockers.append("Architecture config must be a random-initialization untrained blueprint")

    hardware = hardware_info if hardware_info is not None else detect()
    if manifest.get("tier") not in hardware.get("candidate_tiers", []):
        blockers.append("Detected hardware does not meet advisory tier guidance")

    dataset_manifest = Path(dataset_manifest_path) if dataset_manifest_path else (
        repository_root / "config" / "authorized-training-datasets" / "manifest.json"
    )
    approved = []
    if not dataset_manifest.is_file():
        blockers.append("Authorized training dataset manifest is missing")
    else:
        try:
            policy = json.loads(dataset_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            policy = {}
            blockers.append("Authorized training dataset manifest is unreadable")
        datasets = policy.get("datasets", []) if isinstance(policy, dict) else []
        if not isinstance(datasets, list):
            blockers.append("Authorized training dataset entries must be a list")
            datasets = []
        for index, entry in enumerate(datasets):
            if isinstance(entry, dict) and entry.get("training_approved") is True:
                valid, reason = _approved_dataset(entry, repository_root)
                if valid:
                    approved.append(entry)
                else:
                    blockers.append(f"Dataset {entry.get('id', index)} blocked: {reason}")
        if not approved:
            blockers.append("No explicitly approved, rights-evidenced, hash-pinned local dataset is admitted")

    if execute:
        blockers.append("No reviewed training backend adapter is configured; execution is disabled")

    return {
        "schema": "dreamco.buyer_training_preflight.v1",
        "status": "BLOCKED" if blockers else "READY_FOR_BACKEND_REVIEW",
        "tier": manifest.get("tier"),
        "division": manifest.get("division"),
        "weights_status": manifest.get("weights_status"),
        "parameter_count_verified": manifest.get("parameter_count_verified", False),
        "hardware": hardware,
        "approved_dataset_count": len(approved),
        "blockers": blockers,
        "training_started": False,
        "paid_compute_requested": False,
        "customer_data_uploaded": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Execution remains disabled until a reviewed backend adapter exists")
    args = parser.parse_args()
    result = preflight(args.kit, args.execute)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] != "BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
