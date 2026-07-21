"""
Marketplace Catalog — bot listing, discovery, and rating engine for the
DreamCo Bot Marketplace.

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

# ---------------------------------------------------------------------------
# Bot categories
# ---------------------------------------------------------------------------

BOT_CATEGORIES = [
    "PRODUCTIVITY",
    "ANALYTICS",
    "ECOMMERCE",
    "CRM",
    "FINANCE",
    "HEALTHCARE",
    "EDUCATION",
    "ENTERTAINMENT",
    "LOGISTICS",
    "SECURITY",
    "MARKETING",
    "HR",
    "LEGAL",
    "REAL_ESTATE",
    "GAMING",
]

BOT_TYPES = ["standard", "premium", "enterprise", "white_label"]

STATUS_PENDING_REVIEW = "PENDING_REVIEW"
STATUS_ACTIVE = "ACTIVE"
STATUS_REJECTED = "REJECTED"
STATUS_DELISTED = "DELISTED"


class MarketplaceCatalog:
    """Bot listing, discovery, and rating engine for the Bot Marketplace."""

    def __init__(self) -> None:
        self._listings: dict[str, dict] = {}
        self._ratings: dict[str, list[dict]] = {}

    # ------------------------------------------------------------------
    # Listing management
    # ------------------------------------------------------------------

    def list_bot(
        self,
        seller_id: str,
        bot_name: str,
        category: str,
        description: str,
        price_usd: float,
        bot_type: str = "standard",
    ) -> dict:
        """Create a new bot listing (starts in PENDING_REVIEW)."""
        if category not in BOT_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of {BOT_CATEGORIES}.")
        if bot_type not in BOT_TYPES:
            raise ValueError(f"Invalid bot_type '{bot_type}'. Must be one of {BOT_TYPES}.")
        if price_usd < 0:
            raise ValueError("price_usd must be non-negative.")

        listing_id = str(uuid.uuid4())
        listing = {
            "listing_id": listing_id,
            "seller_id": seller_id,
            "bot_name": bot_name,
            "category": category,
            "description": description,
            "price_usd": price_usd,
            "bot_type": bot_type,
            "status": STATUS_PENDING_REVIEW,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "purchase_count": 0,
        }
        self._listings[listing_id] = listing
        self._ratings[listing_id] = []
        return listing

    def approve_listing(self, listing_id: str) -> dict:
        """Approve a pending listing, setting its status to ACTIVE."""
        listing = self._get_or_raise(listing_id)
        listing["status"] = STATUS_ACTIVE
        return listing

    def get_listing(self, listing_id: str) -> dict:
        """Return a single listing by ID."""
        return self._get_or_raise(listing_id)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def search_listings(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
    ) -> list:
        """Search active listings by keyword, category, and/or price ceiling."""
        results = [l for l in self._listings.values() if l["status"] == STATUS_ACTIVE]

        if query:
            q = query.lower()
            results = [
                l for l in results
                if q in l["bot_name"].lower() or q in l["description"].lower()
            ]
        if category:
            results = [l for l in results if l["category"] == category]
        if max_price is not None:
            results = [l for l in results if l["price_usd"] <= max_price]

        return results

    def get_featured_bots(self, n: int = 10) -> list:
        """Return the top-n highest-rated active listings."""
        active = [l for l in self._listings.values() if l["status"] == STATUS_ACTIVE]
        return sorted(active, key=lambda l: self._avg_rating(l["listing_id"]), reverse=True)[:n]

    def get_popular_bots(self, n: int = 10) -> list:
        """Return the top-n most-purchased active listings."""
        active = [l for l in self._listings.values() if l["status"] == STATUS_ACTIVE]
        return sorted(active, key=lambda l: l["purchase_count"], reverse=True)[:n]

    def get_new_arrivals(self, n: int = 10) -> list:
        """Return the n most recently created active listings."""
        active = [l for l in self._listings.values() if l["status"] == STATUS_ACTIVE]
        return sorted(active, key=lambda l: l["created_at"], reverse=True)[:n]

    # ------------------------------------------------------------------
    # Ratings
    # ------------------------------------------------------------------

    def rate_bot(
        self,
        listing_id: str,
        user_id: str,
        rating: int,
        review: str = "",
    ) -> dict:
        """Submit a rating (1–5) and optional review for a listing."""
        self._get_or_raise(listing_id)
        if not 1 <= rating <= 5:
            raise ValueError("rating must be between 1 and 5.")
        entry = {
            "user_id": user_id,
            "rating": rating,
            "review": review,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._ratings[listing_id].append(entry)
        return entry

    def get_bot_stats(self, listing_id: str) -> dict:
        """Return aggregate stats for a listing."""
        listing = self._get_or_raise(listing_id)
        ratings = self._ratings[listing_id]
        avg_rating = (sum(r["rating"] for r in ratings) / len(ratings)) if ratings else 0.0
        return {
            "listing_id": listing_id,
            "avg_rating": round(avg_rating, 2),
            "review_count": len(ratings),
            "purchase_count": listing["purchase_count"],
            "revenue_usd": listing["price_usd"] * listing["purchase_count"],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, listing_id: str) -> dict:
        if listing_id not in self._listings:
            raise KeyError(f"Listing '{listing_id}' not found.")
        return self._listings[listing_id]

    def _avg_rating(self, listing_id: str) -> float:
        ratings = self._ratings.get(listing_id, [])
        if not ratings:
            return 0.0
        return sum(r["rating"] for r in ratings) / len(ratings)
