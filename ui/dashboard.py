"""
DreamCo UI Dashboard

Text-based dashboard for managing bots, tracking tasks, reviewing costs,
and monitoring the DreamCo ecosystem.  Designed to be embedded in a web
UI or CLI tool.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DashboardWidget:
    """A single UI widget (card, table, chart placeholder)."""
    widget_id: str
    title: str
    data: Any
    widget_type: str = "card"   # 'card' | 'table' | 'chart' | 'status'


class BotDashboard:
    """
    Lightweight dashboard for DreamCo bot management.

    Renders a text summary of active bots, recent tasks, token balance,
    and cost justification reports.

    Usage
    -----
        from ui.dashboard import BotDashboard

        dash = BotDashboard(owner="DreamCo")
        dash.add_widget(DashboardWidget("w1", "Active Bots", {"count": 5}))
        print(dash.render())
    """

    def __init__(self, owner: str = "DreamCo") -> None:
        self.owner = owner
        self._widgets: list[DashboardWidget] = []

    def add_widget(self, widget: DashboardWidget) -> None:
        """Add a widget to the dashboard."""
        self._widgets.append(widget)

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget by ID.  Returns True if found and removed."""
        before = len(self._widgets)
        self._widgets = [w for w in self._widgets if w.widget_id != widget_id]
        return len(self._widgets) < before

    def get_widget(self, widget_id: str) -> Optional[DashboardWidget]:
        """Look up a widget by ID."""
        for w in self._widgets:
            if w.widget_id == widget_id:
                return w
        return None

    def render(self) -> str:
        """Render a text-based dashboard summary."""
        lines = [
            "=" * 60,
            f"DreamCo Bot Dashboard — {self.owner}",
            "=" * 60,
        ]
        if not self._widgets:
            lines.append("No widgets configured.")
        for widget in self._widgets:
            lines.append(f"\n[{widget.widget_type.upper()}] {widget.title}")
            if isinstance(widget.data, dict):
                for k, v in widget.data.items():
                    lines.append(f"  {k}: {v}")
            elif isinstance(widget.data, list):
                for item in widget.data:
                    lines.append(f"  • {item}")
            else:
                lines.append(f"  {widget.data}")
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def widget_count(self) -> int:
        """Number of widgets on the dashboard."""
        return len(self._widgets)

    def all_widgets(self) -> list[DashboardWidget]:
        """Return all widgets."""
        return list(self._widgets)


__all__ = ["BotDashboard", "DashboardWidget"]
