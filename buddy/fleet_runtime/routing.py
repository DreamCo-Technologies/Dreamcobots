"""Canonical 65-MasterBot routing with 55-domain ownership safeguards.

A structurally resolved route is not an authorization grant. The 45 core
name matches remain pending GitHub identity attestation/owner review; ten
supplemental domain profiles remain unassigned; twenty shared services never
become primary domain owners.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MASTERBOTS = ROOT / "config" / "masterbot-65-registry.json"
DOMAINS = ROOT / "config" / "generated" / "masterbot-55-domain-crosswalk.json"


@lru_cache(maxsize=1)
def _masterbot_index() -> dict[int, str]:
    data = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    return {int(row["id"]): str(row["name"]) for row in data.get("divisions", [])}


@lru_cache(maxsize=1)
def _domain_index() -> dict[str, dict[str, Any]]:
    data = json.loads(DOMAINS.read_text(encoding="utf-8"))
    return {str(row["domain_name"]): row for row in data.get("domains", [])}


def resolve_route(manifest: dict[str, Any]) -> dict[str, Any]:
    """Resolve a bot's proposed primary domain and shared-service candidates."""
    division = str(manifest.get("division") or "")
    owner = str(manifest.get("primary_domain_owner") or division)
    row = _domain_index().get(owner)
    masterbots = _masterbot_index()
    proposed_id = row.get("masterbot_id") if row else None
    supplied_id = manifest.get("primary_masterbot_id")
    if supplied_id is not None:
        try:
            supplied_id = int(supplied_id)
        except (TypeError, ValueError):
            supplied_id = None
    if supplied_id is not None and supplied_id != proposed_id:
        proposed_id = None
        status = "blocked_inconsistent_primary_masterbot"
    elif not row:
        status = "blocked_domain_not_in_canonical_crosswalk"
    elif row.get("mapping_status") == "unresolved" or proposed_id is None:
        status = "supplemental_domain_unassigned_pending_owner_review"
    elif row.get("mapping_status") == "proposed_exact_name_match" and proposed_id in range(1, 46):
        status = "proposed_core_route_pending_github_identity_attestation"
    else:
        status = "blocked_invalid_domain_masterbot_mapping"

    route_valid = (
        row is not None
        and row.get("mapping_status") == "proposed_exact_name_match"
        and proposed_id in range(1, 46)
        and masterbots.get(proposed_id) == row.get("masterbot_name")
        and (supplied_id is None or supplied_id == proposed_id)
    )
    if not route_valid:
        proposed_id = None

    shared_id = manifest.get("shared_teammate_masterbot_id")
    if shared_id is not None:
        try:
            shared_id = int(shared_id)
        except (TypeError, ValueError):
            shared_id = None
        if shared_id not in range(46, 66) or shared_id not in masterbots:
            shared_id = None
            status = "blocked_invalid_shared_masterbot_route"

    return {
        "orchestrator": "Buddy",
        "execution_division": division or None,
        "canonical_domain_owner": owner or None,
        "domain_id": row.get("domain_id") if row else None,
        "primary_masterbot_id": proposed_id,
        "primary_masterbot_name": masterbots.get(proposed_id) if proposed_id else None,
        "shared_teammate_masterbot_id": shared_id,
        "shared_platform_masterbot_ids": list(range(46, 66)),
        "collaborating_masterbot_ids": [shared_id] if shared_id else [],
        "mapping_status": row.get("mapping_status") if row else "unresolved",
        "route_status": status,
        "route_valid": route_valid,
        "owner_approval_required": True,
        "github_identity_attestation_required": route_valid,
        "privileged_execution_enabled": False,
        "live_external_actions_enabled": False,
        "training_execution_enabled": False,
        "supplemental_portfolio": manifest.get("supplemental_portfolio"),
        "shared_workforce_group": manifest.get("shared_workforce_group"),
        "learning_route": "evidence_backed_reviewed_learning",
        "benchmark_route": "bot_capability_and_division_holdout_benchmarks",
    }
