"""Opt-in local Buddy community profile registry.

Does not identify people in photos or audio itself. Recognition adapters must
supply independently verified, live, consented matches; unverified matches
cannot access account information. No account credentials are stored.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import re
from pathlib import Path

_ALLOWED = {"display_name", "greeting", "interests", "pronouns", "language", "relationship", "notes"}
_ID = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")


def _safe_id(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("Invalid profile ID")
    return value


def _validate_profile(profile: dict) -> dict:
    if not isinstance(profile, dict):
        raise ValueError("Profile must be an object")
    _safe_id(profile.get("id"))
    if profile.get("consent") is not True or profile.get("adult_or_guardian_approved") is not True:
        raise ValueError("Explicit informed consent and adult/guardian approval required")
    data = profile.get("details", {})
    if not isinstance(data, dict) or set(data) - _ALLOWED:
        raise ValueError("Unapproved profile fields")
    if any(not isinstance(v, str) or len(v) > 500 for v in data.values()):
        raise ValueError("Profile details must be short strings")
    return {"id": profile["id"], "details": data, "consent": True,
            "adult_or_guardian_approved": True, "face_opt_in": profile.get("face_opt_in") is True,
            "voice_opt_in": profile.get("voice_opt_in") is True}


def enroll(profile: dict, *, store: Path) -> dict:
    """Write non-biometric profile data only. Store must be user-private."""
    clean = _validate_profile(profile)
    store.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = store / (_safe_id(clean["id"]) + ".json")
    if target.exists():
        raise FileExistsError("Profile exists; explicit update flow required")
    target.write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o600)
    return {"id": clean["id"], "status": "enrolled", "biometric_templates": "not_collected"}


def delete(profile_id: str, *, store: Path) -> dict:
    """Delete profile metadata; biometric vault and backups require separate purge."""
    target = store / (_safe_id(profile_id) + ".json")
    if not target.exists():
        return {"id": profile_id, "deleted": False}
    target.unlink()
    return {"id": profile_id, "deleted": True, "note": "Purge linked biometric vault templates and backups separately"}


def greet(profile_id: str, *, store: Path, match: dict | None = None) -> dict:
    """Require independently verified opt-in face/voice match; never trust a supplied name."""
    path = store / (_safe_id(profile_id) + ".json")
    if not path.exists():
        return {"status": "unknown", "text": "Hello! Welcome to Buddy."}
    row = json.loads(path.read_text(encoding="utf-8"))
    match = match or {}
    modality = match.get("modality")
    allowed = (modality == "face" and row.get("face_opt_in")) or (modality == "voice" and row.get("voice_opt_in"))
    if not (allowed and match.get("verified_by_trusted_adapter") is True
            and match.get("liveness_passed") is True
            and match.get("consent_active") is True
            and hmac.compare_digest(str(match.get("profile_id", "")), profile_id)):
        return {"status": "unverified", "text": "Hello! How may I help you?"}
    name = row.get("details", {}).get("display_name", "friend")
    return {"status": "recognized", "text": f"Hello, {name}! It's nice to see you.", "profile_id": profile_id,
            "account_access": False}
