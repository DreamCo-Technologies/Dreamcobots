"""Canonical 65-MasterBot routing with 55-domain ownership safeguards.

A structurally resolved route is not an authorization grant. The 45 core
name matches remain pending GitHub identity attestation/owner review; ten
supplemental domain profiles remain unassigned; twenty shared services never
become primary domain owners. Dream3D is a proposed subportfolio, not a new
canonical or supplemental domain.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MASTERBOTS = ROOT / "config" / "masterbot-65-registry.json"
DOMAINS = ROOT / "config" / "generated" / "masterbot-55-domain-crosswalk.json"
CHARTERS = ROOT / "config" / "supplemental-portfolio-capability-charters.json"
TEAMMATE_CROSSWALK = ROOT / "config" / "bots" / "teammate-lane-division-crosswalk.json"
CORE_CROSSWALK = ROOT / "config" / "generated" / "masterbot-45-domain-crosswalk.json"


@lru_cache(maxsize=1)
def _masterbot_index() -> dict[int, str]:
    data = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    return {int(row["id"]): str(row["name"]) for row in data.get("divisions", [])}


@lru_cache(maxsize=1)
def _domain_index() -> dict[str, dict[str, Any]]:
    data = json.loads(DOMAINS.read_text(encoding="utf-8"))
    return {str(row["domain_name"]): row for row in data.get("domains", [])}


@lru_cache(maxsize=1)
def _core_masterbot_index() -> dict[str, int]:
    data = json.loads(CORE_CROSSWALK.read_text(encoding="utf-8"))
    return {
        str(row["domain_name"]): int(row["masterbot_id"])
        for row in data.get("domains", [])
    }


@lru_cache(maxsize=1)
def _portfolio_index() -> dict[str, dict[str, Any]]:
    data = json.loads(CHARTERS.read_text(encoding="utf-8"))
    return {str(row["portfolio"]): row for row in data.get("portfolios", [])}


@lru_cache(maxsize=1)
def _teammate_index() -> dict[str, dict[str, Any]]:
    data = json.loads(TEAMMATE_CROSSWALK.read_text(encoding="utf-8"))
    return {str(row["lane_slug"]): row for row in data.get("lanes", [])}


def _safe_int(value: Any) -> tuple[int | None, bool]:
    if value is None:
        return None, False
    if isinstance(value, bool):
        return None, True
    try:
        return int(value), False
    except (TypeError, ValueError):
        return None, True


def resolve_route(manifest: dict[str, Any]) -> dict[str, Any]:
    """Resolve only structurally valid core routes; keep supplemental domains unassigned."""
    division = str(manifest.get("division") or "")
    source_division = str(manifest.get("source_division") or "")
    portfolio_name = str(manifest.get("supplemental_portfolio") or source_division or division)
    if division in {"", "UNASSIGNED"} and source_division:
        division = source_division
    masterbots = _masterbot_index()
    domains = _domain_index()
    portfolios = _portfolio_index()
    teammates = _teammate_index()

    portfolio = portfolios.get(portfolio_name) or portfolios.get(division)
    is_supplemental_domain = bool(
        portfolio and portfolio.get("classification") == "supplemental_domain_profile"
    )
    is_dream3d = portfolio_name == "Dream3D" or division == "Dream3D"
    is_teammate = division == "GrokTeammates" or manifest.get("shared_workforce_group") == "GrokTeammates"

    proposed_owner = None
    shared_id = None
    shared_route_status = "not_requested"

    if is_supplemental_domain:
        # Charter owner is a proposal only. The 55-domain crosswalk remains unresolved.
        owner = portfolio_name
        proposed_owner = str(portfolio.get("owner") or "") or None
        row = domains.get(portfolio_name)
        status = "supplemental_domain_unassigned_pending_owner_review"
    elif is_dream3d:
        # Dream3D is a specialist portfolio under a core owner, not a new domain.
        owner = str((portfolio or {}).get("owner") or manifest.get("primary_domain_owner") or "")
        proposed_owner = owner or None
        row = domains.get(owner)
        status = "proposed_specialist_subportfolio_route_pending_owner_review"
    elif is_teammate:
        teammate = teammates.get(str(manifest.get("slug") or ""))
        if teammate:
            owner = str(teammate.get("canonical_owner_division") or "")
            shared_id = teammate.get("shared_masterbot_id")
        else:
            owner = str(manifest.get("primary_domain_owner") or "")
        row = domains.get(owner)
        status = "proposed_core_route_pending_github_identity_attestation" if row else "blocked_domain_not_in_canonical_crosswalk"
    else:
        owner = str(manifest.get("primary_domain_owner") or division)
        row = domains.get(owner)
        status = "proposed_core_route_pending_github_identity_attestation" if row else "blocked_domain_not_in_canonical_crosswalk"

    proposed_id = row.get("masterbot_id") if row else None
    raw_supplied_id = manifest.get("primary_masterbot_id")
    supplied_id, invalid_supplied_id = _safe_int(raw_supplied_id)

    if is_supplemental_domain:
        # A proposed owner/ID must never be promoted to an actual primary route.
        proposed_id = _core_masterbot_index().get(str(proposed_owner)) if proposed_owner else None
        route_valid = False
        primary_id = None
    elif invalid_supplied_id:
        status = "blocked_invalid_primary_masterbot_id"
        route_valid = False
        primary_id = None
    elif row is None:
        route_valid = False
        primary_id = None
    elif row.get("mapping_status") == "unresolved" or proposed_id is None:
        status = "supplemental_domain_unassigned_pending_owner_review"
        route_valid = False
        primary_id = None
    elif row.get("mapping_status") == "proposed_exact_name_match" and proposed_id in range(1, 46):
        if supplied_id is not None and supplied_id != proposed_id:
            status = "blocked_inconsistent_primary_masterbot"
            route_valid = False
            primary_id = None
        elif masterbots.get(int(proposed_id)) != row.get("masterbot_name"):
            status = "blocked_invalid_domain_masterbot_mapping"
            route_valid = False
            primary_id = None
        else:
            route_valid = True
            primary_id = int(proposed_id)
    else:
        status = "blocked_invalid_domain_masterbot_mapping"
        route_valid = False
        primary_id = None

    if is_dream3d and route_valid:
        status = "proposed_specialist_subportfolio_route_pending_owner_review"

    if is_teammate:
        shared_id, invalid_shared_id = _safe_int(shared_id if shared_id is not None else manifest.get("shared_teammate_masterbot_id"))
        if invalid_shared_id or shared_id not in range(46, 66) or shared_id not in masterbots:
            shared_id = None
            shared_route_status = "blocked_invalid_shared_masterbot_route"
        else:
            shared_route_status = "proposed_shared_service_collaboration_pending_owner_confirmation"
    elif manifest.get("shared_teammate_masterbot_id") is not None:
        shared_id, invalid_shared_id = _safe_int(manifest.get("shared_teammate_masterbot_id"))
        if invalid_shared_id or shared_id not in range(46, 66) or shared_id not in masterbots:
            shared_id = None
            shared_route_status = "blocked_invalid_shared_masterbot_route"
        else:
            shared_route_status = "proposed_shared_service_collaboration_pending_owner_confirmation"

    return {
        "orchestrator": "Buddy",
        "execution_division": division or None,
        "canonical_domain_owner": owner if route_valid else None,
        "proposed_domain_owner": proposed_owner,
        "domain_id": row.get("domain_id") if row else None,
        "primary_masterbot_id": primary_id,
        "primary_masterbot_name": masterbots.get(primary_id) if primary_id else None,
        "proposed_primary_masterbot_id": proposed_id if not route_valid else None,
        "shared_teammate_masterbot_id": shared_id,
        "shared_route_status": shared_route_status,
        "shared_route_valid": shared_id is not None,
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
        "supplemental_portfolio": manifest.get("supplemental_portfolio") or (portfolio.get("portfolio") if portfolio else None),
        "shared_workforce_group": "GrokTeammates" if is_teammate else manifest.get("shared_workforce_group"),
        "learning_route": "evidence_backed_reviewed_learning",
        "benchmark_route": "bot_capability_and_division_holdout_benchmarks",
    }
