# Global Learning System Dashboards

Three integrated dashboards for monitoring DreamCo's global AI learning infrastructure.

## Dashboards

### Learning Dashboard (`learning_dashboard.py`)

Aggregates and displays key metrics from the Global Learning Matrix, ingestion pipeline, and classifier service.

```python
from global_learning_system.dashboards.learning_dashboard import LearningDashboard, DashboardPanel

dash = LearningDashboard()
dash.update("models_trained", 42)
panel = DashboardPanel(title="Pipeline", content=["Ingested: 1200", "Classified: 980"])
dash.add_panel(panel)
print(dash.render())
```

### Profit Dashboard (`profit_dashboard.py`)

Executive-level summary of financial performance, ROI records, and market signals.

```python
from global_learning_system.dashboards.profit_dashboard import ProfitDashboard

dash = ProfitDashboard()
dash.record_roi({"strategy_id": "s1", "revenue": 8000, "cost": 2000})
dash.record_signal({"strategy_id": "s1", "value": 0.85, "alert": False})
print(dash.render())
```

### Sandbox Dashboard (`sandbox_dashboard.py`)

Summary view of sandbox experiment runs — pass/fail rates, average durations, and metric trends.

```python
from global_learning_system.dashboards.sandbox_dashboard import SandboxDashboard

dash = SandboxDashboard()
dash.record_run({
    "experiment_name": "RL-test-01",
    "status": "pass",
    "duration_ms": 342.5,
    "metrics": {"accuracy": 0.93}
})
print(dash.render())
```

## Source

Implementations: [`global_learning_system/dashboards/`](../../global_learning_system/dashboards/)
