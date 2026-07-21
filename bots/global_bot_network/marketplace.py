"""
Bot Marketplace — DreamCo Global Bot Communication Network.

Provides the infrastructure for buying, selling, and subscribing to bots
and bot modules within the DreamCo ecosystem.

Features implemented (Phase 1 / groundwork):
  - Bot / module listings (create, update, deactivate)
  - Purchase transactions (in-memory mock; Stripe integration-ready)
  - Subscription plans for premium bots
  - Earnings tracking per seller
  - Search & browse catalogue

Phase 2 hooks:
  - Real Stripe payment integration via bots.stripe_integration
  - Trusted-bot gating via VerificationSystem
  - Commission / royalty splits
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ListingType(Enum):
    BOT = "bot"
    MODULE = "module"
    TEMPLATE = "template"
    SUBSCRIPTION = "subscription"


class ListingStatus(Enum):
    ACTIVE = "active"
    SOLD_OUT = "sold_out"
    PAUSED = "paused"
    REMOVED = "removed"


class SubscriptionInterval(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class MarketplaceError(Exception):
    """Base exception for marketplace errors."""


class ListingNotFound(MarketplaceError):
    """Raised when a listing cannot be found."""


class InsufficientFunds(MarketplaceError):
    """Raised when a buyer does not have enough balance."""


class ListingUnavailable(MarketplaceError):
    """Raised when a listing is not in ACTIVE status."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class MarketplaceListing:
    """A bot, module, or template available in the marketplace."""

    listing_id: str
    seller_id: str
    title: str
    description: str
    listing_type: ListingType
    price_usd: float
    status: ListingStatus = ListingStatus.ACTIVE
    tags: list = field(default_factory=list)
    subscription_interval: Optional[SubscriptionInterval] = None
    requires_verification: bool = False
    total_sales: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "listing_id": self.listing_id,
            "seller_id": self.seller_id,
            "title": self.title,
            "description": self.description,
            "type": self.listing_type.value,
            "price_usd": self.price_usd,
            "status": self.status.value,
            "tags": list(self.tags),
            "subscription_interval": (
                self.subscription_interval.value
                if self.subscription_interval else None
            ),
            "requires_verification": self.requires_verification,
            "total_sales": self.total_sales,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Purchase:
    """Records a completed marketplace transaction."""

    purchase_id: str
    buyer_id: str
    seller_id: str
    listing_id: str
    amount_usd: float
    listing_type: ListingType
    subscription_interval: Optional[SubscriptionInterval] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "purchase_id": self.purchase_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "listing_id": self.listing_id,
            "amount_usd": self.amount_usd,
            "type": self.listing_type.value,
            "subscription_interval": (
                self.subscription_interval.value
                if self.subscription_interval else None
            ),
            "timestamp": self.timestamp,
        }


@dataclass
class UserWallet:
    """Simple in-memory wallet for marketplace transactions."""

    user_id: str
    balance_usd: float = 0.0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise MarketplaceError("Deposit amount must be positive.")
        self.balance_usd += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise MarketplaceError("Withdrawal amount must be positive.")
        if amount > self.balance_usd:
            raise InsufficientFunds(
                f"Insufficient funds: need ${amount:.2f}, have ${self.balance_usd:.2f}."
            )
        self.balance_usd -= amount

    def to_dict(self) -> dict:
        return {"user_id": self.user_id, "balance_usd": self.balance_usd}


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------

class BotMarketplace:
    """
    DreamCo bot marketplace — buy, sell, and subscribe to bots & modules.

    Usage::

        market = BotMarketplace()
        listing = market.create_listing(
            seller_id="user_seller",
            title="Finance Bot Pro",
            description="Advanced finance automation",
            listing_type=ListingType.BOT,
            price_usd=29.99,
        )
        market.deposit("user_buyer", 100.0)
        purchase = market.buy(listing.listing_id, buyer_id="user_buyer")
    """

    # Platform commission rate (10 %)
    COMMISSION_RATE = 0.10

    def __init__(self) -> None:
        self._listings: dict[str, MarketplaceListing] = {}
        self._purchases: list[Purchase] = []
        self._wallets: dict[str, UserWallet] = {}
        self._seller_earnings: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Listings
    # ------------------------------------------------------------------

    def create_listing(
        self,
        seller_id: str,
        title: str,
        description: str,
        listing_type: ListingType,
        price_usd: float,
        tags: Optional[list] = None,
        subscription_interval: Optional[SubscriptionInterval] = None,
        requires_verification: bool = False,
    ) -> MarketplaceListing:
        """Create a new marketplace listing."""
        listing_id = str(uuid.uuid4())
        listing = MarketplaceListing(
            listing_id=listing_id,
            seller_id=seller_id,
            title=title,
            description=description,
            listing_type=listing_type,
            price_usd=price_usd,
            tags=tags or [],
            subscription_interval=subscription_interval,
            requires_verification=requires_verification,
        )
        self._listings[listing_id] = listing
        return listing

    def update_listing(
        self,
        listing_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price_usd: Optional[float] = None,
        status: Optional[ListingStatus] = None,
        tags: Optional[list] = None,
    ) -> MarketplaceListing:
        """Update an existing listing."""
        listing = self._get_listing(listing_id)
        if title is not None:
            listing.title = title
        if description is not None:
            listing.description = description
        if price_usd is not None:
            listing.price_usd = price_usd
        if status is not None:
            listing.status = status
        if tags is not None:
            listing.tags = tags
        listing._touch()
        return listing

    def remove_listing(self, listing_id: str) -> None:
        """Mark a listing as removed."""
        listing = self._get_listing(listing_id)
        listing.status = ListingStatus.REMOVED
        listing._touch()

    def get_listing(self, listing_id: str) -> MarketplaceListing:
        """Return a listing by ID."""
        return self._get_listing(listing_id)

    def list_active(
        self,
        listing_type: Optional[ListingType] = None,
        query: Optional[str] = None,
        max_price: Optional[float] = None,
    ) -> list[dict]:
        """Browse active listings with optional filters."""
        results = [
            l for l in self._listings.values()
            if l.status == ListingStatus.ACTIVE
        ]
        if listing_type:
            results = [l for l in results if l.listing_type == listing_type]
        if max_price is not None:
            results = [l for l in results if l.price_usd <= max_price]
        if query:
            q = query.lower()
            results = [
                l for l in results
                if q in l.title.lower() or q in l.description.lower()
                or any(q in t.lower() for t in l.tags)
            ]
        return [l.to_dict() for l in results]

    # ------------------------------------------------------------------
    # Wallet management
    # ------------------------------------------------------------------

    def deposit(self, user_id: str, amount: float) -> UserWallet:
        """Add funds to a user's wallet."""
        wallet = self._get_or_create_wallet(user_id)
        wallet.deposit(amount)
        return wallet

    def get_balance(self, user_id: str) -> float:
        """Return a user's current balance."""
        return self._get_or_create_wallet(user_id).balance_usd

    # ------------------------------------------------------------------
    # Purchasing
    # ------------------------------------------------------------------

    def buy(
        self,
        listing_id: str,
        buyer_id: str,
    ) -> Purchase:
        """
        Purchase a listing.

        Deducts the price from the buyer's wallet and credits the seller
        (minus platform commission).

        Raises
        ------
        ListingUnavailable
            If the listing is not ACTIVE.
        InsufficientFunds
            If the buyer cannot cover the price.
        """
        listing = self._get_listing(listing_id)
        if listing.status != ListingStatus.ACTIVE:
            raise ListingUnavailable(
                f"Listing '{listing_id}' is not available (status: {listing.status.value})."
            )

        buyer_wallet = self._get_or_create_wallet(buyer_id)
        buyer_wallet.withdraw(listing.price_usd)

        commission = listing.price_usd * self.COMMISSION_RATE
        seller_amount = listing.price_usd - commission
        seller_wallet = self._get_or_create_wallet(listing.seller_id)
        seller_wallet.deposit(seller_amount)
        self._seller_earnings[listing.seller_id] = (
            self._seller_earnings.get(listing.seller_id, 0.0) + seller_amount
        )

        listing.total_sales += 1
        listing._touch()

        purchase = Purchase(
            purchase_id=str(uuid.uuid4()),
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            listing_id=listing_id,
            amount_usd=listing.price_usd,
            listing_type=listing.listing_type,
            subscription_interval=listing.subscription_interval,
        )
        self._purchases.append(purchase)
        return purchase

    # ------------------------------------------------------------------
    # Earnings & stats
    # ------------------------------------------------------------------

    def get_seller_earnings(self, seller_id: str) -> float:
        """Return total earnings (after commission) for a seller."""
        return self._seller_earnings.get(seller_id, 0.0)

    def get_purchase_history(self, user_id: str) -> list[dict]:
        """Return purchases made by *user_id*."""
        return [
            p.to_dict() for p in self._purchases if p.buyer_id == user_id
        ]

    def get_sales_history(self, seller_id: str) -> list[dict]:
        """Return sales made by *seller_id*."""
        return [
            p.to_dict() for p in self._purchases if p.seller_id == seller_id
        ]

    def get_stats(self) -> dict:
        """Return marketplace statistics."""
        active = sum(1 for l in self._listings.values() if l.status == ListingStatus.ACTIVE)
        return {
            "total_listings": len(self._listings),
            "active_listings": active,
            "total_purchases": len(self._purchases),
            "total_revenue_usd": sum(p.amount_usd for p in self._purchases),
            "commission_rate": self.COMMISSION_RATE,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_listing(self, listing_id: str) -> MarketplaceListing:
        if listing_id not in self._listings:
            raise ListingNotFound(f"Listing '{listing_id}' not found.")
        return self._listings[listing_id]

    def _get_or_create_wallet(self, user_id: str) -> UserWallet:
        if user_id not in self._wallets:
            self._wallets[user_id] = UserWallet(user_id=user_id)
        return self._wallets[user_id]
