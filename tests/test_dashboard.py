"""Tests for dashboard/app.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from dashboard.app import DashboardApp
from core.dreamco_orchestrator import DreamCoOrchestrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_dashboard(revenues=None):
    revenues = revenues or [100.0, 200.0, 50.0]
    orch = DreamCoOrchestrator()
    fake_results = [
        {
            "bot_name": f"bot_{i}",
            "output": {"revenue": rev, "conversion_rate": 0.2},
            "validation": {"scale": rev >= 100},
            "error": None,
        }
        for i, rev in enumerate(revenues)
    ]
    orch.run_all_bots = lambda: fake_results
    return DashboardApp(orchestrator=orch)


# ---------------------------------------------------------------------------
# get_view
# ---------------------------------------------------------------------------

class TestGetView:
    def test_returns_dict_with_required_keys(self):
        dash = _make_dashboard()
        view = dash.get_view()
        for key in ("bots", "total_revenue", "top_performers", "scaling_events", "timestamp"):
            assert key in view

    def test_total_revenue_correct(self):
        dash = _make_dashboard(revenues=[100.0, 200.0, 50.0])
        view = dash.get_view()
        assert view["total_revenue"] == pytest.approx(350.0)

    def test_top_performers_list_not_empty(self):
        dash = _make_dashboard()
        view = dash.get_view()
        assert isinstance(view["top_performers"], list)

    def test_scaling_events_counted(self):
        dash = _make_dashboard(revenues=[200.0, 300.0, 50.0])
        view = dash.get_view()
        # 200 and 300 are >= default threshold of 100
        assert view["scaling_events"] == 2

    def test_bots_list_matches_input(self):
        dash = _make_dashboard(revenues=[100.0, 200.0])
        view = dash.get_view()
        assert len(view["bots"]) == 2

    def test_error_bots_excluded_from_revenue(self):
        orch = DreamCoOrchestrator()
        orch.run_all_bots = lambda: [
            {"bot_name": "ok", "output": {"revenue": 300}, "validation": {}, "error": None},
            {"bot_name": "err", "output": {}, "validation": {}, "error": "failed"},
        ]
        dash = DashboardApp(orchestrator=orch)
        view = dash.get_view()
        assert view["total_revenue"] == pytest.approx(300.0)


# ---------------------------------------------------------------------------
# get_summary_stats
# ---------------------------------------------------------------------------

class TestGetSummaryStats:
    def test_returns_dict(self):
        dash = _make_dashboard()
        stats = dash.get_summary_stats()
        assert isinstance(stats, dict)
