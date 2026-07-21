"""
Tests for the God Bot master controller and the module-level run() functions
added to the four core DreamCo bots (gov_bot, real_estate_bot, side_hustle_bot,
job_bot).
"""

from __future__ import annotations

import os
import sys
import types
from unittest.mock import patch

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_mock_bot_module(name: str, revenue: int, leads: int) -> types.ModuleType:
    """Return a fake module whose run() returns a standard result dict."""
    mod = types.ModuleType(name)
    mod.run = lambda: {  # type: ignore[attr-defined]
        "status": "success",
        "leads": leads,
        "leads_generated": leads,
        "revenue": revenue,
    }
    return mod


# ===========================================================================
# Module-level run() — gov_bot
# ===========================================================================


class TestGovBotRun:
    def _import_gov_bot(self):
        import importlib.util as _util

        path = os.path.join(
            REPO_ROOT,
            "bots",
            "government-contract-grant-bot",
            "government_contract_grant_bot.py",
        )
        spec = _util.spec_from_file_location("gov_bot_test_mod", path)
        assert spec and spec.loader
        mod = _util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    def test_run_returns_dict(self):
        mod = self._import_gov_bot()
        result = mod.run()
        assert isinstance(result, dict)

    def test_run_status_success(self):
        mod = self._import_gov_bot()
        assert mod.run()["status"] == "success"

    def test_run_leads(self):
        mod = self._import_gov_bot()
        assert mod.run()["leads"] == 10

    def test_run_revenue(self):
        mod = self._import_gov_bot()
        assert mod.run()["revenue"] == 500

    def test_run_leads_generated(self):
        mod = self._import_gov_bot()
        assert mod.run()["leads_generated"] == 10


# ===========================================================================
# Module-level run() — real_estate_bot
# ===========================================================================


class TestRealEstateBotRun:
    def test_run_returns_dict(self):
        from bots.real_estate_bot.real_estate_bot import run

        result = run()
        assert isinstance(result, dict)

    def test_run_status_success(self):
        from bots.real_estate_bot.real_estate_bot import run

        assert run()["status"] == "success"

    def test_run_leads(self):
        from bots.real_estate_bot.real_estate_bot import run

        assert run()["leads"] == 5

    def test_run_revenue(self):
        from bots.real_estate_bot.real_estate_bot import run

        assert run()["revenue"] == 2000

    def test_run_leads_generated(self):
        from bots.real_estate_bot.real_estate_bot import run

        assert run()["leads_generated"] == 5


# ===========================================================================
# Module-level run() — side_hustle_bot
# ===========================================================================


class TestSideHustleBotRun:
    def _import_side_hustle_bot(self):
        import importlib.util as _util

        path = os.path.join(REPO_ROOT, "bots", "ai-side-hustle-bots", "bot.py")
        spec = _util.spec_from_file_location("side_hustle_bot_test_mod", path)
        assert spec and spec.loader
        mod = _util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    def test_run_returns_dict(self):
        mod = self._import_side_hustle_bot()
        assert isinstance(mod.run(), dict)

    def test_run_status_success(self):
        mod = self._import_side_hustle_bot()
        assert mod.run()["status"] == "success"

    def test_run_leads(self):
        mod = self._import_side_hustle_bot()
        assert mod.run()["leads"] == 20

    def test_run_revenue(self):
        mod = self._import_side_hustle_bot()
        assert mod.run()["revenue"] == 800

    def test_run_leads_generated(self):
        mod = self._import_side_hustle_bot()
        assert mod.run()["leads_generated"] == 20


# ===========================================================================
# Module-level run() — job_bot
# ===========================================================================


class TestJobBotRun:
    def _import_job_bot(self):
        import importlib.util as _util

        path = os.path.join(
            REPO_ROOT, "bots", "selenium-job-application-bot", "bot.py"
        )
        spec = _util.spec_from_file_location("job_bot_test_mod", path)
        assert spec and spec.loader
        mod = _util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

    def test_run_returns_dict(self):
        mod = self._import_job_bot()
        assert isinstance(mod.run(), dict)

    def test_run_status_success(self):
        mod = self._import_job_bot()
        assert mod.run()["status"] == "success"

    def test_run_leads(self):
        mod = self._import_job_bot()
        assert mod.run()["leads"] == 15

    def test_run_revenue(self):
        mod = self._import_job_bot()
        assert mod.run()["revenue"] == 600

    def test_run_leads_generated(self):
        mod = self._import_job_bot()
        assert mod.run()["leads_generated"] == 15


# ===========================================================================
# GodBot
# ===========================================================================


class TestGodBotInit:
    def test_default_registry_has_four_bots(self):
        from bots.god_bot.god_bot import GodBot, BOT_REGISTRY

        god = GodBot()
        assert len(god.registry) == 4

    def test_custom_registry(self):
        from bots.god_bot.god_bot import GodBot

        god = GodBot(registry=[("some.path", "test_bot")])
        assert len(god.registry) == 1


class TestGodBotRunAll:
    def _make_registry_with_mocks(self, bots_data):
        """Build a registry using in-process fake module names."""
        registry = []
        for bot_name, revenue, leads in bots_data:
            mod_name = f"_mock_god_bot_{bot_name}"
            sys.modules[mod_name] = _make_mock_bot_module(mod_name, revenue, leads)
            registry.append((mod_name, bot_name))
        return registry

    def teardown_method(self):
        for key in list(sys.modules.keys()):
            if key.startswith("_mock_god_bot_"):
                del sys.modules[key]

    def test_run_all_returns_dict(self):
        from bots.god_bot.god_bot import GodBot

        reg = self._make_registry_with_mocks([("bot_a", 100, 2)])
        god = GodBot(registry=reg)
        result = god.run_all()
        assert isinstance(result, dict)

    def test_run_all_aggregates_revenue(self):
        from bots.god_bot.god_bot import GodBot

        reg = self._make_registry_with_mocks([
            ("bot_a", 500, 5),
            ("bot_b", 300, 3),
        ])
        god = GodBot(registry=reg)
        result = god.run_all()
        assert result["total_revenue"] == 800

    def test_run_all_aggregates_leads(self):
        from bots.god_bot.god_bot import GodBot

        reg = self._make_registry_with_mocks([
            ("bot_a", 500, 5),
            ("bot_b", 300, 3),
        ])
        god = GodBot(registry=reg)
        result = god.run_all()
        assert result["total_leads"] == 8

    def test_run_all_bots_run_count(self):
        from bots.god_bot.god_bot import GodBot

        reg = self._make_registry_with_mocks([
            ("bot_a", 100, 1),
            ("bot_b", 200, 2),
            ("bot_c", 300, 3),
        ])
        god = GodBot(registry=reg)
        result = god.run_all()
        assert result["bots_run"] == 3

    def test_run_all_failed_bots_captured(self):
        from bots.god_bot.god_bot import GodBot

        registry = [("nonexistent_module_xyz_123", "bad_bot")]
        god = GodBot(registry=registry)
        result = god.run_all()
        assert "bad_bot" in result["failed_bots"]

    def test_run_all_results_list_length(self):
        from bots.god_bot.god_bot import GodBot

        reg = self._make_registry_with_mocks([("bot_x", 100, 5)])
        god = GodBot(registry=reg)
        result = god.run_all()
        assert len(result["results"]) == 1

    def test_run_all_result_contains_bot_name(self):
        from bots.god_bot.god_bot import GodBot

        reg = self._make_registry_with_mocks([("my_bot", 100, 5)])
        god = GodBot(registry=reg)
        result = god.run_all()
        assert result["results"][0]["bot"] == "my_bot"


class TestGodBotSaveMetrics:
    def test_save_metrics_stores_entry(self):
        import bots.god_bot.god_bot as gm

        original = list(gm._metrics_store)
        gm.save_metrics({"bot": "test", "revenue": 100})
        assert len(gm._metrics_store) == len(original) + 1
        gm._metrics_store[:] = original  # restore

    def test_save_metrics_has_timestamp(self):
        import bots.god_bot.god_bot as gm

        original = list(gm._metrics_store)
        gm.save_metrics({"bot": "test", "revenue": 200})
        entry = gm._metrics_store[-1]
        assert "saved_at" in entry
        gm._metrics_store[:] = original  # restore

    def test_get_metrics_returns_list(self):
        from bots.god_bot.god_bot import get_metrics

        assert isinstance(get_metrics(), list)


class TestGodBotModuleLevelRun:
    def test_module_run_returns_dict(self):
        # Patch all four bots so they don't need real imports during the run
        mocks = {
            "gov_bot": _make_mock_bot_module("gov_bot", 500, 10),
            "real_estate_bot": _make_mock_bot_module("re_bot", 2000, 5),
            "side_hustle_bot": _make_mock_bot_module("sh_bot", 800, 20),
            "job_bot": _make_mock_bot_module("jb_bot", 600, 15),
        }
        fixed_registry = [(f"_mock_run_{k}", k) for k in mocks]
        for mod_name, bot_name in fixed_registry:
            sys.modules[mod_name] = mocks[bot_name]

        from bots.god_bot.god_bot import GodBot

        god = GodBot(registry=fixed_registry)
        result = god.run_all()
        assert isinstance(result, dict)
        assert result["total_revenue"] == 3900
        assert result["total_leads"] == 50

        for mod_name, _ in fixed_registry:
            del sys.modules[mod_name]


class TestGodBotStart:
    def test_start_respects_max_cycles(self):
        from bots.god_bot.god_bot import GodBot

        mod = _make_mock_bot_module("_mock_start_bot", 100, 2)
        sys.modules["_mock_start_bot"] = mod
        registry = [("_mock_start_bot", "start_bot")]

        god = GodBot(registry=registry)
        # Override sleep to be instant
        with patch("bots.god_bot.god_bot.time.sleep"):
            god.start(interval_minutes=0, max_cycles=2)

        del sys.modules["_mock_start_bot"]
        # If we get here without hanging, max_cycles worked correctly
        assert True
