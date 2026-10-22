"""Evidence-based, authorized reverse-engineering coverage tracker.

This module compares *observed* features against independently tested Buddy
implementations. It neither extracts proprietary code nor bypasses protections.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

KINDS = frozenset({"web_app","mobile_app","desktop_app","api","workflow",
                   "bot","device","model","hardware","database","ui"})
EVIDENCE = frozenset({"public_docs","licensed_source","authorized_demo",
                      "user_owned_artifact","sandbox_test"})
STATES = frozenset({"observed","specified","implemented","tested","verified"})

@dataclass(frozen=True)
class Feature:
    feature_id: str
    target_kind: str
    evidence_type: str
    evidence_ref: str
    rights_verified: bool
    state: str
    independent_test_ref: str = ""

def audit(features: Iterable[Feature]) -> dict:
    """Reject unsupported evidence and report actual capability gaps."""
    rows = list(features)
    seen = set()
    results = []
    for f in rows:
        if not f.feature_id or f.feature_id in seen:
            raise ValueError("Missing or duplicate feature ID")
        seen.add(f.feature_id)
        if f.target_kind not in KINDS or f.evidence_type not in EVIDENCE or f.state not in STATES:
            raise ValueError("Unknown target, evidence or state")
        if not f.evidence_ref or not f.rights_verified:
            results.append({"feature_id": f.feature_id, "status": "blocked_rights_or_evidence"})
            continue
        if f.state == "verified" and f.independent_test_ref:
            results.append({"feature_id": f.feature_id, "status": "verified",
                            "test_ref": f.independent_test_ref})
        else:
            results.append({"feature_id": f.feature_id, "status": "gap",
                            "current_state": f.state,
                            "requires": "independent_test_and_verified_outcome"})
    return {"total": len(results),
            "verified": sum(x["status"] == "verified" for x in results),
            "blocked": sum(x["status"] == "blocked_rights_or_evidence" for x in results),
            "gaps": sum(x["status"] == "gap" for x in results),
            "features": results}
