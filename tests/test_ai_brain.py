"""
Tests for bots/ai_brain/ — DecisionEngine, StateManager, MetricsTracker,
and AIBrain orchestrator.
"""

import sys
import os
import json
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.ai_brain.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FEATURE_DECISION_ENGINE,
    FEATURE_PERSISTENT_MEMORY,
    FEATURE_REAL_METRICS,
    FEATURE_AUTO_SCALE,
    FEATURE_RECOVERY_BOT,
    FEATURE_FULL_AUTONOMY,
)
from bots.ai_brain.decision_engine import (
    DecisionEngine,
    DECISION_SCALE_LEADS,
    DECISION_INCREASE_OUTREACH,
    DECISION_SCALE_SYSTEM,
    DECISION_OPTIMIZE,
    DECISION_CREATE_SCALING_BOT,
    DECISION_CREATE_RECOVERY_BOT,
    LEADS_THRESHOLD_LOW,
    REVENUE_THRESHOLD_LOW,
    REVENUE_THRESHOLD_HIGH,
)
from bots.ai_brain.state_manager import StateManager, save_state, load_state
from bots.ai_brain.metrics_tracker import MetricsTracker
from bots.ai_brain.ai_brain import AIBrain, AIBrainError, AIBrainTierError


# ---------------------------------------------------------------------------
# Framework compliance
# ---------------------------------------------------------------------------

class TestFrameworkCompliance:
    def test_decision_engine_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "ai_brain", "decision_engine.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_state_manager_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "ai_brain", "state_manager.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_metrics_tracker_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "ai_brain", "metrics_tracker.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_ai_brain_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "ai_brain", "ai_brain.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------

class TestAIBrainTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_has_decision_engine(self):
        config = get_tier_config(Tier.FREE)
        assert config.has_feature(FEATURE_DECISION_ENGINE)

    def test_free_tier_no_persistent_memory(self):
        config = get_tier_config(Tier.FREE)
        assert not config.has_feature(FEATURE_PERSISTENT_MEMORY)

    def test_pro_tier_has_persistent_memory(self):
        config = get_tier_config(Tier.PRO)
        assert config.has_feature(FEATURE_PERSISTENT_MEMORY)

    def test_pro_tier_has_real_metrics(self):
        config = get_tier_config(Tier.PRO)
        assert config.has_feature(FEATURE_REAL_METRICS)

    def test_enterprise_has_full_autonomy(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.has_feature(FEATURE_FULL_AUTONOMY)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_enterprise_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ---------------------------------------------------------------------------
# Decision Engine
# ---------------------------------------------------------------------------

class TestDecisionEngine:
    def test_low_leads_returns_scale_leads(self):
        engine = DecisionEngine()
        result = engine.run({"revenue": 500, "leads": 5})
        assert result == DECISION_SCALE_LEADS

    def test_low_revenue_returns_increase_outreach(self):
        engine = DecisionEngine()
        result = engine.run({"revenue": 100, "leads": 25})
        assert result == DECISION_INCREASE_OUTREACH

    def test_high_revenue_returns_scale_system(self):
        engine = DecisionEngine()
        result = engine.run({"revenue": 2000, "leads": 50})
        assert result == DECISION_SCALE_SYSTEM

    def test_medium_returns_optimize(self):
        engine = DecisionEngine()
        result = engine.run({"revenue": 500, "leads": 30})
        assert result == DECISION_OPTIMIZE

    def test_auto_generate_bots_high_revenue(self):
        engine = DecisionEngine(auto_generate_bots=True)
        result = engine.run({"revenue": 2000, "leads": 50})
        assert result == DECISION_CREATE_SCALING_BOT

    def test_zero_leads_returns_scale_leads(self):
        engine = DecisionEngine()
        result = engine.run({"revenue": 0, "leads": 0})
        assert result == DECISION_SCALE_LEADS

    def test_decision_log_records_entry(self):
        engine = DecisionEngine()
        engine.run({"revenue": 500, "leads": 30})
        log = engine.get_decision_log()
        assert len(log) == 1
        assert "decision" in log[0]
        assert "revenue" in log[0]
        assert "leads" in log[0]

    def test_multiple_decisions_logged(self):
        engine = DecisionEngine()
        engine.run({"revenue": 0, "leads": 0})
        engine.run({"revenue": 500, "leads": 30})
        engine.run({"revenue": 2000, "leads": 100})
        assert len(engine.get_decision_log()) == 3

    def test_get_latest_decision(self):
        engine = DecisionEngine()
        engine.run({"revenue": 0, "leads": 0})
        engine.run({"revenue": 500, "leads": 30})
        latest = engine.get_latest_decision()
        assert latest["decision"] == DECISION_OPTIMIZE

    def test_get_latest_decision_empty(self):
        engine = DecisionEngine()
        assert engine.get_latest_decision() is None

    def test_decision_summary(self):
        engine = DecisionEngine()
        engine.run({"revenue": 0, "leads": 0})
        engine.run({"revenue": 500, "leads": 30})
        summary = engine.get_decision_summary()
        assert summary["total"] == 2
        assert "decisions" in summary

    def test_evaluate_for_bot_creation_high_revenue(self):
        engine = DecisionEngine()
        bot_type = engine.evaluate_for_bot_creation(2000.0)
        assert bot_type == "scaling_bot"

    def test_evaluate_for_bot_creation_low_revenue(self):
        engine = DecisionEngine()
        bot_type = engine.evaluate_for_bot_creation(50.0)
        assert bot_type == "recovery_bot"

    def test_evaluate_for_bot_creation_mid_revenue(self):
        engine = DecisionEngine()
        bot_type = engine.evaluate_for_bot_creation(500.0)
        assert bot_type is None

    def test_leads_threshold_constant(self):
        assert LEADS_THRESHOLD_LOW == 20

    def test_revenue_threshold_low_constant(self):
        assert REVENUE_THRESHOLD_LOW == 200.0

    def test_revenue_threshold_high_constant(self):
        assert REVENUE_THRESHOLD_HIGH == 1000.0


# ---------------------------------------------------------------------------
# State Manager
# ---------------------------------------------------------------------------

class TestStateManager:
    def _tmp_path(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        return path

    def test_save_and_load_state_functions(self):
        path = self._tmp_path()
        data = {"revenue": 500.0, "leads": 25}
        save_state(data, path)
        loaded = load_state(path)
        assert loaded["revenue"] == 500.0
        assert loaded["leads"] == 25

    def test_load_state_missing_file(self):
        loaded = load_state("/nonexistent/path/state.json")
        assert loaded == {}

    def test_state_manager_init(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        assert sm.get("total_revenue") == 0.0
        assert sm.get("total_leads") == 0

    def test_state_manager_get_set(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        sm.set("total_revenue", 1000.0)
        assert sm.get("total_revenue") == 1000.0

    def test_state_manager_add_revenue(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        total = sm.add_revenue(500.0)
        assert total == 500.0
        total = sm.add_revenue(250.0)
        assert total == 750.0

    def test_state_manager_add_leads(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        total = sm.add_leads(10)
        assert total == 10
        total = sm.add_leads(5)
        assert total == 15

    def test_state_manager_increment_bot_count(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        assert sm.increment_bot_count() == 1
        assert sm.increment_bot_count() == 2

    def test_state_manager_record_decision(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        sm.record_decision("scale_leads")
        sm.record_decision("optimize")
        decisions = sm.get("decisions")
        assert len(decisions) == 2
        assert decisions[0]["decision"] == "scale_leads"

    def test_state_persists_to_file(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        sm.set("total_revenue", 999.99)
        # Load fresh
        loaded = load_state(path)
        assert loaded["total_revenue"] == 999.99

    def test_state_manager_auto_load(self):
        path = self._tmp_path()
        save_state({"total_revenue": 777.0, "total_leads": 42}, path)
        sm = StateManager(state_path=path, auto_load=True)
        assert sm.get("total_revenue") == 777.0
        assert sm.get("total_leads") == 42

    def test_state_manager_reset(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        sm.set("total_revenue", 5000.0)
        sm.reset()
        assert sm.get("total_revenue") == 0.0

    def test_get_full_state(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        sm.set("total_revenue", 100.0)
        state = sm.get_full_state()
        assert isinstance(state, dict)
        assert state["total_revenue"] == 100.0

    def test_update_multiple_keys(self):
        path = self._tmp_path()
        sm = StateManager(state_path=path, auto_load=False)
        sm.update({"total_revenue": 200.0, "total_leads": 50})
        assert sm.get("total_revenue") == 200.0
        assert sm.get("total_leads") == 50


# ---------------------------------------------------------------------------
# Metrics Tracker
# ---------------------------------------------------------------------------

class TestMetricsTracker:
    def _make_leads_file(self, leads: list, suffix=".json") -> str:
        """Create a temporary leads JSON file."""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
        json.dump(leads, f)
        f.close()
        return f.name

    def _make_deals_file(self, deals: list) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(deals, f)
        f.close()
        return f.name

    def test_count_leads_from_json_array(self):
        leads = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        path = self._make_leads_file(leads)
        tracker = MetricsTracker(leads_path=path)
        assert tracker.count_leads() == 3

    def test_count_leads_empty_file(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        f.write("")
        f.close()
        tracker = MetricsTracker(leads_path=f.name)
        assert tracker.count_leads() == 0

    def test_count_leads_missing_file(self):
        tracker = MetricsTracker(leads_path="/nonexistent/leads.json")
        assert tracker.count_leads() == 0

    def test_track_revenue_from_deals(self):
        deals = [{"id": 1}, {"id": 2}, {"id": 3}]
        path = self._make_deals_file(deals)
        tracker = MetricsTracker(deals_path=path, revenue_per_deal=100.0)
        assert tracker.track_revenue() == 300.0

    def test_track_revenue_no_deals(self):
        tracker = MetricsTracker(deals_path="/nonexistent/deals.json")
        assert tracker.track_revenue() == 0.0

    def test_track_revenue_empty_deals(self):
        deals = []
        path = self._make_deals_file(deals)
        tracker = MetricsTracker(deals_path=path)
        assert tracker.track_revenue() == 0.0

    def test_get_metrics(self):
        leads = [{"name": "A"}, {"name": "B"}]
        deals = [{"id": 1}]
        leads_path = self._make_leads_file(leads)
        deals_path = self._make_deals_file(deals)
        tracker = MetricsTracker(
            leads_path=leads_path,
            deals_path=deals_path,
            revenue_per_deal=100.0,
        )
        metrics = tracker.get_metrics()
        assert metrics["leads"] == 2
        assert metrics["revenue"] == 100.0
        assert "timestamp" in metrics

    def test_get_metrics_history(self):
        tracker = MetricsTracker()
        tracker.get_metrics()
        tracker.get_metrics()
        history = tracker.get_metrics_history()
        assert len(history) == 2

    def test_count_deals_closed(self):
        deals = [{"id": 1}, {"id": 2}]
        path = self._make_deals_file(deals)
        tracker = MetricsTracker(deals_path=path, revenue_per_deal=100.0)
        assert tracker.count_deals_closed() == 2


# ---------------------------------------------------------------------------
# AI Brain
# ---------------------------------------------------------------------------

class TestAIBrain:
    def test_free_tier_can_think(self):
        brain = AIBrain(tier=Tier.FREE)
        result = brain.think(override_metrics={"revenue": 500, "leads": 30})
        assert result["decision"] == DECISION_OPTIMIZE

    def test_think_with_low_leads(self):
        brain = AIBrain(tier=Tier.FREE)
        result = brain.think(override_metrics={"revenue": 500, "leads": 5})
        assert result["decision"] == DECISION_SCALE_LEADS

    def test_think_with_low_revenue(self):
        brain = AIBrain(tier=Tier.FREE)
        result = brain.think(override_metrics={"revenue": 100, "leads": 30})
        assert result["decision"] == DECISION_INCREASE_OUTREACH

    def test_think_with_high_revenue(self):
        brain = AIBrain(tier=Tier.FREE)
        result = brain.think(override_metrics={"revenue": 2000, "leads": 50})
        assert result["decision"] == DECISION_SCALE_SYSTEM

    def test_think_result_has_required_fields(self):
        brain = AIBrain(tier=Tier.FREE)
        result = brain.think(override_metrics={"revenue": 500, "leads": 30})
        assert "decision" in result
        assert "metrics" in result
        assert "tier" in result

    def test_pro_tier_has_state(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        brain = AIBrain(tier=Tier.PRO, state_path=path)
        brain.think(override_metrics={"revenue": 500, "leads": 30})
        state = brain.get_state()
        assert isinstance(state, dict)
        assert len(state) > 0

    def test_free_tier_empty_state(self):
        brain = AIBrain(tier=Tier.FREE)
        state = brain.get_state()
        assert state == {}

    def test_get_decision_log(self):
        brain = AIBrain(tier=Tier.FREE)
        brain.think(override_metrics={"revenue": 0, "leads": 0})
        brain.think(override_metrics={"revenue": 500, "leads": 30})
        log = brain.get_decision_log()
        assert len(log) == 2

    def test_run_returns_string(self):
        brain = AIBrain(tier=Tier.FREE)
        # Override to avoid file reads
        brain._metrics_tracker = None
        result = brain.run()
        assert isinstance(result, str)
        assert "AI Brain" in result

    def test_process_payload(self):
        brain = AIBrain(tier=Tier.FREE)
        result = brain.process({"metrics": {"revenue": 500, "leads": 30}})
        assert result["decision"] == DECISION_OPTIMIZE

    def test_enterprise_bot_creation_recommendation(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        brain = AIBrain(tier=Tier.ENTERPRISE, state_path=path)
        result = brain.think(override_metrics={"revenue": 2000, "leads": 50})
        assert result["bot_to_create"] == "scaling_bot"

    def test_enterprise_recovery_bot_recommendation(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        brain = AIBrain(tier=Tier.ENTERPRISE, state_path=path)
        result = brain.think(override_metrics={"revenue": 50, "leads": 25})
        assert result["bot_to_create"] == "recovery_bot"

    def test_tier_error_on_missing_feature(self):
        brain = AIBrain(tier=Tier.FREE)
        orig_config = brain._config

        class _NoFeatures:
            name = orig_config.name
            price_usd_monthly = orig_config.price_usd_monthly

            def has_feature(self, f):
                return False

        brain._config = _NoFeatures()
        with pytest.raises(AIBrainTierError):
            brain.think()
