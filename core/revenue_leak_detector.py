"""Cross-reference bot activity and Stripe charges to detect revenue leaks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class RevenueLeak:
    bot_id: str
    activity_id: str
    estimated_loss_usd: float


class RevenueLeakDetector:
    """Flag activities that should have produced a charge within 60 seconds."""

    def detect(self, activities: list[dict[str, Any]], charges: list[dict[str, Any]]) -> list[RevenueLeak]:
        leaks = []
        for activity in activities:
            activity_time = datetime.fromisoformat(activity["timestamp"])
            matches = [
                charge
                for charge in charges
                if charge.get("bot_id") == activity.get("bot_id")
                and abs((datetime.fromisoformat(charge["timestamp"]) - activity_time).total_seconds()) <= 60
            ]
            if not matches:
                leaks.append(
                    RevenueLeak(
                        bot_id=activity.get("bot_id", "unknown"),
                        activity_id=activity.get("activity_id", "unknown"),
                        estimated_loss_usd=float(activity.get("estimated_value_usd", 0.0)),
                    )
                )
        return leaks
