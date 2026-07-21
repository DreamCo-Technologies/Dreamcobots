"""
learning_dashboard.py — Interface for monitoring global AI learning.

Provides a text-based summary dashboard that aggregates and displays
key metrics from the Global Learning Matrix, ingestion pipeline, and
classifier service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DashboardPanel:
    """A single named panel in the learning dashboard."""

    title: str
    content: List[str] = field(default_factory=list)


class LearningDashboard:
    """
    Aggregates and renders a summary view of the global AI learning state.

    Parameters
    ----------
    title : str
        Dashboard title shown in the header.
    """

    def __init__(self, title: str = "DreamCo Global AI Learning Dashboard"):
        self.title = title
        self._panels: List[DashboardPanel] = []
        self._data: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, key: str, value: Any) -> None:
        """Store a named data value for display."""
        self._data[key] = value

    def add_panel(self, panel: DashboardPanel) -> None:
        """Add a custom panel to the dashboard."""
        self._panels.append(panel)

    def render(self) -> str:
        """
        Render the dashboard as a formatted string.

        Returns
        -------
        str
        """
        lines = [
            "=" * 60,
            f"  {self.title}",
            "=" * 60,
        ]

        for key, value in self._data.items():
            lines.append(f"  {key}: {value}")

        for panel in self._panels:
            lines.append("")
            lines.append(f"  [{panel.title}]")
            for row in panel.content:
                lines.append(f"    {row}")

        lines.append("=" * 60)
        output = "\n".join(lines)
        print(output)
        return output

    def summary(self) -> Dict[str, Any]:
        """Return the raw data dictionary."""
        return dict(self._data)

    def clear(self) -> None:
        """Clear all data and panels."""
        self._data = {}
        self._panels = []
