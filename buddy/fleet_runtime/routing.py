"""Buddy's canonical division and MasterBot routing resolver.

Routing is inspectable and non-privileged. It never grants external-action,
deployment, payment, or model-training permissions.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MASTERBOTS = ROOT / "config" / "masterbot-65-registry.json"
DOMAINS = ROOT / "config" / "generated" / "masterbot-45-domain-crosswalk.json"
PORTFOLIOS = ROOT / "config" / "supplemental-portfolio-capability-charters.json"


@lru_cache(maxsize=1)
def _masterbot_index() -> dict[int, str]:
    data = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    return {int(row["id"]): str(row["name"]) for row in data.get("divisions", [])}


@lru_cache(maxsize=1)
def _domain_index() -> dict[str, int]:
    data = json.loads(DOMAINS.read_text(encoding="utf-8"))
    return {str(row["domain_name"]): int(row["masterbot_id"]) for row in data.get("domains", [])}


@lru_cache(maxsize=1)
def _portfolio_index() -> dict[str, dict[str, Any]]:
    data = json.loads(PORTFOLIOS.read_text(encoding="utf-8"))
    return {str(row["portfolio"]): row for row in data.get("portfolios", [])}


def resolve_route(manifest: dict[str, Any]) -> dict[str, Any]:
    """Resolve one bot to its canonical domain MasterBot and Buddy services."""
    division = str(manifest.get("division") or "")
    owner = str(manifest.get("primary_domain_owner") or division)
    primary_id = manifest.get("primary_masterbot_id")
    if primary_id is None:
        primary_id = _domain_index().get(owner)
    try:
        primary_id = int(primary_id) if primary_id is not None else None
    except (TypeError, ValueError):
        primary_id = None

    masterbots = _masterbot_index()
    domain_index = _domain_index()
    status = str(manifest.get("division_route_status") or "discovery_review_required")
    valid = (
        bool(division)
        and owner in domain_index
        and primary_id in masterbots
        and domain_index.get(owner) == primary_id
    )
    if not valid:
        status = "blocked_unmapped_or_inconsistent_route"
        primary_id = None

    portfolio_name = manifest.get("supplemental_portfolio")
    if portfolio_name:
        portfolio = _portfolio_index().get(str(portfolio_name))
        if not portfolio or portfolio.get("owner") != owner or division != str(portfolio_name):
            status = "blocked_specialist_owner_mismatch"
            valid = False

    shared_id = manifest.get("shared_teammate_masterbot_id")
    if shared_id is not None:
        try:
            shared_id = int(shared_id)
        except (TypeError, ValueError):
            shared_id = None
        if shared_id not in range(46, 66):
            status = "blocked_invalid_shared_masterbot_route"
            valid = False
            shared_id = None

    primary_name = masterbots.get(primary_id) if primary_id else None
    return {
        "orchestrator": "Buddy",
        "execution_division": division or None,
        "canonical_division": owner or None,
        "primary_domain_owner": owner or None,
        "source_division": manifest.get("source_division"),
        "supplemental_portfolio": portfolio_name,
        "shared_workforce_group": manifest.get("shared_workforce_group"),
        "primary_masterbot_id": primary_id,
        "primary_masterbot_name": primary_name,
        "shared_teammate_masterbot_id": shared_id,
        "shared_platform_masterbot_ids": list(range(46, 66)),
        "collaborating_masterbot_ids": [shared_id] if shared_id else [],
        "route_status": status,
        "route_valid": valid,
        "owner_approval_required": True,
        "privileged_execution_enabled": False,
        "queue": "dependency_aware_governed_task_queue",
        "learning_route": "evidence_backed_reviewed_learning",
        "benchmark_route": "bot_capability_and_division_holdout_benchmarks",
    }
