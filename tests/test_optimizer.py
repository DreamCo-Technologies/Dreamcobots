"""Tests for core/optimizer.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from core.optimizer import Optimizer, OptimizationResult


# ---------------------------------------------------------------------------
# improve()
# ---------------------------------------------------------------------------

class TestImprove:
    def setup_method(self):
        self.opt = Optimizer(
            low_conversion_threshold=0.05,
            scale_revenue_threshold=1_000.0,
        )

    def test_change_strategy_low_conversion(self):
        result = self.opt.improve({"revenue": 10, "conversion_rate": 0.01})
        assert result == "Change strategy"

    def test_scale_aggressively_high_revenue(self):
        result = self.opt.improve({"revenue": 1_500, "conversion_rate": 0.3})
        assert result == "Scale aggressively"

    def test_maintain_middle_case(self):
        result = self.opt.improve({"revenue": 200, "conversion_rate": 0.2})
        assert result == "Maintain"

    def test_missing_keys_treated_as_zero(self):
        result = self.opt.improve({})
        assert result == "Change strategy"

    def test_zero_conversion_is_change_strategy(self):
        result = self.opt.improve({"revenue": 500, "conversion_rate": 0.0})
        assert result == "Change strategy"


# ---------------------------------------------------------------------------
# evaluate()
# ---------------------------------------------------------------------------

class TestEvaluate:
    def setup_method(self):
        self.opt = Optimizer()

    def test_returns_optimization_result(self):
        result = self.opt.evaluate("test_bot", {"revenue": 200, "conversion_rate": 0.2})
        assert isinstance(result, OptimizationResult)

    def test_to_dict_has_required_keys(self):
        result = self.opt.evaluate("test_bot", {"revenue": 200, "conversion_rate": 0.2})
        d = result.to_dict()
        for key in ("bot_name", "recommendation", "revenue", "conversion_rate",
                    "leads_generated", "priority_score", "timestamp"):
            assert key in d

    def test_priority_score_positive_for_high_revenue(self):
        result = self.opt.evaluate("top_bot", {"revenue": 2_000, "conversion_rate": 0.5, "leads_generated": 20})
        assert result.priority_score > 0

    def test_history_appended(self):
        self.opt.evaluate("a", {"revenue": 100})
        self.opt.evaluate("b", {"revenue": 200})
        assert len(self.opt.get_history()) == 2


# ---------------------------------------------------------------------------
# evaluate_all()
# ---------------------------------------------------------------------------

class TestEvaluateAll:
    def test_returns_sorted_by_priority(self):
        opt = Optimizer(scale_revenue_threshold=500.0)
        items = [
            {"bot_name": "low", "output": {"revenue": 10, "conversion_rate": 0.02}},
            {"bot_name": "high", "output": {"revenue": 2_000, "conversion_rate": 0.5}},
            {"bot_name": "mid", "output": {"revenue": 300, "conversion_rate": 0.2}},
        ]
        results = opt.evaluate_all(items)
        assert results[0]["bot_name"] == "high"

    def test_empty_list(self):
        opt = Optimizer()
        assert opt.evaluate_all([]) == []


# ---------------------------------------------------------------------------
# get_top_performers()
# ---------------------------------------------------------------------------

class TestTopPerformers:
    def test_returns_n_results(self):
        opt = Optimizer()
        for i in range(10):
            opt.evaluate(f"bot_{i}", {"revenue": i * 100, "conversion_rate": i * 0.05})
        top = opt.get_top_performers(n=3)
        assert len(top) == 3

    def test_top_performers_ordered_by_priority(self):
        opt = Optimizer(scale_revenue_threshold=500.0)
        opt.evaluate("low", {"revenue": 10, "conversion_rate": 0.01})
        opt.evaluate("high", {"revenue": 5_000, "conversion_rate": 0.8})
        top = opt.get_top_performers(n=1)
        assert top[0]["bot_name"] == "high"


# ---------------------------------------------------------------------------
# OptimizationResult
# ---------------------------------------------------------------------------

class TestOptimizationResult:
    def test_to_dict_rounds_values(self):
        r = OptimizationResult(
            bot_name="x",
            recommendation="Maintain",
            revenue=123.456789,
            conversion_rate=0.123456789,
            leads_generated=5,
            priority_score=0.987654321,
        )
        d = r.to_dict()
        assert d["revenue"] == pytest.approx(123.46, abs=0.01)
        assert d["conversion_rate"] == pytest.approx(0.1235, abs=0.0001)
