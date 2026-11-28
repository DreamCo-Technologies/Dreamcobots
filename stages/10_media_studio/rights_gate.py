"""Fail-closed rights checks for media assets, model weights, and dependencies."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

USES = {"study", "adapt", "display", "redistribute", "commercial_use", "train", "voice_clone", "likeness_clone"}

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
    if record.get("ownership_class") in {None, "", "unknown_do_not_publish"}:
        reasons.append("ownership class is unknown")
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
    if record.get("source_sha256") and record.get("observed_sha256") != record.get("source_sha256"):
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
    if model.get("restrictions"):
        reasons.append("model has unresolved restrictions")
    use = "train" if training else "commercial_use" if commercial else "display"
    return RightsDecision(not reasons, model_id, use, tuple(reasons))

def require_allowed(decision: RightsDecision) -> None:
    if not decision.allowed:
        raise PermissionError(f"Rights gate blocked {decision.asset_id}: " + "; ".join(decision.reasons))
