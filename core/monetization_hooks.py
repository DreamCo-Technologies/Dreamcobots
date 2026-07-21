"""MonetizationHooks: funnel tracking and conversion management."""
import logging
from typing import Callable, Dict, List, Optional


class MonetizationHooks:
    """Tracks funnel stages and conversion events for lead-to-revenue pipelines."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._funnel: List[Dict] = []
        self._callbacks: Dict[str, List[Callable]] = {}

    def track(self, stage: str, metadata: Optional[Dict] = None) -> None:
        """Record a funnel stage event."""
        entry = {"stage": stage, "metadata": metadata or {}}
        self._funnel.append(entry)
        self.logger.info("Funnel stage tracked: %s | metadata=%s", stage, metadata)
        for cb in self._callbacks.get(stage, []):
            cb(entry)

    def on_stage(self, stage: str, callback: Callable) -> None:
        """Register a callback to fire when a specific funnel stage is reached."""
        self._callbacks.setdefault(stage, []).append(callback)

    def conversion_rate(self, from_stage: str, to_stage: str) -> float:
        """Return the conversion rate between two funnel stages."""
        from_count = sum(1 for e in self._funnel if e["stage"] == from_stage)
        to_count = sum(1 for e in self._funnel if e["stage"] == to_stage)
        if from_count == 0:
            return 0.0
        return to_count / from_count

    def funnel_report(self) -> List[Dict]:
        """Return all funnel events."""
        return list(self._funnel)

    def reset(self) -> None:
        """Clear all funnel events."""
        self._funnel.clear()
