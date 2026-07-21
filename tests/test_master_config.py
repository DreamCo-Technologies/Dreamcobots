"""
Tests for config/config_manager.py — MasterConfigManager singleton.
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from config.config_manager import MasterConfigManager, BotPriority


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_singleton():
    """Ensure each test gets a fresh MasterConfigManager instance."""
    MasterConfigManager._reset()
    yield
    MasterConfigManager._reset()


@pytest.fixture
def cfg():
    return MasterConfigManager()


# ---------------------------------------------------------------------------
# Basic loading
# ---------------------------------------------------------------------------


class TestMasterConfigLoads:
    def test_version_present(self, cfg):
        assert cfg.get("version") is not None

    def test_profit_targets_daily(self, cfg):
        daily = cfg.get("profit_targets.daily")
        assert daily == 500.0

    def test_profit_targets_weekly(self, cfg):
        assert cfg.get("profit_targets.weekly") == 3500.0

    def test_profit_targets_monthly(self, cfg):
        assert cfg.get("profit_targets.monthly") == 15000.0

    def test_resource_allocation_budget(self, cfg):
        budget = cfg.get("resource_allocation.max_api_budget_daily")
        assert budget == 200.0

    def test_reinvestment_percentage(self, cfg):
        assert cfg.get("resource_allocation.reinvestment_percentage") == 0.30

    def test_learning_retention_days(self, cfg):
        assert cfg.get("learning.feedback_retention_days") == 90

    def test_learning_retrain_frequency(self, cfg):
        assert cfg.get("learning.retrain_frequency_hours") == 168

    def test_learning_min_samples(self, cfg):
        assert cfg.get("learning.min_samples_to_retrain") == 1000

    def test_model_registry_path(self, cfg):
        assert cfg.get("learning.model_registry_path") == "models/registry"


# ---------------------------------------------------------------------------
# Tier configuration
# ---------------------------------------------------------------------------


class TestTiers:
    def test_free_tier_requests(self, cfg):
        assert cfg.get("tiers.free.requests_per_month") == 500

    def test_free_tier_concurrent_bots(self, cfg):
        assert cfg.get("tiers.free.concurrent_bots") == 2

    def test_pro_tier_price(self, cfg):
        assert cfg.get("tiers.pro.price_monthly") == 49.0

    def test_pro_tier_concurrent_bots(self, cfg):
        assert cfg.get("tiers.pro.concurrent_bots") == 10

    def test_enterprise_tier_price(self, cfg):
        assert cfg.get("tiers.enterprise.price_monthly") == 299.0

    def test_enterprise_tier_concurrent_bots(self, cfg):
        assert cfg.get("tiers.enterprise.concurrent_bots") == 50

    def test_free_tier_models_is_list(self, cfg):
        models = cfg.get("tiers.free.models")
        assert isinstance(models, list)
        assert "gpt-3.5-turbo" in models


# ---------------------------------------------------------------------------
# Bot priorities
# ---------------------------------------------------------------------------


class TestBotPriorities:
    def test_trading_priority(self, cfg):
        assert cfg.get("bot_priorities.trading") == 1

    def test_content_generation_priority(self, cfg):
        assert cfg.get("bot_priorities.content_generation") == 2

    def test_job_application_priority(self, cfg):
        assert cfg.get("bot_priorities.job_application") == 3

    def test_government_contracts_priority(self, cfg):
        assert cfg.get("bot_priorities.government_contracts") == 4


# ---------------------------------------------------------------------------
# get() edge cases
# ---------------------------------------------------------------------------


class TestGetMethod:
    def test_missing_key_returns_default(self, cfg):
        assert cfg.get("does.not.exist") is None

    def test_missing_key_returns_custom_default(self, cfg):
        assert cfg.get("does.not.exist", "fallback") == "fallback"

    def test_nested_key_resolution(self, cfg):
        assert cfg.get("tiers.pro.price_monthly") == 49.0

    def test_all_returns_dict(self, cfg):
        result = cfg.all()
        assert isinstance(result, dict)
        assert "tiers" in result


# ---------------------------------------------------------------------------
# Singleton behaviour
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_same_instance_returned(self):
        a = MasterConfigManager()
        b = MasterConfigManager()
        assert a is b

    def test_reset_creates_new_instance(self):
        a = MasterConfigManager()
        MasterConfigManager._reset()
        b = MasterConfigManager()
        assert a is not b


# ---------------------------------------------------------------------------
# Env-var expansion
# ---------------------------------------------------------------------------


class TestEnvVarExpansion:
    def test_env_var_with_default(self, monkeypatch):
        monkeypatch.delenv("DREAMCO_ENV", raising=False)
        MasterConfigManager._reset()
        cfg = MasterConfigManager()
        # master_config.yaml sets environment: "${DREAMCO_ENV:-production}"
        assert cfg.get("environment") == "production"

    def test_env_var_overridden(self, monkeypatch):
        monkeypatch.setenv("DREAMCO_ENV", "staging")
        MasterConfigManager._reset()
        cfg = MasterConfigManager()
        assert cfg.get("environment") == "staging"


# ---------------------------------------------------------------------------
# BotPriority dataclass
# ---------------------------------------------------------------------------


class TestBotPriority:
    def test_instantiates(self):
        bp = BotPriority(bot_name="trading", priority=1, max_concurrent=5, budget_allocation_pct=0.25)
        assert bp.bot_name == "trading"
        assert bp.priority == 1
        assert bp.max_concurrent == 5
        assert bp.budget_allocation_pct == 0.25
