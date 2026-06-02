"""Cost monitoring alert engine with Slack and email dispatch hooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AlertRule:
    name: str
    threshold: float
    severity: str
    metric: str


@dataclass
class Alert:
    bot_id: str
    rule: AlertRule
    observed_value: float


class AlertEngine:
    """Evaluate cost thresholds against bot metrics."""

    def __init__(self) -> None:
        self.rules = [
            AlertRule(name="cost-per-call", threshold=0.01, severity="WARNING", metric="cost_per_call"),
            AlertRule(name="monthly-cost", threshold=500.0, severity="CRITICAL", metric="monthly_cost"),
        ]

    def evaluate(self, bot_metrics: dict[str, Any]) -> list[Alert]:
        alerts = []
        for rule in self.rules:
            value = float(bot_metrics.get(rule.metric, 0.0))
            if value > rule.threshold:
                alerts.append(Alert(bot_id=bot_metrics.get("bot_id", "unknown"), rule=rule, observed_value=value))
        return alerts

    def dispatch(self, alerts: list[Alert]) -> list[str]:
        messages = []
        for alert in alerts:
            message = f"[{alert.rule.severity}] {alert.bot_id} exceeded {alert.rule.metric}: {alert.observed_value}"
            messages.append(message)
        return messages
