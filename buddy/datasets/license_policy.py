"""Conservative, machine-readable triage for public dataset license candidates.

This is a routing aid, not a legal opinion. A permissive license tag alone never
proves rights in every file or permission for every intended model-training use.
"""
from __future__ import annotations
import re
from typing import Any

# Explicitly recognizable public licenses with broad reuse permissions.
# Share-alike, non-commercial, research-only, custom, missing and unknown terms
# are intentionally excluded from automatic training-candidate triage.
ALLOWLIST = {
    "CC0-1.0", "CC0", "CC-BY-4.0", "CC-BY-3.0",
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
    "Unlicense", "0BSD"
}
ALIASES = {
    "cc0": "CC0-1.0", "cc0-1.0": "CC0-1.0",
    "cc-by-4.0": "CC-BY-4.0", "cc-by-3.0": "CC-BY-3.0",
    "apache 2.0": "Apache-2.0", "apache-2.0": "Apache-2.0",
    "mit": "MIT", "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause", "unlicense": "Unlicense",
    "0bsd": "0BSD"
}

def normalize_license(value: Any) -> str:
    raw = str(value or "").strip()
    key = re.sub(r"\s+", " ", raw).lower()
    return ALIASES.get(key, raw)

def assess_training_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    license_id = normalize_license(candidate.get("license"))
    explicit = candidate.get("ai_training_allowed") is True
    content_rights = candidate.get("content_rights_verified") is True
    privacy = candidate.get("privacy_review") == "PASSED"
    provenance = bool(candidate.get("source") and candidate.get("id") and str(candidate.get("url", "")).startswith("https://"))
    allowed_license = license_id in ALLOWLIST
    if allowed_license and explicit and content_rights and privacy and provenance:
        status = "PERMISSIVE_LICENSE_TRAINING_CANDIDATE_REQUIRES_DATA_QUALITY_AND_FINAL_REVIEW"
    elif not license_id or license_id.lower() in {"unknown", "other", "none", "null"}:
        status = "BLOCKED_UNKNOWN_LICENSE"
    elif not allowed_license:
        status = "BLOCKED_LICENSE_REQUIRES_MANUAL_TERMS_REVIEW"
    elif not explicit:
        status = "BLOCKED_NO_EXPLICIT_AI_TRAINING_PERMISSION"
    elif not content_rights:
        status = "BLOCKED_CONTENT_RIGHTS_UNVERIFIED"
    elif not privacy:
        status = "BLOCKED_PRIVACY_REVIEW"
    else:
        status = "BLOCKED_PROVENANCE"
    return {
        "license": license_id or None,
        "allowlisted_license": allowed_license,
        "ai_training_permission_explicit": explicit,
        "content_rights_verified": content_rights,
        "privacy_review": privacy,
        "status": status,
        "training_approved": False,
        "note": "This automated triage is not legal advice or final dataset approval; inspect every source, file, contributor right, privacy obligation and applicable term."
    }
