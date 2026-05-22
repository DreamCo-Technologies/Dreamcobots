"""
REST-style API module for the Military Contract Bot.

Provides a lightweight programmatic interface so external systems
(dashboards, orchestrators, government portals) can integrate with the bot
without importing the full class hierarchy.

All endpoints accept / return plain Python dicts to keep the module
free of framework dependencies — mount these handlers under any WSGI/ASGI
framework (Flask, FastAPI, Django REST) in production.
"""

from __future__ import annotations

import time
from typing import Any, Optional

# Lazy import to avoid circular dependency
_bot_instance = None


def _get_bot():
    """Return the singleton MilitaryContractBot instance (ENTERPRISE tier)."""
    global _bot_instance
    if _bot_instance is None:
        from military_contract_bot import MilitaryContractBot, Tier
        _bot_instance = MilitaryContractBot(tier=Tier.ENTERPRISE)
    return _bot_instance


# ---------------------------------------------------------------------------
# API response helpers
# ---------------------------------------------------------------------------

def _ok(data: Any, status: int = 200) -> dict:
    return {"status": status, "ok": True, "data": data, "ts": time.time()}


def _err(message: str, status: int = 400) -> dict:
    return {"status": status, "ok": False, "error": message, "ts": time.time()}


# ---------------------------------------------------------------------------
# Contract search endpoints
# ---------------------------------------------------------------------------

def api_search_contracts(
    keyword: str = "",
    agency: Optional[str] = None,
    naics: Optional[str] = None,
    min_value: float = 0,
    max_value: Optional[float] = None,
    set_aside: Optional[str] = None,
) -> dict:
    """Search military contracts by keyword and filters.

    GET /api/v1/contracts/search
    """
    try:
        bot = _get_bot()
        results = bot.search_contracts(
            keyword=keyword,
            agency=agency,
            naics=naics,
            min_value=min_value,
            max_value=max_value,
            set_aside=set_aside,
        )
        return _ok({"contracts": results, "count": len(results)})
    except Exception as exc:
        return _err(str(exc))


def api_get_opportunity(opportunity_id: str) -> dict:
    """Get details for a single opportunity.

    GET /api/v1/contracts/{opportunity_id}
    """
    try:
        bot = _get_bot()
        result = bot.get_opportunity(opportunity_id)
        if result is None:
            return _err(f"Opportunity '{opportunity_id}' not found.", status=404)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def api_analyze_opportunity(opportunity_id: str) -> dict:
    """Run AI analysis on a single opportunity.

    POST /api/v1/contracts/{opportunity_id}/analyze
    """
    try:
        bot = _get_bot()
        result = bot.analyze_opportunity(opportunity_id)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


# ---------------------------------------------------------------------------
# Proposal / pipeline endpoints
# ---------------------------------------------------------------------------

def api_submit_proposal(opportunity_id: str, proposal: dict) -> dict:
    """Submit a proposal for an opportunity.

    POST /api/v1/contracts/{opportunity_id}/proposals
    """
    try:
        bot = _get_bot()
        result = bot.submit_proposal(opportunity_id, proposal)
        return _ok(result, status=201)
    except Exception as exc:
        return _err(str(exc))


def api_list_proposals() -> dict:
    """List all submitted proposals.

    GET /api/v1/proposals
    """
    try:
        bot = _get_bot()
        return _ok({"proposals": bot.list_proposals()})
    except Exception as exc:
        return _err(str(exc))


# ---------------------------------------------------------------------------
# Compliance endpoints
# ---------------------------------------------------------------------------

def api_check_compliance(opportunity_id: str, controls: Optional[list] = None) -> dict:
    """Run compliance check for an opportunity.

    POST /api/v1/contracts/{opportunity_id}/compliance
    """
    try:
        bot = _get_bot()
        opp = bot.get_opportunity(opportunity_id)
        if opp is None:
            return _err(f"Opportunity '{opportunity_id}' not found.", status=404)
        from mil_compliance import check_cmmc_compliance, validate_clauses
        cmmc = check_cmmc_compliance(controls or [], opp.get("cmmc_level", 1))
        clauses = validate_clauses(
            opp.get("far_clauses", []),
            opp.get("value", 0),
        )
        return _ok({"cmmc": cmmc, "clause_validation": clauses})
    except Exception as exc:
        return _err(str(exc))


# ---------------------------------------------------------------------------
# Analytics / monitoring endpoints
# ---------------------------------------------------------------------------

def api_get_analytics() -> dict:
    """Get current performance analytics.

    GET /api/v1/analytics
    """
    try:
        bot = _get_bot()
        return _ok(bot.analytics.get_summary())
    except Exception as exc:
        return _err(str(exc))


def api_health_check() -> dict:
    """Health / readiness probe.

    GET /api/v1/health
    """
    try:
        bot = _get_bot()
        summary = bot.get_summary()
        return _ok({
            "healthy": True,
            "tier": summary.get("tier"),
            "total_opportunities": summary.get("total_opportunities"),
            "uptime_seconds": bot.analytics.uptime_seconds(),
        })
    except Exception as exc:
        return _err(str(exc), status=503)


# ---------------------------------------------------------------------------
# Alert endpoints
# ---------------------------------------------------------------------------

def api_add_alert(keyword: str) -> dict:
    """Register a new alert keyword.

    POST /api/v1/alerts
    """
    try:
        bot = _get_bot()
        result = bot.add_alert_keyword(keyword)
        return _ok(result, status=201)
    except Exception as exc:
        return _err(str(exc))


def api_list_alerts() -> dict:
    """List all registered alert keywords.

    GET /api/v1/alerts
    """
    try:
        bot = _get_bot()
        return _ok({"alerts": bot.get_alerts()})
    except Exception as exc:
        return _err(str(exc))
