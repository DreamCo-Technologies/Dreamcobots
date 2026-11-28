"""Fail-closed rights checks for media assets, model weights, and dependencies."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

USES = {"study", "adapt", "display", "redistribute", "commercial_use", "train", "voice_clone", "likeness_clone"}
OWNERSHIP_CLASSES = {"dreamco_owned", "dreamco_commissioned_with_assignment", "licensed_for_use", "open_license_with_conditions", "public_domain_or_publicly_reusable", "third_party_reference_only", "synthetic_generated_by_dreamco", "user_contributed_with_permission"}

def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None

@dataclass(frozen=True)
class RightsDecision:
    allowed: bool
    asset_id: str
    use: str
    reasons: tuple[str, ...]
    attribution_required: bool = False
    share_alike_required: bool = False

def authorize_asset(record: dict[str, Any], use: str, *, commercial: bool = False) -> RightsDecision:
    asset_id = str(record.get("asset_id") or "unknown")
    reasons: list[str] = []
    if use not in USES:
        reasons.append("unsupported use")
    if record.get("review_status") != "approved":
        reasons.append("asset rights have not received human approval")
    if record.get("ownership_class") not in OWNERSHIP_CLASSES:
        reasons.append("ownership class is unknown or unsupported")
    permissions = record.get("permissions")
    if not isinstance(permissions, dict) or permissions.get(use) is not True:
        reasons.append(f"explicit permission for {use} is missing")
    if commercial and (not isinstance(permissions, dict) or permissions.get("commercial_use") is not True):
        reasons.append("commercial-use permission is missing")
    if use in {"voice_clone", "likeness_clone"}:
        consent = record.get("consent")
        if not isinstance(consent, dict) or consent.get("revoked") is not False:
            reasons.append("active subject consent is missing or revoked")
        scope = consent.get("scope", []) if isinstance(consent, dict) else []
        if use not in scope:
            reasons.append(f"consent scope does not include {use}")
        if not isinstance(consent, dict) or not consent.get("consent_id") or len(str(consent.get("attestation") or "")) < 20 or not _valid_sha(consent.get("reference_sha256")):
            reasons.append("consent receipt, reference hash, and attestation are required")
        if isinstance(consent, dict) and consent.get("expires_at"):
            try:
                expires = datetime.fromisoformat(str(consent["expires_at"]).replace("Z", "+00:00"))
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                if expires < datetime.now(timezone.utc):
                    reasons.append("subject consent has expired")
            except ValueError:
                reasons.append("consent expiry timestamp is invalid")
    if not _valid_sha(record.get("source_sha256")) or not _valid_sha(record.get("observed_sha256")):
        reasons.append("approved and observed asset SHA-256 hashes are required")
    elif record.get("observed_sha256") != record.get("source_sha256"):
        reasons.append("asset hash does not match the approved source hash")
    return RightsDecision(not reasons, asset_id, use, tuple(reasons),
                          bool(record.get("attribution_required")), bool(record.get("share_alike_required")))

def authorize_model(model: dict[str, Any], *, commercial: bool, training: bool = False) -> RightsDecision:
    model_id = str(model.get("model_id") or "unknown")
    reasons: list[str] = []
    if model.get("status") != "approved":
        reasons.append("model is not approved for deployment")
    if model.get("code_license_status") != "verified":
        reasons.append("repository code license is not verified")
    if model.get("weights_license_status") != "verified":
        reasons.append("checkpoint/weights license is not verified")
    if model.get("dependencies_reviewed") is not True:
        reasons.append("runtime dependencies have not been reviewed")
    if commercial and model.get("commercial_use_allowed") is not True:
        reasons.append("model license does not authorize commercial use")
    if training and model.get("training_allowed") is not True:
        reasons.append("model license does not authorize the requested training")
    if not re.fullmatch(r"[0-9a-f]{40}", str(model.get("exact_model_revision") or "")):
        reasons.append("exact immutable model revision is required")
    for field in ("code_license_evidence", "weights_license_evidence", "dependency_sbom_sha256", "human_reviewer", "reviewed_at"):
        if not model.get(field):
            reasons.append(f"{field} is required for approval")
    if model.get("dependency_sbom_sha256") and not _valid_sha(model.get("dependency_sbom_sha256")):
        reasons.append("dependency SBOM must be identified by SHA-256")
    if model.get("restrictions"):
        reasons.append("model has unresolved restrictions")
    use = "train" if training else "commercial_use" if commercial else "display"
    return RightsDecision(not reasons, model_id, use, tuple(reasons))

def require_allowed(decision: RightsDecision) -> None:
    if not decision.allowed:
        raise PermissionError(f"Rights gate blocked {decision.asset_id}: " + "; ".join(decision.reasons))
