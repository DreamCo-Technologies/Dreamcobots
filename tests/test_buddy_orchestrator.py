"""
Tests for bots/buddy_orchestrator/

Covers:
  • DataScrapeLifecycle — deadline tracking, record_scrape, summary
  • BuddyOrchestrator   — registration, run_bot, aggregation, revenue, GitHub
                          Actions status, go-live, status snapshot
"""

from __future__ import annotations

import sys
import os
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.buddy_orchestrator.data_scrape_lifecycle import (
    DataScrapeLifecycle,
    SCRAPE_DEADLINE,
    ScrapeStatus,
)
from bots.buddy_orchestrator.buddy_orchestrator import (
    BuddyOrchestrator,
    BotSpec,
    OrchestratorError,
)


# ===========================================================================
# DataScrapeLifecycle
# ===========================================================================


class TestDataScrapeLifecycleDefaultDeadline:
    def test_default_deadline_is_june_22_2026(self):
        lc = DataScrapeLifecycle()
        assert lc.deadline == date(2026, 6, 22)

    def test_deadline_iso_format(self):
        lc = DataScrapeLifecycle()
        assert lc.deadline_iso() == "2026-06-22"

    def test_module_constant_matches(self):
        assert SCRAPE_DEADLINE == date(2026, 6, 22)


class TestDataScrapeLifecycleScrapingActive:
    def test_active_when_deadline_is_today(self):
        today = date.today()
        lc = DataScrapeLifecycle(deadline=today)
        assert lc.scraping_active() is True

    def test_active_when_deadline_is_future(self):
        future = date(2099, 12, 31)
        lc = DataScrapeLifecycle(deadline=future)
        assert lc.scraping_active() is True

    def test_inactive_when_deadline_passed(self):
        past = date(2000, 1, 1)
        lc = DataScrapeLifecycle(deadline=past)
        assert lc.scraping_active() is False


class TestDataScrapeLifecycleDaysRemaining:
    def test_days_remaining_future_deadline(self):
        future = date(2099, 12, 31)
        lc = DataScrapeLifecycle(deadline=future)
        assert lc.days_remaining() > 0

    def test_days_remaining_zero_when_passed(self):
        past = date(2000, 1, 1)
        lc = DataScrapeLifecycle(deadline=past)
        assert lc.days_remaining() == 0

    def test_days_remaining_today_is_zero_or_one(self):
        today = date.today()
        lc = DataScrapeLifecycle(deadline=today)
        # today - today = 0 → max(0, 0) = 0
        assert lc.days_remaining() == 0


class TestDataScrapeLifecycleRegisterBot:
    def test_register_creates_record(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        rec = lc.register_bot("test_bot")
        assert rec.bot_id == "test_bot"

    def test_register_idempotent(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        r1 = lc.register_bot("bot_a")
        r2 = lc.register_bot("bot_a")
        assert r1 is r2

    def test_initial_datasets_zero(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        rec = lc.register_bot("fresh_bot")
        assert rec.datasets_collected == 0


class TestDataScrapeLifecycleRecordScrape:
    def test_record_increments_datasets(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        lc.register_bot("bot_x")
        lc.record_scrape("bot_x", datasets=3)
        assert lc._records["bot_x"].datasets_collected == 3

    def test_record_accumulates(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        lc.register_bot("bot_y")
        lc.record_scrape("bot_y", datasets=2)
        lc.record_scrape("bot_y", datasets=5)
        assert lc._records["bot_y"].datasets_collected == 7

    def test_record_returns_status_recorded(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        result = lc.record_scrape("new_bot")
        assert result["status"] == "recorded"

    def test_record_returns_days_remaining(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        result = lc.record_scrape("nb")
        assert result["days_remaining"] > 0

    def test_record_after_deadline_returns_deadline_passed(self):
        lc = DataScrapeLifecycle(deadline=date(2000, 1, 1))
        result = lc.record_scrape("late_bot")
        assert result["status"] == "deadline_passed"

    def test_record_after_deadline_does_not_increment(self):
        lc = DataScrapeLifecycle(deadline=date(2000, 1, 1))
        lc.record_scrape("late_bot", datasets=99)
        # bot was never registered via register_bot
        assert "late_bot" not in lc._records

    def test_record_sets_last_scraped_at(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        result = lc.record_scrape("ts_bot")
        assert result["last_scraped_at"] is not None

    def test_auto_registers_unknown_bot(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        lc.record_scrape("auto_bot")
        assert "auto_bot" in lc._records


class TestDataScrapeLifecycleSummary:
    def test_summary_keys(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        s = lc.summary()
        for key in ("deadline", "scraping_active", "days_remaining", "registered_bots", "total_datasets_collected", "bots"):
            assert key in s

    def test_summary_total_datasets(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        lc.record_scrape("a", datasets=4)
        lc.record_scrape("b", datasets=6)
        s = lc.summary()
        assert s["total_datasets_collected"] == 10

    def test_summary_registered_bots(self):
        lc = DataScrapeLifecycle(deadline=date(2099, 1, 1))
        lc.register_bot("r1")
        lc.register_bot("r2")
        s = lc.summary()
        assert s["registered_bots"] == 2


# ===========================================================================
# BuddyOrchestrator
# ===========================================================================


@pytest.fixture
def orch():
    return BuddyOrchestrator(github_repo="test-owner/test-repo")


class TestBuddyOrchestratorRegistration:
    def test_register_returns_bot_spec(self, orch):
        spec = orch.register_bot("bot_a", tier="PRO")
        assert isinstance(spec, BotSpec)

    def test_register_sets_bot_id(self, orch):
        spec = orch.register_bot("my_bot")
        assert spec.bot_id == "my_bot"

    def test_register_sets_tier(self, orch):
        spec = orch.register_bot("t_bot", tier="ENTERPRISE")
        assert spec.tier == "ENTERPRISE"

    def test_register_sets_price(self, orch):
        spec = orch.register_bot("p_bot", price_usd=29.99)
        assert spec.price_usd == 29.99

    def test_register_idempotent(self, orch):
        orch.register_bot("idem_bot", tier="FREE")
        orch.register_bot("idem_bot", tier="PRO")
        assert orch._catalog["idem_bot"].tier == "PRO"

    def test_get_bot_returns_spec(self, orch):
        orch.register_bot("fetch_bot")
        spec = orch.get_bot("fetch_bot")
        assert spec is not None
        assert spec.bot_id == "fetch_bot"

    def test_get_bot_returns_none_for_unknown(self, orch):
        assert orch.get_bot("nonexistent") is None

    def test_unregister_removes_bot(self, orch):
        orch.register_bot("rm_bot")
        result = orch.unregister_bot("rm_bot")
        assert result is True
        assert orch.get_bot("rm_bot") is None

    def test_unregister_unknown_returns_false(self, orch):
        assert orch.unregister_bot("ghost") is False


class TestBuddyOrchestratorCatalog:
    def test_list_catalog_empty(self, orch):
        assert orch.list_catalog() == []

    def test_list_catalog_contains_registered(self, orch):
        orch.register_bot("cat_bot", category="finance")
        catalog = orch.list_catalog()
        assert any(b["bot_id"] == "cat_bot" for b in catalog)

    def test_catalog_item_keys(self, orch):
        orch.register_bot("full_bot", features=["feature_a"])
        item = orch.list_catalog()[0]
        for key in ("bot_id", "display_name", "category", "tier", "description", "price_usd", "features", "is_live"):
            assert key in item

    def test_catalog_features_list(self, orch):
        orch.register_bot("feat_bot", features=["a", "b", "c"])
        item = orch.list_catalog()[0]
        assert item["features"] == ["a", "b", "c"]

    def test_catalog_exposes_swarm_metadata(self, orch):
        orch.register_bot(
            "swarm_bot",
            coordination_mode="stigmergic",
            marl_enabled=True,
            stigmergic_channels=["shared_board"],
        )
        item = orch.list_catalog()[0]
        assert item["coordination_mode"] == "stigmergic"
        assert item["marl_enabled"] is True
        assert item["swarm_enabled"] is True


class TestBuddyOrchestratorRunBot:
    def test_run_unregistered_raises(self, orch):
        with pytest.raises(OrchestratorError):
            orch.run_bot("unknown_bot")

    def test_run_returns_dict(self, orch):
        orch.register_bot("rb")
        result = orch.run_bot("rb", task="test task")
        assert isinstance(result, dict)

    def test_run_result_keys(self, orch):
        orch.register_bot("rk")
        result = orch.run_bot("rk")
        for key in ("bot_id", "task", "result", "revenue_usd", "ran_at", "success"):
            assert key in result

    def test_run_success_true_on_happy_path(self, orch):
        orch.register_bot("happy")
        result = orch.run_bot("happy")
        assert result["success"] is True

    def test_run_with_custom_runner(self, orch):
        orch.register_bot("custom")
        runner = lambda bid, task: {"custom": True}
        result = orch.run_bot("custom", runner=runner)
        assert result["result"] == {"custom": True}

    def test_run_with_failing_runner(self, orch):
        orch.register_bot("fail_bot")
        def bad_runner(bid, task):
            raise RuntimeError("boom")
        result = orch.run_bot("fail_bot", runner=bad_runner)
        assert result["success"] is False

    def test_run_records_history(self, orch):
        orch.register_bot("history_bot")
        orch.run_bot("history_bot")
        assert len(orch._run_history) == 1

    def test_run_tracks_revenue(self, orch):
        orch.register_bot("rev_bot")
        orch.run_bot("rev_bot", revenue_usd=50.0)
        assert orch._revenue["rev_bot"] == 50.0

    def test_run_all_runs_each_bot(self, orch):
        orch.register_bot("ba")
        orch.register_bot("bb")
        results = orch.run_all()
        assert len(results) == 2


class TestBuddyOrchestratorDataAggregation:
    def test_aggregate_data_keys(self, orch):
        data = orch.aggregate_data()
        for key in ("timestamp", "bots", "runs", "revenue", "scraping", "data_store"):
            assert key in data

    def test_ingest_and_retrieve(self, orch):
        orch.ingest("key1", "value1")
        data = orch.aggregate_data()
        assert data["data_store"]["key1"] == "value1"

    def test_aggregate_counts_runs(self, orch):
        orch.register_bot("cnt")
        orch.run_bot("cnt")
        orch.run_bot("cnt")
        data = orch.aggregate_data()
        assert data["runs"]["total"] == 2

    def test_aggregate_total_revenue(self, orch):
        orch.register_bot("r1")
        orch.register_bot("r2")
        orch.run_bot("r1", revenue_usd=10.0)
        orch.run_bot("r2", revenue_usd=20.0)
        data = orch.aggregate_data()
        assert data["revenue"]["total_usd"] == 30.0

    def test_aggregate_includes_swarm_summary(self, orch):
        orch.register_bot(
            "swarm_bot",
            coordination_mode="decentralized",
            marl_enabled=True,
            stigmergic_channels=["shared_reward_map"],
        )
        data = orch.aggregate_data()
        assert data["swarm"]["swarm_enabled_bots"] == 1
        assert data["swarm"]["marl_enabled_bots"] == 1
        assert data["swarm"]["coordination_modes"]["decentralized"] == 1


class TestBuddyOrchestratorSwarmBenchmarks:
    def test_swarm_benchmark_report_is_ranked(self, orch):
        report = orch.swarm_benchmark_report()
        assert report["best_overall"] == "hybrid_llm_marl"
        assert report["architectures"][0]["overall_score"] >= report["architectures"][-1]["overall_score"]


class TestBuddyOrchestratorRevenueOptimisation:
    def test_top_revenue_bots_empty(self, orch):
        assert orch.top_revenue_bots() == []

    def test_top_revenue_bots_ordered(self, orch):
        orch.register_bot("low")
        orch.register_bot("high")
        orch.run_bot("low", revenue_usd=5.0)
        orch.run_bot("high", revenue_usd=100.0)
        top = orch.top_revenue_bots()
        assert top[0]["bot_id"] == "high"

    def test_top_revenue_bots_respects_n(self, orch):
        for i in range(10):
            orch.register_bot(f"b{i}")
            orch.run_bot(f"b{i}", revenue_usd=float(i))
        top = orch.top_revenue_bots(n=3)
        assert len(top) == 3

    def test_optimise_revenue_keys(self, orch):
        result = orch.optimise_revenue()
        assert "total_revenue_usd" in result
        assert "top_bots" in result
        assert "suggestions" in result

    def test_optimise_revenue_suggestion_inactive(self, orch):
        orch.register_bot("inactive_bot")
        result = orch.optimise_revenue()
        combined = " ".join(result["suggestions"])
        assert "not live" in combined


class TestBuddyOrchestratorGoLive:
    def test_go_live_marks_spec(self, orch):
        orch.register_bot("live_bot")
        orch.go_live("live_bot")
        assert orch._catalog["live_bot"].is_live is True

    def test_go_live_unknown_raises(self, orch):
        with pytest.raises(OrchestratorError):
            orch.go_live("ghost")

    def test_deactivate_unsets_live(self, orch):
        orch.register_bot("dbot")
        orch.go_live("dbot")
        orch.deactivate("dbot")
        assert orch._catalog["dbot"].is_live is False

    def test_deactivate_unknown_raises(self, orch):
        with pytest.raises(OrchestratorError):
            orch.deactivate("ghost")


class TestBuddyOrchestratorGitHubActions:
    def test_status_keys(self, orch):
        result = orch.github_actions_status()
        assert "repo" in result
        assert "runs" in result
        assert "source" in result

    def test_status_returns_repo(self, orch):
        result = orch.github_actions_status()
        assert result["repo"] == "test-owner/test-repo"

    def test_status_unavailable_without_requests(self, orch):
        with patch.dict("sys.modules", {"requests": None}):
            result = orch.github_actions_status()
        # Should not raise; runs will be empty
        assert isinstance(result["runs"], list)

    def test_status_parses_api_response(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 1,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-01T00:00:00Z",
                    "html_url": "https://github.com/test/run/1",
                }
            ]
        }
        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.github_actions_status(per_page=1)
        assert len(result["runs"]) == 1
        assert result["runs"][0]["name"] == "CI"
        assert result["source"] == "github_api"


class TestBuddyOrchestratorStatus:
    def test_status_keys(self, orch):
        s = orch.status()
        for key in ("orchestrator", "github_repo", "catalog_size", "scraping_active", "scrape_deadline", "days_until_deadline", "total_runs", "total_revenue_usd"):
            assert key in s

    def test_status_orchestrator_name(self, orch):
        assert orch.status()["orchestrator"] == "BuddyOrchestrator"

    def test_status_catalog_size_reflects_registrations(self, orch):
        orch.register_bot("x")
        orch.register_bot("y")
        assert orch.status()["catalog_size"] == 2

    def test_status_scrape_deadline(self, orch):
        assert orch.status()["scrape_deadline"] == "2026-06-22"

    def test_status_reports_swarm_overview(self, orch):
        orch.register_bot("swarm_bot", coordination_mode="decentralized")
        status = orch.status()
        assert status["swarm_enabled_bots"] == 1
        assert status["best_swarm_architecture"] == "hybrid_llm_marl"


class TestBuddyOrchestratorIntegration:
    def test_full_cycle(self):
        orch = BuddyOrchestrator(github_repo="owner/repo")
        orch.register_bot("buddy_bot", tier="PRO", price_usd=49.0, features=["chat", "emotion"])
        orch.register_bot("sales_bot", tier="ENTERPRISE", price_usd=99.0)
        orch.go_live("buddy_bot")
        orch.run_bot("buddy_bot", revenue_usd=49.0)
        orch.run_bot("sales_bot", revenue_usd=99.0)
        orch.ingest("active_users", 1500)

        data = orch.aggregate_data()
        assert data["bots"]["registered"] == 2
        assert data["bots"]["live"] == 1
        assert data["revenue"]["total_usd"] == 148.0
        assert data["data_store"]["active_users"] == 1500

        opt = orch.optimise_revenue()
        assert opt["top_bots"][0]["bot_id"] == "sales_bot"


# ===========================================================================
# Post-merge recovery
# ===========================================================================


class TestBuddyOrchestratorFindIncompleteRuns:
    def test_keys_present(self, orch):
        result = orch.find_incomplete_runs()
        for key in ("repo", "incomplete_runs", "total_checked", "fetched_at"):
            assert key in result

    def test_returns_correct_repo(self, orch):
        result = orch.find_incomplete_runs()
        assert result["repo"] == "test-owner/test-repo"

    def test_incomplete_runs_is_list(self, orch):
        result = orch.find_incomplete_runs()
        assert isinstance(result["incomplete_runs"], list)

    def test_total_checked_is_int(self, orch):
        result = orch.find_incomplete_runs()
        assert isinstance(result["total_checked"], int)

    def test_graceful_without_requests(self, orch):
        with patch.dict("sys.modules", {"requests": None}):
            result = orch.find_incomplete_runs()
        assert result["incomplete_runs"] == []
        assert result["total_checked"] == 0

    def test_filters_failure_conclusion(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 1,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "failure",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-01T00:00:00Z",
                    "html_url": "https://github.com/test/run/1",
                },
                {
                    "id": 2,
                    "name": "Deploy",
                    "status": "completed",
                    "conclusion": "success",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-01T01:00:00Z",
                    "html_url": "https://github.com/test/run/2",
                },
            ]
        }
        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.find_incomplete_runs()
        assert result["total_checked"] == 2
        assert len(result["incomplete_runs"]) == 1
        assert result["incomplete_runs"][0]["id"] == 1

    def test_filters_cancelled_conclusion(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 10,
                    "name": "Tests",
                    "status": "completed",
                    "conclusion": "cancelled",
                    "head_branch": "feature",
                    "event": "push",
                    "run_started_at": "2026-05-02T00:00:00Z",
                    "html_url": "https://github.com/test/run/10",
                }
            ]
        }
        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.find_incomplete_runs()
        assert len(result["incomplete_runs"]) == 1

    def test_filters_in_progress_status(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 20,
                    "name": "Lint",
                    "status": "in_progress",
                    "conclusion": None,
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-02T00:00:00Z",
                    "html_url": "https://github.com/test/run/20",
                }
            ]
        }
        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.find_incomplete_runs()
        assert len(result["incomplete_runs"]) == 1
        assert result["incomplete_runs"][0]["id"] == 20

    def test_successful_runs_excluded(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 30,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-02T00:00:00Z",
                    "html_url": "https://github.com/test/run/30",
                }
            ]
        }
        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.find_incomplete_runs()
        assert len(result["incomplete_runs"]) == 0


class TestBuddyOrchestratorRerunWorkflowRun:
    def test_returns_triggered_true_on_201(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.rerun_workflow_run(run_id=42)
        assert result["triggered"] is True
        assert result["run_id"] == 42

    def test_returns_triggered_true_on_204(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.rerun_workflow_run(run_id=99)
        assert result["triggered"] is True

    def test_returns_triggered_false_on_error_status(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.rerun_workflow_run(run_id=7)
        assert result["triggered"] is False
        assert "HTTP 403" in result["error"]

    def test_graceful_without_requests(self, orch):
        with patch.dict("sys.modules", {"requests": None}):
            result = orch.rerun_workflow_run(run_id=55)
        assert result["triggered"] is False
        assert "run_id" in result

    def test_failed_jobs_only_uses_correct_endpoint(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            orch.rerun_workflow_run(run_id=1, failed_jobs_only=True)
        called_url = mock_requests.post.call_args[0][0]
        assert "rerun-failed-jobs" in called_url

    def test_full_rerun_uses_correct_endpoint(self, orch):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        with patch.dict("sys.modules", {"requests": mock_requests}):
            orch.rerun_workflow_run(run_id=2, failed_jobs_only=False)
        called_url = mock_requests.post.call_args[0][0]
        assert called_url.endswith("/rerun")


class TestBuddyOrchestratorPostMergeRecovery:
    def test_keys_present(self, orch):
        result = orch.post_merge_recovery()
        for key in ("repo", "total_checked", "incomplete_found", "rerun_results", "fetched_at"):
            assert key in result

    def test_returns_correct_repo(self, orch):
        result = orch.post_merge_recovery()
        assert result["repo"] == "test-owner/test-repo"

    def test_rerun_results_is_list(self, orch):
        result = orch.post_merge_recovery()
        assert isinstance(result["rerun_results"], list)

    def test_graceful_without_requests(self, orch):
        with patch.dict("sys.modules", {"requests": None}):
            result = orch.post_merge_recovery()
        assert result["incomplete_found"] == 0
        assert result["rerun_results"] == []

    def test_reruns_each_incomplete_run(self, orch):
        # Simulate two failed runs found
        list_response = MagicMock()
        list_response.status_code = 200
        list_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 101,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "failure",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-01T00:00:00Z",
                    "html_url": "https://github.com/test/run/101",
                },
                {
                    "id": 102,
                    "name": "Deploy",
                    "status": "completed",
                    "conclusion": "timed_out",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-01T01:00:00Z",
                    "html_url": "https://github.com/test/run/102",
                },
            ]
        }
        rerun_response = MagicMock()
        rerun_response.status_code = 201

        mock_requests = MagicMock()
        mock_requests.get.return_value = list_response
        mock_requests.post.return_value = rerun_response

        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.post_merge_recovery()

        assert result["total_checked"] == 2
        assert result["incomplete_found"] == 2
        assert len(result["rerun_results"]) == 2
        assert all(r["triggered"] for r in result["rerun_results"])

    def test_no_reruns_when_all_successful(self, orch):
        list_response = MagicMock()
        list_response.status_code = 200
        list_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 200,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "head_branch": "main",
                    "event": "push",
                    "run_started_at": "2026-05-02T00:00:00Z",
                    "html_url": "https://github.com/test/run/200",
                }
            ]
        }
        mock_requests = MagicMock()
        mock_requests.get.return_value = list_response

        with patch.dict("sys.modules", {"requests": mock_requests}):
            result = orch.post_merge_recovery()

        assert result["total_checked"] == 1
        assert result["incomplete_found"] == 0
        assert result["rerun_results"] == []
