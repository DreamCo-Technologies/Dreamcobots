"""
Monetization Engine — purchase transactions, upsells, and seller dashboards
for the DreamCo Bot Marketplace.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from datetime import datetime, timezone
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401

UPSELL_TYPES = [
    "PREMIUM_SKILL",
    "ADVANCED_API",
    "EXCLUSIVE_DATASET",
    "PRO_TEMPLATE",
    "ENTERPRISE_FEATURE",
]


class MonetizationEngine:
    """Purchase transactions, upsells, and seller revenue analytics."""

    def __init__(self, catalog=None) -> None:
        self._upsells: dict[str, dict] = {}
        self._upsells_by_listing: dict[str, list[str]] = {}
        self._transactions: list[dict] = []
        self._catalog = catalog

    # ------------------------------------------------------------------
    # Upsells
    # ------------------------------------------------------------------

    def create_upsell(
        self,
        listing_id: str,
        upsell_type: str,
        name: str,
        description: str,
        price_usd: float,
    ) -> dict:
        """Create an upsell offer linked to a bot listing."""
        if upsell_type not in UPSELL_TYPES:
            raise ValueError(f"Invalid upsell_type '{upsell_type}'. Must be one of {UPSELL_TYPES}.")
        if price_usd < 0:
            raise ValueError("price_usd must be non-negative.")

        upsell_id = str(uuid.uuid4())
        upsell = {
            "upsell_id": upsell_id,
            "listing_id": listing_id,
            "upsell_type": upsell_type,
            "name": name,
            "description": description,
            "price_usd": price_usd,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._upsells[upsell_id] = upsell
        self._upsells_by_listing.setdefault(listing_id, []).append(upsell_id)
        return upsell

    def get_upsells(self, listing_id: str) -> list:
        """Return all upsells for a given listing."""
        ids = self._upsells_by_listing.get(listing_id, [])
        return [self._upsells[uid] for uid in ids]

    # ------------------------------------------------------------------
    # Purchases
    # ------------------------------------------------------------------

    def purchase_bot(
        self,
        listing_id: str,
        buyer_id: str,
        platform_fee_pct: float = 0.15,
    ) -> dict:
        """Record a bot purchase and compute fee split."""
        if self._catalog is None:
            raise RuntimeError("MonetizationEngine requires a catalog to look up prices.")
        listing = self._catalog.get_listing(listing_id)
        gross = listing["price_usd"]
        return self._record_transaction(
            item_id=listing_id,
            item_type="bot",
            buyer_id=buyer_id,
            seller_id=listing["seller_id"],
            gross=gross,
            platform_fee_pct=platform_fee_pct,
        )

    def purchase_upsell(
        self,
        upsell_id: str,
        buyer_id: str,
        platform_fee_pct: float = 0.15,
    ) -> dict:
        """Record an upsell purchase and compute fee split."""
        if upsell_id not in self._upsells:
            raise KeyError(f"Upsell '{upsell_id}' not found.")
        upsell = self._upsells[upsell_id]
        listing_id = upsell["listing_id"]
        if self._catalog is None:
            raise RuntimeError("MonetizationEngine requires a catalog to look up seller.")
        listing = self._catalog.get_listing(listing_id)
        return self._record_transaction(
            item_id=upsell_id,
            item_type="upsell",
            buyer_id=buyer_id,
            seller_id=listing["seller_id"],
            gross=upsell["price_usd"],
            platform_fee_pct=platform_fee_pct,
        )

    # ------------------------------------------------------------------
    # Seller dashboard
    # ------------------------------------------------------------------

    def get_seller_dashboard(self, seller_id: str) -> dict:
        """Return aggregated revenue metrics for a seller."""
        seller_txns = [t for t in self._transactions if t["seller_id"] == seller_id]

        total_sales = len(seller_txns)
        total_revenue = sum(t["gross_amount"] for t in seller_txns)
        fees_paid = sum(t["platform_fee"] for t in seller_txns)
        net_earnings = sum(t["seller_earnings"] for t in seller_txns)

        # Top bots by earnings
        bot_earnings: dict[str, float] = {}
        for t in seller_txns:
            if t["item_type"] == "bot":
                bot_earnings[t["item_id"]] = bot_earnings.get(t["item_id"], 0.0) + t["seller_earnings"]
        top_bots = sorted(
            [{"listing_id": k, "earnings": v} for k, v in bot_earnings.items()],
            key=lambda x: x["earnings"],
            reverse=True,
        )[:5]

        recent = sorted(seller_txns, key=lambda t: t["purchased_at"], reverse=True)[:10]

        return {
            "seller_id": seller_id,
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "platform_fees_paid": round(fees_paid, 2),
            "net_earnings": round(net_earnings, 2),
            "top_bots": top_bots,
            "recent_transactions": recent,
        }

    def get_revenue_projection(self, seller_id: str, months: int = 12) -> dict:
        """Project future revenue based on historical average monthly earnings."""
        dashboard = self.get_seller_dashboard(seller_id)
        seller_txns = [t for t in self._transactions if t["seller_id"] == seller_id]

        if not seller_txns:
            monthly_avg = 0.0
        else:
            # Determine number of distinct months in the data
            months_set: set = set()
            for t in seller_txns:
                dt = datetime.fromisoformat(t["purchased_at"])
                months_set.add((dt.year, dt.month))
            num_months = max(len(months_set), 1)
            monthly_avg = dashboard["net_earnings"] / num_months

        projected = round(monthly_avg * months, 2)
        return {
            "seller_id": seller_id,
            "projection_months": months,
            "monthly_avg_net": round(monthly_avg, 2),
            "projected_net_earnings": projected,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_transaction(
        self,
        item_id: str,
        item_type: str,
        buyer_id: str,
        seller_id: str,
        gross: float,
        platform_fee_pct: float,
    ) -> dict:
        platform_fee = round(gross * platform_fee_pct, 2)
        seller_earnings = round(gross - platform_fee, 2)
        txn = {
            "transaction_id": str(uuid.uuid4()),
            "item_id": item_id,
            "item_type": item_type,
            "listing_id": item_id if item_type == "bot" else self._upsells.get(item_id, {}).get("listing_id"),
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "gross_amount": gross,
            "platform_fee": platform_fee,
            "seller_earnings": seller_earnings,
            "purchased_at": datetime.now(timezone.utc).isoformat(),
        }
        self._transactions.append(txn)

        # Update purchase_count on the listing
        if self._catalog is not None and item_type == "bot":
            try:
                listing = self._catalog.get_listing(item_id)
                listing["purchase_count"] = listing.get("purchase_count", 0) + 1
            except KeyError:
                pass

        return txn
