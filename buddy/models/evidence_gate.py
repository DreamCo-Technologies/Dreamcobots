"""Evidence gate for division infrastructure, training, benchmark and runtime readiness.
The gate validates artifacts; it does not execute integrations or promote models.
"""
from __future__ import annotations
import hashlib, re
from pathlib import Path
from typing import Any

REQUIRED_DOMAINS = {"infrastructure", "dataset", "training", "benchmark", "runtime"}
HASH = re.compile(r"^[0-9a-f]{64}$")

class EvidenceGateError(ValueError):
    pass

def verify_division_evidence(manifest: dict[str, Any], artifact_root: str | Path) -> dict[str, Any]:
    if not isinstance(manifest, dict) or manifest.get("schema") != "dreamco.division_evidence_manifest.v1":
        raise EvidenceGateError("unsupported division evidence manifest")
    division_id = manifest.get("masterbot_id")
    if isinstance(division_id, bool) or not isinstance(division_id, int) or not 1 <= division_id <= 65:
        raise EvidenceGateError("masterbot_id must be between 1 and 65")
    records = manifest.get("evidence")
    if not isinstance(records, list):
        raise EvidenceGateError("evidence must be a list")
    by_domain = {}
    for item in records:
        if not isinstance(item, dict) or item.get("domain") not in REQUIRED_DOMAINS:
            raise EvidenceGateError("unknown or malformed evidence domain")
        domain = item["domain"]
        if domain in by_domain:
            raise EvidenceGateError("duplicate evidence domain: " + domain)
        by_domain[domain] = item
    missing = sorted(REQUIRED_DOMAINS - set(by_domain))
    failures = []
    root = Path(artifact_root).resolve()
    for domain in sorted(REQUIRED_DOMAINS & set(by_domain)):
        item = by_domain[domain]
        if item.get("status") != "PASS":
            failures.append({"domain": domain, "reason": "evidence_status_not_pass"})
            continue
        if item.get("masterbot_id") != division_id:
            failures.append({"domain": domain, "reason": "division_identity_mismatch"})
            continue
        if not str(item.get("evidence_id", "")).strip() or not str(item.get("observed_at", "")).strip():
            failures.append({"domain": domain, "reason": "evidence_identity_or_timestamp_missing"})
            continue
        rel = Path(str(item.get("artifact_path", "")))
        if rel.is_absolute() or ".." in rel.parts or not str(rel):
            failures.append({"domain": domain, "reason": "artifact_path_not_confined"})
            continue
        artifact = (root / rel).resolve()
        if root not in artifact.parents or not artifact.is_file():
            failures.append({"domain": domain, "reason": "artifact_missing_or_outside_root"})
            continue
        expected = str(item.get("artifact_sha256", ""))
        if not HASH.fullmatch(expected):
            failures.append({"domain": domain, "reason": "artifact_sha256_missing_or_invalid"})
            continue
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != expected:
            failures.append({"domain": domain, "reason": "artifact_hash_mismatch"})
            continue
        if not str(item.get("source_ref", "")).strip():
            failures.append({"domain": domain, "reason": "source_evidence_reference_missing"})
    ready = not missing and not failures
    return {"schema": "dreamco.division_evidence_gate_result.v1", "masterbot_id": division_id,
        "status": "READY_FOR_INDEPENDENT_REVIEW" if ready else "BLOCKED",
        "verified_domains": sorted(set(by_domain) - {x["domain"] for x in failures}),
        "missing_domains": missing, "failures": failures,
        "production_promotion": False, "independent_review_required": True, "weights_updated": False}
