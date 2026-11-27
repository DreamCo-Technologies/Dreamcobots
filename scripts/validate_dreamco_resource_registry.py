#!/usr/bin/env python3
"""Validate the 100-source registry and fail-closed rights admission contract."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/dreamco_institute_resource_registry.json"
REQUIRED = {
    "id", "name", "category", "resource_type", "acquisition_status",
    "license_status", "commercial_training_permission", "quarantine_status",
    "source_provenance_required", "sha256_required",
}
EVIDENCE = (
    "license_evidence", "source_url", "snapshot_path", "snapshot_sha256",
    "reviewed_by", "retention_evidence",
)


def _resolve_snapshot(root: Path, reference):
    reference = str(reference or "").strip()
    if not reference:
        return None
    relative = Path(reference.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "data":
        return None
    resolved = (root / relative).resolve()
    if root not in resolved.parents or not resolved.is_file():
        return None
    return resolved


def validate(data, expected_count=100, root=ROOT):
    errors = []
    root = Path(root).resolve()
    entries = data.get("resources", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        entries = []
        errors.append("resources must be a list")
    if not isinstance(data, dict) or data.get("resource_count") != expected_count or len(entries) != expected_count:
        errors.append(f"registry must contain exactly {expected_count} resources")

    ids = [item.get("id") for item in entries if isinstance(item, dict)]
    if len(ids) != len(entries):
        errors.append("every resource entry must be an object")
    if len(set(ids)) != len(ids):
        errors.append("resource IDs must be unique")

    for item in entries:
        if not isinstance(item, dict):
            continue
        missing = REQUIRED - set(item)
        if missing:
            errors.append(f"{item.get('id')}: missing fields {sorted(missing)}")
        approved = item.get("commercial_training_permission") == "APPROVED"
        admitted = item.get("quarantine_status") == "APPROVED_FOR_TRAINING"
        if item.get("license_status") != "UNVERIFIED" and not item.get("license_evidence"):
            errors.append(f"{item.get('id')}: license evidence required")
        if admitted and not approved:
            errors.append(f"{item.get('id')}: training gate cannot pass without explicit permission")
        if approved and not admitted:
            errors.append(f"{item.get('id')}: permission approval requires quarantine review before training")
        if admitted:
            if item.get("license_status") != "VERIFIED" or item.get("acquisition_status") != "ACQUIRED":
                errors.append(f"{item.get('id')}: training admission requires verified license and authorized acquisition")
            if not all(item.get(key) for key in EVIDENCE):
                errors.append(f"{item.get('id')}: approval evidence incomplete")
            if not re.fullmatch(r"[a-fA-F0-9]{64}", str(item.get("snapshot_sha256", ""))):
                errors.append(f"{item.get('id')}: valid SHA-256 snapshot hash required")
            if item.get("privacy_review") != "PASSED":
                errors.append(f"{item.get('id')}: privacy/PII review must be PASSED")
            snapshot = _resolve_snapshot(root, item.get("snapshot_path"))
            if snapshot is None:
                errors.append(f"{item.get('id')}: snapshot_path must resolve to an approved local data file")
            elif hashlib.sha256(snapshot.read_bytes()).hexdigest().lower() != str(item.get("snapshot_sha256", "")).lower():
                errors.append(f"{item.get('id')}: snapshot hash does not match local file bytes")
    return errors


def main():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors = validate(data)
    print(json.dumps({
        "status": "FAIL" if errors else "PASS",
        "resource_count": len(data.get("resources", [])),
        "blocked_pending_review": sum(
            item.get("quarantine_status") != "APPROVED_FOR_TRAINING"
            for item in data.get("resources", [])
        ),
        "errors": errors,
    }, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
