"""Dashboard data helper for the DreamCobots platform."""
from datetime import datetime


class DashboardData:
    """Stores and provides metrics and events for the DreamCobots dashboard."""

    def __init__(self):
        """Initialize the dashboard data store."""
        self._metrics = {}
        self._events = []

    def update_metrics(self, metrics_dict: dict):
        """Update the current metrics snapshot."""
        self._metrics = dict(metrics_dict)
        self._metrics["updated_at"] = datetime.utcnow().isoformat()

    def get_metrics(self) -> dict:
        """Return the most recent metrics snapshot."""
        return dict(self._metrics)

    def add_event(self, event: str):
        """Add a new event to the events log."""
        self._events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
        })
        if len(self._events) > 200:
            self._events = self._events[-200:]

    def get_events(self) -> list:
        """Return the most recent events."""
        return list(self._events[-50:])
