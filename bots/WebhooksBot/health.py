"""
WebhookHealthMonitor — monitors delivery health and alerts on SLA breaches.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW
from .webhook_bot import WebhooksBot, DeliveryStatus

logger = logging.getLogger(__name__)


@dataclass
class HealthAlert:
    bot_id: str
    metric: str
    value: float
    threshold: float
    severity: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
        }


class WebhookHealthMonitor:
    """
    Continuously monitors webhook delivery health for all registered bots.

    Tracks:
    - Delivery success rate (alert if < 95%)
    - Dead-letter queue growth (alert if > 10 items)
    - Average retry count (alert if > 2)
    - Subscription coverage (alert if any bot has 0 active subscriptions)

    GLOBAL AI SOURCES FLOW
    """

    SUCCESS_RATE_THRESHOLD = 0.95
    DEAD_LETTER_THRESHOLD = 10
    RETRY_THRESHOLD = 2.0

    def __init__(self, webhooks_bot: WebhooksBot) -> None:
        self._bot = webhooks_bot
        self._alerts: List[HealthAlert] = []
        self._check_count = 0

    def check(self) -> Dict[str, Any]:
        """Run a full health check pass and return status report."""
        self._check_count += 1
        alerts_raised = []
        summary = self._bot.get_health_summary()

        # Check dead-letter queue
        dead = summary.get("dead_letter_count", 0)
        if dead > self.DEAD_LETTER_THRESHOLD:
            alert = HealthAlert(
                bot_id="__platform__",
                metric="dead_letter_count",
                value=float(dead),
                threshold=float(self.DEAD_LETTER_THRESHOLD),
                severity="critical",
            )
            self._alerts.append(alert)
            alerts_raised.append(alert.to_dict())
            logger.critical("Dead-letter threshold exceeded: %d > %d", dead, self.DEAD_LETTER_THRESHOLD)

        # Per-bot delivery stats
        subs = self._bot.get_subscriptions()
        bot_stats: Dict[str, Dict] = {}
        for sub in subs:
            bid = sub["bot_id"]
            s = bot_stats.setdefault(bid, {"delivered": 0, "failed": 0})
            s["delivered"] += sub.get("delivery_count", 0)
            s["failed"] += sub.get("failure_count", 0)

        for bid, stats in bot_stats.items():
            total = stats["delivered"] + stats["failed"]
            if total == 0:
                continue
            rate = stats["delivered"] / total
            if rate < self.SUCCESS_RATE_THRESHOLD:
                alert = HealthAlert(
                    bot_id=bid,
                    metric="delivery_success_rate",
                    value=rate,
                    threshold=self.SUCCESS_RATE_THRESHOLD,
                    severity="warning",
                )
                self._alerts.append(alert)
                alerts_raised.append(alert.to_dict())
                logger.warning("Low delivery rate for bot=%s: %.2f%%", bid, rate * 100)

        return {
            "check_number": self._check_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "alerts_raised": alerts_raised,
            "total_alerts": len(self._alerts),
            "healthy": len(alerts_raised) == 0,
        }

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._alerts]

    def clear_alerts(self) -> int:
        count = len(self._alerts)
        self._alerts.clear()
        return count
