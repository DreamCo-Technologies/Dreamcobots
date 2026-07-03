import json
import os
import sys
from unittest import mock

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from BuddyAI.event_bus import EventBus
from BuddyAI.income_dashboard import Dashboard as IncomeDashboard
from bots.control_tower.control_tower import GitHubRepoManager
from bots.division_performance_dashboard.division_performance_dashboard import DivisionPerformanceDashboard
from bots.dreamco_empire_os.empire_os import DreamCoEmpireOS
from dashboards.super_dashboard import DEFAULT_REGISTRY_PATH, SuperDashboard
from dashboards.super_dashboard_web import create_app
from sandbox.sandbox import SandboxTester


def _min_category_expectations():
    return {
        "Bot Health & Status": 15,
        "Performance Metrics": 15,
        "Revenue & Financial": 15,
        "Resource Utilization": 12,
        "API & Integration": 12,
        "Security & Compliance": 10,
        "Data Quality": 10,
        "Infrastructure": 10,
        "Workflow & Task": 10,
        "User & Experience": 10,
        "Cost Optimization": 8,
        "Division Metrics": 12,
    }


def _make_engine() -> SuperDashboard:
    engine = SuperDashboard(DEFAULT_REGISTRY_PATH)
    engine.sources = [
        ("buddyai_income", lambda: {"revenue_24h": 12450.0, "traffic_24h": 145230.0, "engagement": 88.0}),
        ("dreamco_empire_os", lambda: {"active_bots": 38, "healthy_bots": 38, "unhealthy_bots": 0}),
        ("division_performance", lambda: {"division_count": 5, "api_calls": 145230, "avg_response_ms": 235.0}),
        ("command_tower", lambda: {"open_pr_count": 5, "open_issue_count": 12, "last_workflow_status": "success"}),
        ("performance_sandbox", lambda: {"avg_latency_ms": 145.0, "throughput_ops_per_second": 320.0, "roi_percent": 62.0}),
        ("web_dashboard", lambda: {"catalog_total": 45, "live_bots": 23, "governance_mode": "balanced"}),
    ]
    return engine


def test_registry_contains_200_plus_metrics_with_required_categories():
    data = json.loads(DEFAULT_REGISTRY_PATH.read_text(encoding="utf-8"))
    metrics = data["metrics"]
    assert len(metrics) >= 200

    counts = {}
    for metric in metrics:
        counts[metric["category"]] = counts.get(metric["category"], 0) + 1

    for category, minimum in _min_category_expectations().items():
        assert counts.get(category, 0) >= minimum


def test_build_snapshot_returns_expected_rollups_and_health_ranges():
    engine = _make_engine()
    snapshot = engine.build_snapshot()

    assert snapshot["summary"]["total_checks"] >= 200
    assert 1 <= snapshot["summary"]["overall_health_score"] <= 100
    assert len(snapshot["metrics"]) == snapshot["summary"]["total_checks"]
    assert snapshot["division_scores"]
    assert snapshot["bot_scores"]

    for metric in snapshot["metrics"]:
        assert metric["status"] in {"healthy", "warning", "critical"}
        assert 1 <= metric["health_score"] <= 100


def test_export_formats_return_non_empty_output():
    engine = _make_engine()
    engine.build_snapshot()

    exported_json = engine.export_json()
    exported_csv = engine.export_csv()
    exported_html = engine.export_html_report()

    assert '"metrics"' in exported_json
    assert "id,name,category" in exported_csv.splitlines()[0]
    assert "<table" in exported_html


def test_super_dashboard_web_endpoints_support_filters_and_exports():
    engine = _make_engine()
    app = create_app(engine)
    client = app.test_client()

    metrics_payload = client.get("/api/metrics?category=Bot%20Health%20%26%20Status&status=healthy&sort_by=value&order=desc")
    assert metrics_payload.status_code == 200
    metrics_data = metrics_payload.get_json()
    assert metrics_data["summary"]["total_checks"] >= 1
    assert all(item["category"] == "Bot Health & Status" for item in metrics_data["metrics"])

    scores_payload = client.get("/api/health-scores")
    assert scores_payload.status_code == 200
    scores_data = scores_payload.get_json()
    assert scores_data["division_scores"]

    csv_export = client.get("/api/export/csv")
    assert csv_export.status_code == 200
    assert "text/csv" in csv_export.content_type


def test_existing_dashboards_expose_super_dashboard_snapshots():
    income_dashboard = IncomeDashboard(cfg={"dashboard_output_dir": "/tmp"}, bus=EventBus())
    income_payload = income_dashboard.super_dashboard_snapshot(
        {
            "total_revenue": 12500.0,
            "total_traffic": 145000,
            "source_count": 3,
            "top_source": "ads",
            "by_source": {
                "ads": {"engagement": 81.0},
                "affiliate": {"engagement": 77.0},
            },
        }
    )
    assert income_payload["revenue_24h"] == 12500.0

    empire_payload = DreamCoEmpireOS().super_dashboard_snapshot()
    assert "active_bots" in empire_payload

    division_payload = DivisionPerformanceDashboard().super_dashboard_snapshot()
    assert "api_calls" in division_payload

    sandbox_payload = SandboxTester().super_dashboard_snapshot()
    assert "roi_percent" in sandbox_payload

    with mock.patch.object(GitHubRepoManager, "get_repo_status", return_value={
        "summary": {"open_pr_count": 5, "open_issue_count": 4, "last_workflow_status": "success"},
        "workflow_runs": [{"name": "CI", "conclusion": "success"}],
    }):
        tower_payload = GitHubRepoManager().super_dashboard_snapshot("DreamCo-Technologies", "Dreamcobots")
    assert tower_payload["open_pr_count"] == 5
