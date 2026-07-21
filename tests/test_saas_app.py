"""Tests for api/app.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from api.app import DreamCoSaaSApp, authenticate, _get_tier, VALID_API_KEYS, TIER_DAILY_LIMITS
from core.dreamco_orchestrator import DreamCoOrchestrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app():
    orch = DreamCoOrchestrator()
    orch.run_all_bots = lambda: [
        {"bot_name": "stub", "output": {"revenue": 100}, "validation": {"scale": False}, "error": None}
    ]
    return DreamCoSaaSApp(orchestrator=orch)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuthenticate:
    def test_valid_demo_key(self):
        assert authenticate("dreamco_demo_key") is True

    def test_invalid_key(self):
        assert authenticate("bad_key_xyz") is False

    def test_empty_key(self):
        assert authenticate("") is False


# ---------------------------------------------------------------------------
# Tier resolution
# ---------------------------------------------------------------------------

class TestGetTier:
    def test_pro_prefix(self):
        assert _get_tier("dreamco_pro_abc123") == "PRO"

    def test_enterprise_prefix(self):
        assert _get_tier("dreamco_ent_xyz") == "ENTERPRISE"

    def test_demo_key_is_free(self):
        assert _get_tier("dreamco_demo_key") == "FREE"

    def test_unknown_key_is_free(self):
        assert _get_tier("unknown_key") == "FREE"


# ---------------------------------------------------------------------------
# handle_run_bots
# ---------------------------------------------------------------------------

class TestHandleRunBots:
    def test_unauthorized_returns_401(self):
        app = _make_app()
        body, status = app.handle_run_bots("bad_key")
        assert status == 401
        assert "error" in body

    def test_authorized_returns_200(self):
        app = _make_app()
        body, status = app.handle_run_bots("dreamco_demo_key")
        assert status == 200
        assert "results" in body

    def test_rate_limit_enforced(self):
        app = _make_app()
        limit = TIER_DAILY_LIMITS["FREE"]
        for _ in range(limit):
            app.handle_run_bots("dreamco_demo_key")
        body, status = app.handle_run_bots("dreamco_demo_key")
        assert status == 429

    def test_tier_in_response(self):
        app = _make_app()
        body, status = app.handle_run_bots("dreamco_demo_key")
        assert "tier" in body


# ---------------------------------------------------------------------------
# handle_run_single
# ---------------------------------------------------------------------------

class TestHandleRunSingle:
    def test_unauthorized_returns_401(self):
        app = _make_app()
        body, status = app.handle_run_single("bad_key", "some.path", "bot")
        assert status == 401

    def test_authorized_returns_result(self):
        app = _make_app()
        body, status = app.handle_run_single("dreamco_demo_key", "nonexistent.module", "test_bot")
        assert status == 200
        assert "result" in body


# ---------------------------------------------------------------------------
# handle_summary
# ---------------------------------------------------------------------------

class TestHandleSummary:
    def test_free_tier_blocked(self):
        app = _make_app()
        body, status = app.handle_summary("dreamco_demo_key")
        assert status == 403

    def test_unauthorized_returns_401(self):
        app = _make_app()
        body, status = app.handle_summary("bad_key")
        assert status == 401


# ---------------------------------------------------------------------------
# handle_health
# ---------------------------------------------------------------------------

class TestHandleHealth:
    def test_health_returns_200(self):
        app = _make_app()
        body, status = app.handle_health()
        assert status == 200
        assert body["status"] == "ok"
