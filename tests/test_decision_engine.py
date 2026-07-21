"""Tests for bots/ai_brain/tiers.py and bots/ai_brain/decision_engine.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.ai_brain.decision_engine import (
    DecisionEngine,
    DecisionEngineTierError,
    ACTIONS,
    LOW_REVENUE_THRESHOLD,
    HIGH_REVENUE_THRESHOLD,
    BOTTLENECK_ERROR_RATE_THRESHOLD,
)
from bots.ai_brain.tiers import get_bot_tier_info, BOT_FEATURES


# ---------------------------------------------------------------------------
# Tier info
# ---------------------------------------------------------------------------

class TestTierInfo:
    def test_free_tier_info(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert isinstance(info["features"], list)
        assert len(info["features"]) > 0

    def test_pro_tier_info(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_enterprise_tier_info(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"

    def test_all_tiers_have_features(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert len(info["features"]) > 0


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestDecisionEngineInstantiation:
    def test_default_tier_is_free(self):
        engine = DecisionEngine()
        assert engine.tier == Tier.FREE

    def test_pro_tier(self):
        engine = DecisionEngine(tier=Tier.PRO)
        assert engine.tier == Tier.PRO

    def test_enterprise_tier(self):
        engine = DecisionEngine(tier=Tier.ENTERPRISE)
        assert engine.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        engine = DecisionEngine()
        assert engine.config is not None

    def test_decision_history_empty_on_init(self):
        engine = DecisionEngine(tier=Tier.PRO)
        assert engine._decision_history == []


# ---------------------------------------------------------------------------
# analyze_revenue
# ---------------------------------------------------------------------------

class TestAnalyzeRevenue:
    def test_empty_data_signals_scale_leads(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({})
        assert "scale_leads" in result["signals"]

    def test_low_total_revenue_signals_scale_leads(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({"lead_gen": 10.0, "sales": 20.0})
        assert "scale_leads" in result["signals"]

    def test_high_total_revenue_signals_optimize_sales(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({"lead_gen": 600.0, "sales": 800.0})
        assert "optimize_sales" in result["signals"]

    def test_real_estate_low_signals_focus_real_estate(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({"real_estate": 50.0, "sales": 500.0})
        assert "focus_real_estate" in result["signals"]

    def test_total_is_sum(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({"a": 100.0, "b": 200.0, "c": 300.0})
        assert result["total"] == 600.0

    def test_lowest_and_highest_keys_present(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({"a": 10.0, "b": 500.0})
        assert result["lowest"]["source"] == "a"
        assert result["highest"]["source"] == "b"

    def test_single_source(self):
        engine = DecisionEngine()
        result = engine.analyze_revenue({"lead_gen": 50.0})
        assert result["total"] == 50.0
        assert result["lowest"]["source"] == "lead_gen"
        assert result["highest"]["source"] == "lead_gen"


# ---------------------------------------------------------------------------
# analyze_crm_trends
# ---------------------------------------------------------------------------

class TestAnalyzeCRMTrends:
    def test_empty_data_returns_no_signals(self):
        engine = DecisionEngine()
        result = engine.analyze_crm_trends({})
        assert result["top_bot"] is None
        assert result["bottom_bot"] is None
        assert result["signals"] == []

    def test_lead_bot_bottom_signals_scale_leads(self):
        engine = DecisionEngine()
        result = engine.analyze_crm_trends({
            "lead_gen_bot": {"conversion_rate": 0.02},
            "sales_bot": {"conversion_rate": 0.20},
        })
        assert "scale_leads" in result["signals"]
        assert result["bottom_bot"] == "lead_gen_bot"

    def test_sales_bot_bottom_signals_increase_outreach(self):
        engine = DecisionEngine()
        result = engine.analyze_crm_trends({
            "sales_bot": {"conversion_rate": 0.03},
            "lead_gen_bot": {"conversion_rate": 0.15},
        })
        assert "increase_outreach" in result["signals"]

    def test_top_bot_identified(self):
        engine = DecisionEngine()
        result = engine.analyze_crm_trends({
            "lead_gen_bot": {"conversion_rate": 0.05},
            "sales_bot": {"conversion_rate": 0.30},
        })
        assert result["top_bot"] == "sales_bot"

    def test_real_estate_bot_bottom_signals_focus(self):
        engine = DecisionEngine()
        result = engine.analyze_crm_trends({
            "real_estate_bot": {"conversion_rate": 0.01},
            "sales_bot": {"conversion_rate": 0.25},
        })
        assert "focus_real_estate" in result["signals"]


# ---------------------------------------------------------------------------
# detect_bottlenecks
# ---------------------------------------------------------------------------

class TestDetectBottlenecks:
    def test_no_bottlenecks_in_healthy_workflow(self):
        engine = DecisionEngine()
        bottlenecks = engine.detect_bottlenecks({
            "step_a": {"error_rate": 0.01},
            "step_b": {"error_rate": 0.02},
        })
        assert bottlenecks == []

    def test_bottleneck_detected_above_threshold(self):
        engine = DecisionEngine()
        bottlenecks = engine.detect_bottlenecks({
            "sms_outreach": {"error_rate": 0.18},
        })
        assert len(bottlenecks) == 1
        assert bottlenecks[0]["step"] == "sms_outreach"

    def test_high_severity_above_25_pct(self):
        engine = DecisionEngine()
        bottlenecks = engine.detect_bottlenecks({
            "bad_step": {"error_rate": 0.30},
        })
        assert bottlenecks[0]["severity"] == "high"

    def test_medium_severity_between_threshold_and_25_pct(self):
        engine = DecisionEngine()
        bottlenecks = engine.detect_bottlenecks({
            "flaky_step": {"error_rate": 0.12},
        })
        assert bottlenecks[0]["severity"] == "medium"

    def test_multiple_bottlenecks(self):
        engine = DecisionEngine()
        bottlenecks = engine.detect_bottlenecks({
            "step_a": {"error_rate": 0.15},
            "step_b": {"error_rate": 0.28},
            "step_c": {"error_rate": 0.005},
        })
        assert len(bottlenecks) == 2

    def test_empty_workflow_returns_empty_list(self):
        engine = DecisionEngine()
        assert engine.detect_bottlenecks({}) == []


# ---------------------------------------------------------------------------
# make_decision — core logic
# ---------------------------------------------------------------------------

class TestMakeDecision:
    def test_returns_dict_with_required_keys(self):
        engine = DecisionEngine()
        result = engine.make_decision()
        assert "decision" in result
        assert "all_scores" in result
        assert "revenue_analysis" in result
        assert "crm_analysis" in result
        assert "bottlenecks" in result
        assert "timestamp" in result

    def test_decision_has_required_keys(self):
        engine = DecisionEngine()
        decision = engine.make_decision()["decision"]
        assert "key" in decision
        assert "label" in decision
        assert "description" in decision
        assert "score" in decision
        assert "reason" in decision

    def test_decision_key_is_valid_action(self):
        valid_keys = {a["key"] for a in ACTIONS}
        engine = DecisionEngine()
        result = engine.make_decision()
        assert result["decision"]["key"] in valid_keys

    def test_low_revenue_leads_to_scale_leads(self):
        engine = DecisionEngine()
        result = engine.make_decision(revenue_data={"lead_gen": 10.0, "sales": 15.0})
        assert result["decision"]["key"] == "scale_leads"

    def test_bottleneck_prioritised_on_pro_tier(self):
        engine = DecisionEngine(tier=Tier.PRO)
        result = engine.make_decision(
            revenue_data={"lead_gen": 50.0},
            workflow_data={"outreach": {"error_rate": 0.30}},
        )
        assert result["decision"]["key"] == "fix_bottleneck"

    def test_bottleneck_not_prioritised_on_free_tier(self):
        """Free tier does not have bottleneck detection."""
        engine = DecisionEngine(tier=Tier.FREE)
        result = engine.make_decision(
            revenue_data={"lead_gen": 50.0},
            workflow_data={"outreach": {"error_rate": 0.40}},
        )
        # fix_bottleneck should NOT win on FREE because bottleneck detection is disabled
        assert result["decision"]["key"] != "fix_bottleneck"

    def test_high_revenue_with_crm_on_pro_tier(self):
        engine = DecisionEngine(tier=Tier.PRO)
        result = engine.make_decision(
            revenue_data={"lead_gen": 800.0, "sales": 1200.0},
            crm_data={
                "lead_gen_bot": {"conversion_rate": 0.05},
                "sales_bot": {"conversion_rate": 0.30},
            },
        )
        key = result["decision"]["key"]
        assert key in ("optimize_sales", "build_new_bot", "scale_leads")

    def test_all_scores_sorted_descending(self):
        engine = DecisionEngine()
        result = engine.make_decision()
        scores = [s["score"] for s in result["all_scores"]]
        assert scores == sorted(scores, reverse=True)

    def test_decision_recorded_in_history(self):
        engine = DecisionEngine(tier=Tier.PRO)
        engine.make_decision()
        assert len(engine._decision_history) == 1

    def test_multiple_decisions_accumulate(self):
        engine = DecisionEngine(tier=Tier.PRO)
        engine.make_decision()
        engine.make_decision()
        engine.make_decision()
        assert len(engine._decision_history) == 3

    def test_result_is_deterministic_for_same_inputs(self):
        """Same inputs must produce the same decision (no random fallback)."""
        engine = DecisionEngine(tier=Tier.PRO)
        data = {"lead_gen": 50.0, "sales": 100.0}
        r1 = engine.make_decision(revenue_data=data)
        r2 = engine.make_decision(revenue_data=data)
        assert r1["decision"]["key"] == r2["decision"]["key"]


# ---------------------------------------------------------------------------
# Decision history (PRO/ENTERPRISE only)
# ---------------------------------------------------------------------------

class TestDecisionHistory:
    def test_free_tier_raises_error(self):
        engine = DecisionEngine(tier=Tier.FREE)
        with pytest.raises(DecisionEngineTierError):
            engine.get_decision_history()

    def test_pro_tier_returns_list(self):
        engine = DecisionEngine(tier=Tier.PRO)
        engine.make_decision()
        history = engine.get_decision_history()
        assert isinstance(history, list)
        assert len(history) == 1

    def test_enterprise_tier_returns_list(self):
        engine = DecisionEngine(tier=Tier.ENTERPRISE)
        engine.make_decision()
        history = engine.get_decision_history()
        assert len(history) == 1


# ---------------------------------------------------------------------------
# run() method
# ---------------------------------------------------------------------------

class TestRunMethod:
    def test_run_returns_string(self):
        engine = DecisionEngine()
        result = engine.run()
        assert isinstance(result, str)

    def test_run_contains_decision_prefix(self):
        engine = DecisionEngine()
        result = engine.run()
        assert "Decision:" in result

    def test_run_works_on_all_tiers(self):
        for tier in Tier:
            engine = DecisionEngine(tier=tier)
            result = engine.run()
            assert isinstance(result, str)
