"""Sellability gate: decides whether an asset, lesson, or package may be used for training and/or sold.

Implements config/buddy-training-data-provenance-policy.json. A lesson/package inherits the most
restrictive decision among its inputs. Missing required fields -> treated as unknown_do_not_publish.
"""
from __future__ import annotations

from typing import Iterable, Mapping

REQUIRED = (
    "asset_id", "source_type", "source", "collection_date", "owner", "license", "ownership_class",
    "commercial_redistribution_allowed", "attribution_required", "share_alike_required",
    "transformation_history", "provenance_hash", "review_status",
)
ALWAYS_SELLABLE = {"dreamco_owned", "dreamco_commissioned_with_assignment", "synthetic_generated_by_dreamco",
                   "public_domain_or_publicly_reusable"}
LICENSE_DEPENDENT = {"licensed_for_use", "open_license_with_conditions"}
RANK = {"blocked": 0, "reference_only": 1, "train_only": 2, "sellable": 3}


def decide(rec: Mapping) -> dict:
    """Return {"decision": blocked|reference_only|train_only|sellable, "reasons": [...]}."""
    missing = [f for f in REQUIRED if f not in rec or rec[f] in (None, "")]
    if missing:
        return {"decision": "blocked", "reasons": [f"missing:{f}" for f in missing]}
    cls = rec["ownership_class"]
    if cls == "unknown_do_not_publish":
        return {"decision": "blocked", "reasons": ["unknown ownership"]}
    if rec["review_status"] == "rejected":
        return {"decision": "blocked", "reasons": ["rights review rejected"]}
    if cls == "third_party_reference_only":
        return {"decision": "reference_only", "reasons": ["third-party: summaries/citations/original tasks only"]}
    if cls == "user_contributed_with_permission" or rec["source_type"] == "user_upload":
        c = rec.get("consent") or {}
        if not c or c.get("revoked") or len(str(c.get("attestation", "")).strip()) < 20:
            return {"decision": "blocked", "reasons": ["no valid consent"]}
        scope = set(c.get("scope", []))
        if "sell" in scope and rec["commercial_redistribution_allowed"] and rec["review_status"] == "approved":
            return {"decision": "sellable", "reasons": ["user consent includes sell"]}
        if "train" in scope or "sell" in scope:
            return {"decision": "train_only", "reasons": ["consent lacks sell scope or not approved"]}
        return {"decision": "blocked", "reasons": ["consent scope excludes train"]}
    if cls in LICENSE_DEPENDENT and not rec["commercial_redistribution_allowed"]:
        return {"decision": "train_only", "reasons": ["license does not allow commercial redistribution"]}
    if cls in ALWAYS_SELLABLE or cls in LICENSE_DEPENDENT:
        if rec["review_status"] != "approved":
            return {"decision": "train_only", "reasons": ["awaiting rights review"]}
        return {"decision": "sellable", "reasons": [cls]}
    return {"decision": "blocked", "reasons": [f"unrecognized class {cls}"]}


def combine(records: Iterable[Mapping]) -> dict:
    """Most restrictive decision wins. Empty input is blocked."""
    results = [(r.get("asset_id", "?"), decide(r)) for r in records]
    if not results:
        return {"decision": "blocked", "reasons": ["no inputs"], "inputs": []}
    worst = min(results, key=lambda x: RANK[x[1]["decision"]])
    return {"decision": worst[1]["decision"], "limiting_asset": worst[0], "reasons": worst[1]["reasons"],
            "inputs": [{"asset_id": a, **d} for a, d in results]}
