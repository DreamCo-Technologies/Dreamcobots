"""
DreamCo Empire OS — Marketplace Module

Hub for browsing, purchasing, and deploying new bots, tools,
and integrations within the DreamCo ecosystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class ListingCategory(Enum):
    BOT = "bot"
    TOOL = "tool"
    INTEGRATION = "integration"
    TEMPLATE = "template"
    DATASET = "dataset"


class ListingStatus(Enum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    COMING_SOON = "coming_soon"
    RETIRED = "retired"


@dataclass
class MarketplaceListing:
    """A single item in the DreamCo marketplace."""
    listing_id: str
    name: str
    category: ListingCategory
    description: str
    price_usd: float
    seller: str = "DreamCo Official"
    status: ListingStatus = ListingStatus.AVAILABLE
    rating: float = 0.0
    reviews: int = 0
    purchases: int = 0
    tags: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Marketplace:
    """
    Marketplace — buy and sell bots, tools, and integrations.

    Tracks listings, purchases, ratings, and revenue generated
    through the marketplace channel.
    """

    def __init__(self) -> None:
        self._listings: dict[str, MarketplaceListing] = {}
        self._purchase_log: list = []
        self._total_revenue_usd: float = 0.0

    def add_listing(
        self,
        listing_id: str,
        name: str,
        category: ListingCategory,
        description: str,
        price_usd: float,
        seller: str = "DreamCo Official",
        tags: Optional[list] = None,
    ) -> dict:
        """Add a new listing to the marketplace."""
        listing = MarketplaceListing(
            listing_id=listing_id,
            name=name,
            category=category,
            description=description,
            price_usd=max(0.0, price_usd),
            seller=seller,
            tags=tags or [],
        )
        self._listings[listing_id] = listing
        return _listing_to_dict(listing)

    def purchase(self, listing_id: str, buyer: str) -> dict:
        """Record a purchase of a marketplace listing."""
        listing = self._get(listing_id)
        if listing.status != ListingStatus.AVAILABLE:
            raise ValueError(f"Listing '{listing_id}' is not available for purchase.")
        listing.purchases += 1
        self._total_revenue_usd += listing.price_usd
        entry = {
            "listing_id": listing_id,
            "name": listing.name,
            "buyer": buyer,
            "price_usd": listing.price_usd,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._purchase_log.append(entry)
        return entry

    def rate_listing(self, listing_id: str, rating: float) -> dict:
        """Submit a rating (1.0–5.0) for a listing."""
        listing = self._get(listing_id)
        if not (1.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0.")
        total = listing.rating * listing.reviews + rating
        listing.reviews += 1
        listing.rating = round(total / listing.reviews, 2)
        return {"listing_id": listing_id, "new_rating": listing.rating, "total_reviews": listing.reviews}

    def search(self, query: str = "", category: Optional[ListingCategory] = None) -> list:
        """Search listings by keyword and/or category."""
        results = list(self._listings.values())
        if category:
            results = [l for l in results if l.category == category]
        if query:
            q = query.lower()
            results = [l for l in results if q in l.name.lower() or q in l.description.lower()
                       or any(q in t.lower() for t in l.tags)]
        results.sort(key=lambda l: l.rating, reverse=True)
        return [_listing_to_dict(l) for l in results]

    def get_summary(self) -> dict:
        listings = list(self._listings.values())
        return {
            "total_listings": len(listings),
            "available": sum(1 for l in listings if l.status == ListingStatus.AVAILABLE),
            "total_purchases": sum(l.purchases for l in listings),
            "total_revenue_usd": round(self._total_revenue_usd, 2),
            "avg_rating": round(sum(l.rating for l in listings) / len(listings), 2) if listings else 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _get(self, listing_id: str) -> MarketplaceListing:
        if listing_id not in self._listings:
            raise KeyError(f"Listing '{listing_id}' not found.")
        return self._listings[listing_id]


def _listing_to_dict(l: MarketplaceListing) -> dict:
    return {
        "listing_id": l.listing_id,
        "name": l.name,
        "category": l.category.value,
        "description": l.description,
        "price_usd": l.price_usd,
        "seller": l.seller,
        "status": l.status.value,
        "rating": l.rating,
        "reviews": l.reviews,
        "purchases": l.purchases,
        "tags": l.tags,
        "created_at": l.created_at,
    }
