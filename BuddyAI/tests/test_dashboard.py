# Tests for BuddyAI dashboard (metrics, stress tests, dashboard rendering).

import pytest

from BuddyAI.dashboard.metrics import MetricsCollector
from BuddyAI.dashboard.stress_test import StressTestRunner
from BuddyAI.dashboard.dashboard import ClientDashboard
from BuddyAI.financial.models import Account


# ---------------------------------------------------------------------------
# MetricsCollector tests
# ---------------------------------------------------------------------------

class TestMetricsCollector:
    def setup_method(self):
        self.metrics = MetricsCollector(client_id="client-1")

    def test_record_task_increments_count(self):
        self.metrics.record_task("t1", "scrape", 1.5)
        self.metrics.record_task("t2", "analyze", 2.0)
        assert self.metrics.tasks_completed_count() == 2

    def test_failed_task_not_counted_as_completed(self):
        self.metrics.record_task("t1", "scrape", 1.5, status="failed")
        assert self.metrics.tasks_completed_count() == 0

    def test_average_task_duration(self):
        self.metrics.record_task("t1", "a", 2.0)
        self.metrics.record_task("t2", "b", 4.0)
        assert self.metrics.average_task_duration() == pytest.approx(3.0)

    def test_average_task_duration_no_tasks(self):
        assert self.metrics.average_task_duration() == 0.0

    def test_filter_tasks_by_status(self):
        self.metrics.record_task("t1", "a", 1.0, status="completed")
        self.metrics.record_task("t2", "b", 1.0, status="failed")
        completed = self.metrics.get_tasks(status="completed")
        assert len(completed) == 1
        assert completed[0].task_id == "t1"

    def test_record_compute_snapshot(self):
        snap = self.metrics.record_compute_snapshot(cpu_percent=55.0, memory_percent=70.0)
        assert snap.cpu_percent == 55.0
        assert snap.memory_percent == 70.0

    def test_average_cpu_usage(self):
        self.metrics.record_compute_snapshot(cpu_percent=40.0, memory_percent=50.0)
        self.metrics.record_compute_snapshot(cpu_percent=60.0, memory_percent=70.0)
        assert self.metrics.average_cpu_usage() == pytest.approx(50.0)

    def test_average_memory_usage(self):
        self.metrics.record_compute_snapshot(cpu_percent=40.0, memory_percent=50.0)
        self.metrics.record_compute_snapshot(cpu_percent=60.0, memory_percent=70.0)
        assert self.metrics.average_memory_usage() == pytest.approx(60.0)

    def test_no_compute_snapshots_returns_zero(self):
        assert self.metrics.average_cpu_usage() == 0.0
        assert self.metrics.average_memory_usage() == 0.0

    def test_record_earning_accumulates(self):
        self.metrics.record_earning(100.0)
        self.metrics.record_earning(50.0)
        assert self.metrics.total_earnings() == pytest.approx(150.0)

    def test_earnings_timeline_sorted(self):
        from datetime import datetime
        dt_jan1 = datetime(2024, 1, 1)
        dt_jan2 = datetime(2024, 1, 2)
        dt_jan3 = datetime(2024, 1, 3)
        # Record in out-of-order fashion; timeline() should return sorted ascending.
        self.metrics.record_earning(30.0, timestamp=dt_jan3)
        self.metrics.record_earning(10.0, timestamp=dt_jan1)
        self.metrics.record_earning(20.0, timestamp=dt_jan2)
        tl = self.metrics.earnings_timeline()
        amounts = [e["amount"] for e in tl]
        assert amounts == [10.0, 20.0, 30.0]

    def test_summary_contains_expected_keys(self):
        summary = self.metrics.summary()
        assert "tasks_completed" in summary
        assert "total_earnings" in summary
        assert "average_cpu_percent" in summary
        assert "average_memory_percent" in summary


# ---------------------------------------------------------------------------
# StressTestRunner tests
# ---------------------------------------------------------------------------

class TestStressTestRunner:
    def setup_method(self):
        self.runner = StressTestRunner()

    def test_run_returns_result_with_correct_iterations(self):
        result = self.runner.run(target=lambda: None, test_name="noop", iterations=50)
        assert result.iterations == 50
        assert result.successful_ops == 50
        assert result.failed_ops == 0

    def test_run_counts_failures(self):
        def always_fail():
            raise RuntimeError("simulated failure")

        result = self.runner.run(target=always_fail, test_name="fail_test", iterations=10)
        assert result.failed_ops == 10
        assert result.successful_ops == 0

    def test_success_rate_all_pass(self):
        result = self.runner.run(target=lambda: None, test_name="ok", iterations=20)
        assert result.success_rate == 1.0

    def test_success_rate_all_fail(self):
        result = self.runner.run(
            target=lambda: (_ for _ in ()).throw(Exception("err")),
            test_name="fail",
            iterations=5,
        )
        assert result.success_rate == 0.0

    def test_ops_per_second_positive(self):
        result = self.runner.run(target=lambda: None, test_name="speed", iterations=100)
        assert result.ops_per_second > 0

    def test_zero_iterations_raises(self):
        with pytest.raises(ValueError, match="iterations"):
            self.runner.run(target=lambda: None, test_name="bad", iterations=0)

    def test_list_results_sorted_descending(self):
        r1 = self.runner.run(target=lambda: None, test_name="first", iterations=5)
        r2 = self.runner.run(target=lambda: None, test_name="second", iterations=5)
        results = self.runner.list_results()
        # Most recent first
        assert results[0].test_id == r2.test_id

    def test_result_to_dict_has_required_fields(self):
        result = self.runner.run(target=lambda: None, test_name="dict_test", iterations=1)
        d = result.to_dict()
        for key in (
            "test_id", "test_name", "iterations", "successful_ops",
            "failed_ops", "success_rate", "ops_per_second",
        ):
            assert key in d


# ---------------------------------------------------------------------------
# ClientDashboard tests
# ---------------------------------------------------------------------------

class TestClientDashboard:
    def setup_method(self):
        self.account = Account(owner_id="c1", owner_name="Alice", balance=250.0)
        self.dashboard = ClientDashboard(
            client_id="c1",
            client_name="Alice",
            account=self.account,
        )

    def test_render_contains_top_level_keys(self):
        data = self.dashboard.render()
        for key in ("client_id", "client_name", "profitability", "compute_usage", "tasks", "stress_tests", "visualizations"):
            assert key in data

    def test_render_account_balance(self):
        data = self.dashboard.render()
        assert data["account_balance"] == pytest.approx(250.0)

    def test_render_no_account(self):
        dash = ClientDashboard(client_id="x", client_name="Bob")
        data = dash.render()
        assert data["account_balance"] is None

    def test_dashboard_records_tasks_and_reflects_in_render(self):
        self.dashboard.metrics.record_task("t1", "scrape", 3.0)
        data = self.dashboard.render()
        assert data["tasks"]["completed"] == 1
        assert len(data["tasks"]["records"]) == 1

    def test_dashboard_earnings_reflected_in_render(self):
        self.dashboard.metrics.record_earning(200.0)
        data = self.dashboard.render()
        assert data["profitability"]["total_earnings"] == pytest.approx(200.0)

    def test_dashboard_compute_snapshots_in_render(self):
        self.dashboard.metrics.record_compute_snapshot(cpu_percent=30.0, memory_percent=50.0)
        data = self.dashboard.render()
        assert len(data["compute_usage"]["snapshots"]) == 1

    def test_visualizations_populated_after_snapshots_and_earnings(self):
        self.dashboard.metrics.record_compute_snapshot(cpu_percent=50.0, memory_percent=60.0)
        self.dashboard.metrics.record_earning(100.0)
        data = self.dashboard.render()
        viz = data["visualizations"]
        assert len(viz["cpu_over_time"]) == 1
        assert len(viz["memory_over_time"]) == 1
        assert len(viz["earnings_over_time"]) == 1

    def test_print_summary_runs_without_error(self, capsys):
        self.dashboard.metrics.record_task("t1", "task_a", 1.5)
        self.dashboard.metrics.record_earning(50.0)
        self.dashboard.print_summary()
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "50.00" in captured.out
