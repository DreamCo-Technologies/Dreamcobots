"""
DreamCo Control Plane — Revenue Gateway
=========================================

Tracks ARR/MRR figures and subscription-tier distribution for the Revenue
Operations dashboard section.

In production this would be backed by Stripe / billing DB queries.  Here it
provides a clean interface that can be populated by billing event handlers or
injected in tests.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class RevenueGateway:
    """
    Dashboard gateway for revenue / billing metrics.

    Revenue figures are injected via :meth:`record_subscription` and
    :meth:`set_arr` / :meth:`set_mrr`.  A production implementation would
    query the billing database directly.
    """

    def __init__(self) -> None:
        self._arr: float = 0.0
        self._mrr: float = 0.0
        self._subscriptions: Dict[str, Dict[str, Any]] = {}  # customer_id → record
        self._datasets_sold: int = 0
        self._updated_at: float = time.time()

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------

    def set_arr(self, arr: float) -> None:
        """Set the current Annual Recurring Revenue figure."""
        self._arr = arr
        self._updated_at = time.time()

    def set_mrr(self, mrr: float) -> None:
        """Set the current Monthly Recurring Revenue figure."""
        self._mrr = mrr
        self._updated_at = time.time()

    def record_subscription(
        self,
        customer_id: str,
        tier: str,
        mrr_contribution: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record or update a customer subscription."""
        self._subscriptions[customer_id] = {
            "customer_id": customer_id,
            "tier": tier,
            "mrr_contribution": mrr_contribution,
            "recorded_at": time.time(),
            "metadata": metadata or {},
        }
        self._updated_at = time.time()

    def increment_datasets_sold(self, count: int = 1) -> None:
        """Increment the datasets-sold counter."""
        self._datasets_sold += count
        self._updated_at = time.time()

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a revenue snapshot for the dashboard."""
        tier_distribution: Dict[str, int] = {}
        tier_mrr: Dict[str, float] = {}

        for sub in self._subscriptions.values():
            t = sub["tier"]
            tier_distribution[t] = tier_distribution.get(t, 0) + 1
            tier_mrr[t] = tier_mrr.get(t, 0.0) + sub["mrr_contribution"]

        total_customers = len(self._subscriptions)
        computed_mrr = sum(s["mrr_contribution"] for s in self._subscriptions.values())

        return {
            "arr": self._arr,
            "mrr": self._mrr if self._mrr else computed_mrr,
            "total_customers": total_customers,
            "tier_distribution": tier_distribution,
            "tier_mrr": {k: round(v, 2) for k, v in tier_mrr.items()},
            "datasets_sold": self._datasets_sold,
            "updated_at": self._updated_at,
            "snapshot_at": time.time(),
        }
