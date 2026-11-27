"""Training-use policy for first-party DreamCo Bootcamp assets."""
from __future__ import annotations
from typing import Any, Mapping

FIRST_PARTY_SCOPE = "first_party_dreamco"

def evaluate_bootcamp_learning_use(asset: Mapping[str, Any]) -> dict[str, Any]:
    """Avoid repeated consent prompts for DreamCo-owned course assets.

    This policy does not grant rights to third-party works, learner submissions,
    customer content, personal data, secrets, or safety-restricted material.
    """
    scope = asset.get("scope")
    if scope != FIRST_PARTY_SCOPE:
        return {"eligible": False, "reason": "not_first_party_dreamco", "requires_separate_permission": True}
    if asset.get("ownership_confirmed") is not True:
        return {"eligible": False, "reason": "ownership_or_authority_not_confirmed", "requires_separate_permission": True}
    if asset.get("contains_unlicensed_third_party_material") is True:
        return {"eligible": False, "reason": "third_party_material_present", "requires_separate_permission": True}
    if asset.get("learner_submitted") is True:
        return {"eligible": False, "reason": "learner_submission_uses_separate_terms", "requires_separate_permission": True}
    if asset.get("contains_personal_data") is True:
        return {"eligible": False, "reason": "privacy_review_required", "requires_separate_permission": False}
    if asset.get("contains_secrets") is True:
        return {"eligible": False, "reason": "secrets_must_be_removed", "requires_separate_permission": False}
    if asset.get("safety_review_passed") is not True:
        return {"eligible": False, "reason": "safety_review_required", "requires_separate_permission": False}
    return {
        "eligible": True,
        "reason": "first_party_standing_authorization",
        "requires_separate_permission": False,
        "allowed_uses": ["index", "retrieve", "summarize", "evaluate", "internal_model_training"],
    }
