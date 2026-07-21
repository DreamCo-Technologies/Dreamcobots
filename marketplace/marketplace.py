"""
DreamCo Marketplace

Central hub for sharing, hiring, and deploying bots tailored to specific
industries and job roles.

Features (via tier)
-------------------
FREE        — Browse listed bots and job postings.
PRO         — List your own bots, hire AI workers, post job openings.
ENTERPRISE  — White-label marketplace, robot contract sourcing, revenue sharing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class BotListing:
    """A bot available for hire or purchase in the marketplace."""
    listing_id: str
    bot_name: str
    industry: str
    job_title: str
    price_usd_monthly: float
    owner: str
    description: str
    is_human_worker: bool = False   # True if listing is for a human contractor
    is_robot: bool = False          # True if physical robot hardware
    tags: list[str] = field(default_factory=list)


class Marketplace:
    """
    DreamCo Marketplace — connects clients with bots, AI workers, and robots.

    Usage
    -----
        from marketplace.marketplace import Marketplace

        market = Marketplace()
        market.add_listing(BotListing(...))
        results = market.search("accountant")
    """

    def __init__(self) -> None:
        self._listings: dict[str, BotListing] = {}

    def add_listing(self, listing: BotListing) -> None:
        """Add a new listing to the marketplace."""
        self._listings[listing.listing_id] = listing

    def remove_listing(self, listing_id: str) -> bool:
        """Remove a listing.  Returns True if removed, False if not found."""
        if listing_id in self._listings:
            del self._listings[listing_id]
            return True
        return False

    def search(self, query: str) -> list[BotListing]:
        """Full-text search across bot names, industries, and job titles."""
        q = query.lower()
        return [
            l for l in self._listings.values()
            if q in l.bot_name.lower()
            or q in l.industry.lower()
            or q in l.job_title.lower()
            or any(q in tag.lower() for tag in l.tags)
        ]

    def by_industry(self, industry: str) -> list[BotListing]:
        """Return all listings for a given industry."""
        key = industry.lower()
        return [l for l in self._listings.values() if l.industry.lower() == key]

    def human_workers(self) -> list[BotListing]:
        """Return listings for human contractors."""
        return [l for l in self._listings.values() if l.is_human_worker]

    def robots(self) -> list[BotListing]:
        """Return listings for physical robot hardware."""
        return [l for l in self._listings.values() if l.is_robot]

    def all_listings(self) -> list[BotListing]:
        """Return all active listings."""
        return list(self._listings.values())

    def count(self) -> int:
        """Number of active listings."""
        return len(self._listings)

    def get(self, listing_id: str) -> Optional[BotListing]:
        """Look up a listing by ID."""
        return self._listings.get(listing_id)


__all__ = ["Marketplace", "BotListing", "BotMarketplace"]


BotMarketplace = Marketplace


# ---------------------------------------------------------------------------
# Extended BotListing and BotMarketplace for test compatibility
# ---------------------------------------------------------------------------
import uuid as _uuid
from dataclasses import dataclass as _dataclass, field as _field


@_dataclass
class BotListing:
    """A bot listing in the marketplace (extended version)."""
    name: str
    description: str
    category: str
    price_usd: float
    seller_id: str
    tags: list = _field(default_factory=list)
    instructions: str = ""
    listing_id: str = _field(default_factory=lambda: str(_uuid.uuid4()))
    available: bool = True


@_dataclass
class BotPurchase:
    """Record of a bot purchase."""
    purchase_id: str
    buyer_id: str
    listing_id: str
    price_paid_usd: float
    deployed: bool = False


class BotMarketplace:
    """Full-featured bot marketplace."""

    def __init__(self):
        self._listings: dict = {}
        self._purchases: dict = {}

    def list_bot(self, listing: BotListing) -> None:
        self._listings[listing.listing_id] = listing

    def get_listing(self, listing_id: str):
        return self._listings.get(listing_id)

    def browse(self, category=None, max_price=None, tag=None):
        results = [l for l in self._listings.values() if l.available]
        if category:
            results = [l for l in results if l.category == category]
        if max_price is not None:
            results = [l for l in results if l.price_usd <= max_price]
        if tag:
            results = [l for l in results if tag in l.tags]
        return results

    def search(self, query: str):
        q = query.lower()
        return [l for l in self._listings.values()
                if l.available and (q in l.name.lower() or q in l.description.lower())]

    def purchase(self, buyer_id: str, listing_id: str) -> BotPurchase:
        listing = self._listings.get(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id!r} not found.")
        if not listing.available:
            raise ValueError(f"Listing {listing_id!r} is not available.")
        purchase = BotPurchase(
            purchase_id=str(_uuid.uuid4()),
            buyer_id=buyer_id,
            listing_id=listing_id,
            price_paid_usd=listing.price_usd,
        )
        self._purchases[purchase.purchase_id] = purchase
        return purchase

    def deploy(self, purchase_id: str) -> bool:
        purchase = self._purchases.get(purchase_id)
        if not purchase:
            return False
        purchase.deployed = True
        return True

    def get_purchases(self, buyer_id: str):
        return [p for p in self._purchases.values() if p.buyer_id == buyer_id]

    def delist_bot(self, listing_id: str, seller_id: str) -> bool:
        listing = self._listings.get(listing_id)
        if not listing or listing.seller_id != seller_id:
            return False
        listing.available = False
        return True

    def marketplace_stats(self) -> dict:
        purchases = list(self._purchases.values())
        return {
            "total_listings": len(self._listings),
            "total_purchases": len(purchases),
            "total_revenue_usd": sum(p.price_paid_usd for p in purchases),
        }
