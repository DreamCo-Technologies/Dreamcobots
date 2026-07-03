"""Unified Super Dashboard metrics engine."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = Path(__file__).with_name("metrics_registry.json")

STATUS_SCORE = {"healthy": 100, "warning": 70, "critical": 35}
DIVISIONS = ["DreamCyber", "DreamFinance", "DreamOps", "DreamAgents", "DreamCommerce"]
BOTS = [
    "DreamBuddy",
    "ControlTower",
    "RevenuePilot",
    "OpsGuard",
    "APIFlow",
    "InsightForge",
]


@dataclass(frozen=True)
class MetricDefinition:
    id: str
    name: str
    category: str
    description: str
    unit: str
    direction: str
    warning_threshold: float
    critical_threshold: float
    division_scoped: bool
    bot_scoped: bool


class SuperDashboard:
    """Aggregates dashboard data and computes 200+ health checks."""

    def __init__(self, registry_path: str | Path = DEFAULT_REGISTRY_PATH, history_days: int = 30) -> None:
        self.registry_path = Path(registry_path)
        self.history_days = history_days
        self.metric_definitions = self._load_registry()
        self.refresh_interval_seconds = self._read_registry_value("refresh_interval_seconds", 10)
        self.history: deque[dict[str, Any]] = deque(maxlen=max(history_days * 24 * 6, 1))
        self.sources: list[tuple[str, Callable[[], dict[str, Any]]]] = [
            ("buddyai_income", self._collect_buddyai_income),
            ("dreamco_empire_os", self._collect_empire_os),
            ("division_performance", self._collect_division_performance),
            ("command_tower", self._collect_command_tower),
            ("performance_sandbox", self._collect_performance_sandbox),
            ("web_dashboard", self._collect_web_dashboard),
        ]

    def _read_registry_value(self, key: str, default: Any) -> Any:
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            return data.get(key, default)
        except Exception:
            return default

    def _load_registry(self) -> list[MetricDefinition]:
        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        return [
            MetricDefinition(
                id=m["id"],
                name=m["name"],
                category=m["category"],
                description=m["description"],
                unit=m["unit"],
                direction=m["direction"],
                warning_threshold=float(m["warning_threshold"]),
                critical_threshold=float(m["critical_threshold"]),
                division_scoped=bool(m.get("division_scoped", False)),
                bot_scoped=bool(m.get("bot_scoped", False)),
            )
            for m in data.get("metrics", [])
        ]

    def register_source(self, name: str, collector: Callable[[], dict[str, Any]]) -> None:
        self.sources.append((name, collector))

    def collect_source_data(self) -> dict[str, Any]:
        snapshots: dict[str, Any] = {}
        for name, source in self.sources:
            try:
                snapshots[name] = source()
            except Exception as exc:  # pragma: no cover
                snapshots[name] = {"status": "unavailable", "error": str(exc)}
        return snapshots

    def build_snapshot(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        source_data = self.collect_source_data()
        checks = [self._evaluate_metric(metric, source_data, now) for metric in self.metric_definitions]
        division_scores = self._score_entities(checks, key="division")
        bot_scores = self._score_entities(checks, key="bot")
        health_rollup = self._health_rollup(checks)
        snapshot = {
            "timestamp": now.isoformat(),
            "metrics": checks,
            "summary": {
                "total_checks": len(checks),
                "by_status": dict(Counter(check["status"] for check in checks)),
                "by_category": dict(Counter(check["category"] for check in checks)),
                "overall_health_score": health_rollup,
            },
            "division_scores": division_scores,
            "bot_scores": bot_scores,
            "sources": source_data,
        }
        self.history.append(snapshot)
        return snapshot

    def latest_snapshot(self) -> dict[str, Any]:
        if self.history:
            return self.history[-1]
        return self.build_snapshot()

    def get_historical_trend(self, days: int = 30) -> list[dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=min(days, self.history_days))
        return [
            {
                "timestamp": s["timestamp"],
                "overall_health_score": s["summary"]["overall_health_score"],
                "warning": s["summary"]["by_status"].get("warning", 0),
                "critical": s["summary"]["by_status"].get("critical", 0),
            }
            for s in self.history
            if datetime.fromisoformat(s["timestamp"]) >= cutoff
        ]

    def comparative_analysis(self) -> dict[str, Any]:
        snapshot = self.latest_snapshot()
        division_ranked = sorted(snapshot["division_scores"].items(), key=lambda item: item[1], reverse=True)
        bot_ranked = sorted(snapshot["bot_scores"].items(), key=lambda item: item[1], reverse=True)
        return {
            "division_vs_division": division_ranked,
            "bot_vs_bot": bot_ranked,
        }

    def export_json(self) -> str:
        return json.dumps(self.latest_snapshot(), indent=2)

    def export_csv(self) -> str:
        rows = self.latest_snapshot()["metrics"]
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=["id", "name", "category", "division", "bot", "value", "unit", "status", "health_score", "updated_at"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in writer.fieldnames})
        return buffer.getvalue()

    def export_html_report(self) -> str:
        snapshot = self.latest_snapshot()
        rows = "".join(
            f"<tr><td>{m['id']}</td><td>{m['name']}</td><td>{m['category']}</td><td>{m['division'] or '-'}"
            f"</td><td>{m['bot'] or '-'}</td><td>{m['value']}</td><td>{m['status']}</td><td>{m['health_score']}</td></tr>"
            for m in snapshot["metrics"]
        )
        return (
            "<html><head><title>Super Dashboard Report</title></head><body>"
            f"<h1>Super Dashboard Report</h1><p>Generated: {snapshot['timestamp']}</p>"
            f"<p>Overall health: {snapshot['summary']['overall_health_score']}</p>"
            "<table border='1' cellpadding='4'><tr><th>ID</th><th>Name</th><th>Category</th><th>Division</th>"
            "<th>Bot</th><th>Value</th><th>Status</th><th>Health</th></tr>"
            f"{rows}</table></body></html>"
        )

    def _evaluate_metric(self, metric: MetricDefinition, source_data: dict[str, Any], now: datetime) -> dict[str, Any]:
        value = self._metric_value(metric, source_data)
        status = self._metric_status(metric, value)
        health_score = STATUS_SCORE[status]
        division = DIVISIONS[hash(metric.id) % len(DIVISIONS)] if metric.division_scoped else None
        bot = BOTS[hash(metric.name) % len(BOTS)] if metric.bot_scoped else None
        return {
            "id": metric.id,
            "name": metric.name,
            "category": metric.category,
            "description": metric.description,
            "division": division,
            "bot": bot,
            "value": round(value, 3),
            "unit": metric.unit,
            "status": status,
            "health_score": health_score,
            "warning_threshold": metric.warning_threshold,
            "critical_threshold": metric.critical_threshold,
            "updated_at": now.isoformat(),
        }

    def _metric_value(self, metric: MetricDefinition, source_data: dict[str, Any]) -> float:
        buddy = source_data.get("buddyai_income", {})
        revenue_total = float(buddy.get("revenue_24h", 12000.0))
        traffic = float(buddy.get("traffic_24h", 140000.0))

        empire = source_data.get("dreamco_empire_os", {})
        active_bots = float(empire.get("active_bots", 38))

        command = source_data.get("command_tower", {})
        open_prs = float(command.get("open_pr_count", 5))

        seed = (sum(ord(ch) for ch in metric.id) % 19) + 1
        if metric.category == "Revenue & Financial":
            return revenue_total + (seed * 250)
        if metric.category == "Performance Metrics":
            return 80 + seed * 16
        if metric.category == "Bot Health & Status":
            return max(70.0, 100 - seed)
        if metric.category == "Resource Utilization":
            return 20 + seed * 3
        if metric.category == "API & Integration":
            return round(seed * 0.38, 3)
        if metric.category == "Security & Compliance":
            return max(0.0, float(seed - 8))
        if metric.category == "Data Quality":
            return max(75.0, 100 - seed * 0.9)
        if metric.category == "Infrastructure":
            return max(85.0, 100 - seed * 0.4)
        if metric.category == "Workflow & Task":
            return max(80.0, 100 - seed * 0.7)
        if metric.category == "User & Experience":
            return max(75.0, 100 - seed * 1.2)
        if metric.category == "Cost Optimization":
            return 55 + seed * 2.5
        if metric.category == "Division Metrics":
            return min(100.0, 70 + active_bots * 0.3 + open_prs * 0.2 + seed * 0.9)
        return traffic / 1000 + seed

    @staticmethod
    def _metric_status(metric: MetricDefinition, value: float) -> str:
        if metric.direction == "higher_is_better":
            if value < metric.critical_threshold:
                return "critical"
            if value < metric.warning_threshold:
                return "warning"
            return "healthy"

        if value > metric.critical_threshold:
            return "critical"
        if value > metric.warning_threshold:
            return "warning"
        return "healthy"

    @staticmethod
    def _score_entities(metrics: list[dict[str, Any]], key: str) -> dict[str, int]:
        grouped: dict[str, list[int]] = defaultdict(list)
        for metric in metrics:
            entity = metric.get(key)
            if entity:
                grouped[entity].append(metric["health_score"])
        return {entity: max(1, min(100, int(sum(scores) / max(1, len(scores))))) for entity, scores in grouped.items()}

    @staticmethod
    def _health_rollup(metrics: list[dict[str, Any]]) -> int:
        if not metrics:
            return 1
        return max(1, min(100, int(sum(metric["health_score"] for metric in metrics) / len(metrics))))

    # ------------------------------------------------------------------
    # Source collectors from existing dashboards
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_buddyai_income() -> dict[str, Any]:
        try:
            from BuddyAI.event_bus import EventBus
            from BuddyAI.income_dashboard import Dashboard

            dash = Dashboard(cfg={"dashboard_output_dir": "output/dashboard"}, bus=EventBus())
            sample_summary = {
                "total_revenue": 12450.0,
                "total_traffic": 145230.0,
                "source_count": 4,
                "top_source": "ads",
                "by_source": {"ads": {"engagement": 82.0}, "affiliate": {"engagement": 79.0}},
            }
            return dash.super_dashboard_snapshot(sample_summary)
        except Exception:
            return {"revenue_24h": 12450.0, "traffic_24h": 145230.0, "engagement": 82.0, "status": "sample"}

    @staticmethod
    def _collect_empire_os() -> dict[str, Any]:
        try:
            from bots.dreamco_empire_os.empire_os import DreamCoEmpireOS

            dashboard = DreamCoEmpireOS().super_dashboard_snapshot()
            return dashboard
        except Exception:
            return {"active_bots": 38, "healthy_bots": 38, "unhealthy_bots": 0, "status": "sample"}

    @staticmethod
    def _collect_division_performance() -> dict[str, Any]:
        try:
            from bots.division_performance_dashboard.division_performance_dashboard import DivisionPerformanceDashboard

            return DivisionPerformanceDashboard().super_dashboard_snapshot()
        except Exception:
            return {"division_count": 5, "api_calls": 145230, "avg_response_ms": 235.0, "status": "sample"}

    @staticmethod
    def _collect_command_tower() -> dict[str, Any]:
        try:
            from bots.control_tower.control_tower import GitHubRepoManager

            owner = "DreamCo-Technologies"
            repo = "Dreamcobots"
            return GitHubRepoManager().super_dashboard_snapshot(owner=owner, repo=repo)
        except Exception:
            return {"open_pr_count": 5, "open_issue_count": 12, "last_workflow_status": "unknown", "status": "sample"}

    @staticmethod
    def _collect_performance_sandbox() -> dict[str, Any]:
        try:
            from sandbox.sandbox import SandboxTester

            return SandboxTester().super_dashboard_snapshot()
        except Exception:
            return {"avg_latency_ms": 145.0, "throughput_ops_per_second": 320.0, "roi_percent": 62.0, "status": "sample"}

    @staticmethod
    def _collect_web_dashboard() -> dict[str, Any]:
        try:
            from ui.web_dashboard import super_dashboard_runtime_snapshot

            return super_dashboard_runtime_snapshot()
        except Exception:
            return {"catalog_total": 45, "live_bots": 20, "governance_mode": "balanced", "status": "sample"}


__all__ = ["SuperDashboard", "MetricDefinition", "DEFAULT_REGISTRY_PATH"]
