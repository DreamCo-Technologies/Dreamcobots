"""
Tests for framework/retraining_optimizer.py and scripts/integration_lookup.py

Covers:
  1. RetrainingOptimizer – basic drift detection
  2. RetrainingOptimizer – method selection at each severity band
  3. RetrainingOptimizer – drift_summary helper
  4. RetrainingOptimizer – constructor validation
  5. integration_lookup – search_registry relevance
  6. integration_lookup – save_integration_results persistence
  7. integration_lookup – fetch_integration_opportunities (offline)
"""

import json
import os
import sys
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Retraining Optimizer imports
# ---------------------------------------------------------------------------
from framework.retraining_optimizer import (
    RetrainingOptimizer,
    STRATEGY_FULL_RETRAIN,
    STRATEGY_FINE_TUNE,
    STRATEGY_INCREMENTAL,
    STRATEGY_NO_RETRAIN,
)

# ---------------------------------------------------------------------------
# Integration Lookup imports
# ---------------------------------------------------------------------------
from scripts.integration_lookup import (
    search_registry,
    save_integration_results,
    fetch_integration_opportunities,
    _REGISTRY,
)


# ===========================================================================
# RetrainingOptimizer tests
# ===========================================================================

class TestRetrainingOptimizerShouldRetrain:
    def setup_method(self):
        self.opt = RetrainingOptimizer(threshold=0.05)

    def test_no_retrain_when_accuracy_improved(self):
        assert self.opt.should_retrain(0.84, 0.92) is False

    def test_no_retrain_when_drop_below_threshold(self):
        # 0.03 drop < 0.05 threshold
        assert self.opt.should_retrain(0.92, 0.89) is False

    def test_retrain_when_drop_equals_threshold(self):
        # 0.05 drop == threshold
        assert self.opt.should_retrain(0.92, 0.87) is True

    def test_retrain_when_drop_above_threshold(self):
        # 0.08 drop > 0.05 threshold
        assert self.opt.should_retrain(0.92, 0.84) is True


class TestRetrainingOptimizerSelectMethod:
    def setup_method(self):
        self.opt = RetrainingOptimizer(threshold=0.05, critical_threshold=0.15)

    def test_no_retrain_below_threshold(self):
        assert self.opt.select_retraining_method(0.92, 0.90) == STRATEGY_NO_RETRAIN

    def test_incremental_update_lower_band(self):
        # drop=0.06, mid=0.075, so 0.05 <= 0.06 < 0.075 => incremental
        assert self.opt.select_retraining_method(0.92, 0.86) == STRATEGY_INCREMENTAL

    def test_fine_tune_upper_band(self):
        # drop=0.08, mid=0.075, critical=0.15, so 0.075 <= 0.08 < 0.15 => fine_tune
        assert self.opt.select_retraining_method(0.92, 0.84) == STRATEGY_FINE_TUNE

    def test_full_retrain_at_critical(self):
        # drop=0.17 >= 0.15 => full_retrain
        assert self.opt.select_retraining_method(0.92, 0.75) == STRATEGY_FULL_RETRAIN


class TestRetrainingOptimizerDriftSummary:
    def setup_method(self):
        self.opt = RetrainingOptimizer(threshold=0.05)

    def test_summary_keys(self):
        summary = self.opt.drift_summary(0.92, 0.84, label="revenue_bot")
        assert "baseline_accuracy" in summary
        assert "current_accuracy" in summary
        assert "accuracy_drop" in summary
        assert "drift_detected" in summary
        assert "recommended_method" in summary
        assert summary["label"] == "revenue_bot"

    def test_summary_values(self):
        summary = self.opt.drift_summary(0.92, 0.84)
        assert summary["baseline_accuracy"] == 0.92
        assert summary["current_accuracy"] == 0.84
        assert abs(summary["accuracy_drop"] - 0.08) < 1e-9
        assert summary["drift_detected"] is True


class TestRetrainingOptimizerValidation:
    def test_invalid_threshold_zero(self):
        with pytest.raises(ValueError):
            RetrainingOptimizer(threshold=0.0)

    def test_invalid_threshold_above_one(self):
        with pytest.raises(ValueError):
            RetrainingOptimizer(threshold=1.1)

    def test_critical_not_greater_than_threshold(self):
        with pytest.raises(ValueError):
            RetrainingOptimizer(threshold=0.10, critical_threshold=0.05)


# ===========================================================================
# Integration Lookup tests
# ===========================================================================

class TestSearchRegistry:
    def test_returns_all_when_empty_query(self):
        results = search_registry("")
        assert len(results) == len(_REGISTRY)

    def test_automation_query_returns_matches(self):
        results = search_registry("automation")
        names = [r["name"] for r in results]
        assert any("Zapier" in n or "GitHub Actions" in n for n in names)

    def test_unknown_query_returns_empty(self):
        results = search_registry("zzz_definitely_not_a_match_xyz_999")
        assert results == []

    def test_results_sorted_by_relevance(self):
        results = search_registry("automation workflow")
        assert len(results) >= 1
        # The most-tagged entry should come first
        assert results[0]["id"] in {"zapier", "make", "github_actions"}

    def test_payments_query(self):
        results = search_registry("payments billing")
        assert any(r["id"] == "stripe" for r in results)


class TestSaveIntegrationResults:
    def test_creates_file_if_missing(self, tmp_path):
        path = str(tmp_path / "lookup.json")
        save_integration_results("test query", [{"id": "test"}], data_path=path)
        assert os.path.exists(path)
        with open(path) as fh:
            data = json.load(fh)
        assert "test query" in data["queries"]
        assert data["total_queries"] == 1

    def test_appends_to_existing_file(self, tmp_path):
        path = str(tmp_path / "lookup.json")
        save_integration_results("query1", [{"id": "a"}], data_path=path)
        save_integration_results("query2", [{"id": "b"}], data_path=path)
        with open(path) as fh:
            data = json.load(fh)
        assert data["total_queries"] == 2
        assert "query1" in data["queries"]
        assert "query2" in data["queries"]

    def test_result_count_stored_correctly(self, tmp_path):
        path = str(tmp_path / "lookup.json")
        save_integration_results("q", [{"id": "x"}, {"id": "y"}], data_path=path)
        with open(path) as fh:
            data = json.load(fh)
        assert data["queries"]["q"]["result_count"] == 2


class TestFetchIntegrationOpportunities:
    def test_returns_list(self):
        results = fetch_integration_opportunities("automation")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_fallback_returns_full_registry_on_no_match(self):
        results = fetch_integration_opportunities("zzz_no_match_xyz")
        assert len(results) == len(_REGISTRY)

    def test_all_results_have_required_keys(self):
        results = fetch_integration_opportunities("payments")
        for r in results:
            assert "id" in r
            assert "name" in r
            assert "category" in r
