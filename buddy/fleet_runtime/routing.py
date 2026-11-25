"""Governed Buddy route proposals for the 55-domain / 65-MasterBot model.

This resolver records a candidate route only. Chat approval is not a signed
GitHub owner review, and no route from this module grants dispatch or privileges.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MASTERBOTS = ROOT / "config/masterbot-65-registry.json"
DOMAINS = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
APPROVAL = ROOT / "config/review/division-owner-conversation-approval.json"


@lru_cache(maxsize=1)
def _masterbots() -> dict[int, str]:
    data = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    return {int(row["id"]): str(row["name"]) for row in data.get("divisions", [])}


@lru_cache(maxsize=1)
def _domains() -> dict[str, dict[str, Any]]:
    data = json.loads(DOMAINS.read_text(encoding="utf-8"))
    return {str(row["domain_name"]): row for row in data.get("domains", [])}


@lru_cache(maxsize=1)
def _approval() -> dict[str, Any]:
    return json.loads(APPROVAL.read_text(encoding="utf-8"))


def _base(division: str | None) -> dict[str, Any]:
    return {
        "orchestrator": "Buddy",
        "execution_division": division,
        "primary_domain_owner": None,
        "primary_masterbot_id": None,
        "primary_masterbot_name": None,
        "proposed_collaborator_masterbot_id": None,
        "related_domain": None,
        "shared_platform_masterbot_ids": list(range(46, 66)),
        "route_status": "blocked_unmapped_division",
        "route_valid": False,
        "owner_approval_required": True,
        "github_identity_attestation_required": True,
        "dispatch_allowed": False,
        "privileged_execution_enabled": False,
        "external_actions_enabled": False,
        "model_training_enabled": False,
        "source_refs": [
            "config/masterbot-65-registry.json",
            "config/generated/masterbot-55-domain-crosswalk.json",
            "config/review/division-owner-conversation-approval.json",
        ],
    }


def resolve_route(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return a non-privileged candidate route for one bot manifest."""
    division = str(manifest.get("division") or "").strip()
    route = _base(division or None)
    if not division:
        return route

    masterbots = _masterbots()
    domains = _domains()
    approval = _approval()
    domain = domains.get(division)

    if domain:
        status = domain.get("mapping_status")
        if status == "proposed_exact_name_match":
            masterbot_id = domain.get("masterbot_id")
            try:
                masterbot_id = int(masterbot_id)
            except (TypeError, ValueError):
                return route
            if masterbots.get(masterbot_id) != division or not 1 <= masterbot_id <= 45:
                return route
            approved = next((row for row in approval.get("exact_name_matches", [])
                             if row.get("domain_id") == domain.get("domain_id")
                             and row.get("masterbot_id") == masterbot_id), None)
            if not approved:
                return route
            route.update({
                "primary_domain_owner": division,
                "primary_masterbot_id": masterbot_id,
                "primary_masterbot_name": masterbots[masterbot_id],
                "route_status": "proposed_exact_name_match_pending_owner_review",
                "route_valid": True,
                "user_approval_status": approved.get("decision"),
            })
            return route

        if status == "unresolved":
            proposal = next((row for row in approval.get("supplemental_collaborators", [])
                            if row.get("domain_id") == domain.get("domain_id")), None)
            if not proposal:
                route["route_status"] = "supplemental_domain_without_collaborator_proposal"
                return route
            collaborator_id = proposal.get("proposed_collaborator_masterbot_id")
            related_domain = str(proposal.get("related_domain") or "")
            related = domains.get(related_domain)
            try:
                collaborator_id = int(collaborator_id)
            except (TypeError, ValueError):
                return route
            if (not related or related.get("mapping_status") != "proposed_exact_name_match"
                    or related.get("masterbot_id") != collaborator_id
                    or masterbots.get(collaborator_id) != related_domain):
                route["route_status"] = "blocked_invalid_supplemental_collaborator"
                return route
            route.update({
                "proposed_collaborator_masterbot_id": collaborator_id,
                "related_domain": related_domain,
                "route_status": "proposed_collaborator_pending_owner_review",
                "route_valid": True,
                "user_approval_status": proposal.get("decision"),
            })
            return route

    # Shared-platform MasterBots are service lanes, not domain owners.
    masterbot_id = next((ident for ident, name in masterbots.items() if name == division), None)
    shared_ids = set(approval.get("shared_platform_services", {}).get("masterbot_ids", []))
    if masterbot_id in shared_ids and masterbot_id in range(46, 66):
        route.update({
            "primary_domain_owner": None,
            "primary_masterbot_id": masterbot_id,
            "primary_masterbot_name": division,
            "route_status": "shared_platform_service_pending_owner_confirmation",
            "route_valid": True,
            "shared_platform_service": True,
            "available_to_all_domain_divisions": True,
        })
    return route
