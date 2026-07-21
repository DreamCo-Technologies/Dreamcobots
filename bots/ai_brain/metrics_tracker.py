"""
Metrics Tracker — reads real metrics from data/leads.json and data/deals.json
to provide actual revenue and lead counts (replacing simulated/fake data).

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Default data paths
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
_DEFAULT_LEADS_PATH = os.path.join(_DATA_DIR, "leads.json")
_DEFAULT_DEALS_PATH = os.path.join(_DATA_DIR, "deals.json")

# Revenue per deal (default)
REVENUE_PER_DEAL_USD: float = 100.0


# ---------------------------------------------------------------------------
# Metrics Tracker
# ---------------------------------------------------------------------------

class MetricsTracker:
    """
    Reads real metrics from data files to power the Decision Engine.

    Replaces simulated/random metrics with actual counts from leads.json
    and deals.json.

    Parameters
    ----------
    leads_path : str, optional
        Path to the leads data file.
    deals_path : str, optional
        Path to the deals data file.
    revenue_per_deal : float
        Revenue credited per closed deal.
    """

    def __init__(
        self,
        leads_path: Optional[str] = None,
        deals_path: Optional[str] = None,
        revenue_per_deal: float = REVENUE_PER_DEAL_USD,
    ) -> None:
        self._leads_path = leads_path or _DEFAULT_LEADS_PATH
        self._deals_path = deals_path or _DEFAULT_DEALS_PATH
        self.revenue_per_deal = revenue_per_deal
        self._metrics_log: list[dict] = []

    # ------------------------------------------------------------------
    # Core metric readers (matching problem statement signatures)
    # ------------------------------------------------------------------

    def count_leads(self) -> int:
        """
        Count the number of leads in the leads data file.

        Returns 0 if the file does not exist or cannot be parsed.
        """
        try:
            with open(self._leads_path, encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return 0
                # Support both JSON array and JSONL (one JSON per line)
                if content.startswith("["):
                    data = json.loads(content)
                    return len(data) if isinstance(data, list) else 0
                # JSONL format
                lines = [l.strip() for l in content.splitlines() if l.strip()]
                return len(lines)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return 0

    def track_revenue(self) -> float:
        """
        Calculate total revenue from closed deals.

        Returns deals_count × revenue_per_deal. Returns 0.0 on file errors.
        """
        deals = 0
        try:
            with open(self._deals_path, encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, list):
                        deals = len(data)
                    elif isinstance(data, dict):
                        deals = 1
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return round(deals * self.revenue_per_deal, 2)

    def get_metrics(self) -> dict:
        """Return all current metrics as a dict."""
        leads = self.count_leads()
        revenue = self.track_revenue()
        snapshot = {
            "leads": leads,
            "revenue": revenue,
            "deals": int(round(revenue / self.revenue_per_deal)) if self.revenue_per_deal else 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._metrics_log.append(snapshot)
        return snapshot

    def get_metrics_history(self) -> list[dict]:
        """Return all previously collected metrics snapshots."""
        return list(self._metrics_log)

    def count_messages_sent(self, messages_path: Optional[str] = None) -> int:
        """Count sent messages from a messages log file."""
        path = messages_path or os.path.join(_DATA_DIR, "messages.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.loads(f.read())
                return len(data) if isinstance(data, list) else 0
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return 0

    def count_replies(self, replies_path: Optional[str] = None) -> int:
        """Count lead replies from a replies log file."""
        path = replies_path or os.path.join(_DATA_DIR, "replies.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.loads(f.read())
                return len(data) if isinstance(data, list) else 0
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return 0

    def count_deals_closed(self) -> int:
        """Count the number of closed deals."""
        revenue = self.track_revenue()
        return int(round(revenue / self.revenue_per_deal)) if self.revenue_per_deal else 0
