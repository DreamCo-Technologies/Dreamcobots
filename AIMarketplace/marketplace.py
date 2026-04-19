# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
AI Marketplace — Core Engine

Provides a product catalogue, subscription management, and SDK generation
for the DreamCobots AI Marketplace.

Usage
-----
    from AIMarketplace.marketplace import AIMarketplace, PricingTier

    market = AIMarketplace()
    product = market.add_product(
        name="DreamMimic Voice Bot",
        description="AI-powered TTS and voice cloning.",
        category="voice",
        pricing_tier=PricingTier.PRO,
        price_usd=29.99,
    )
    sub = market.subscribe(user_id="user_001", product_id=product["product_id"])
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PricingTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class Product:
    product_id: str
    name: str
    description: str
    category: str
    pricing_tier: PricingTier = PricingTier.FREE
    price_usd: float = 0.0
    sdk_languages: List[str] = field(default_factory=lambda: ["python"])
    tags: List[str] = field(default_factory=list)
    status: str = "available"

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "pricing_tier": self.pricing_tier.value,
            "price_usd": self.price_usd,
            "sdk_languages": self.sdk_languages,
            "tags": self.tags,
            "status": self.status,
        }


@dataclass
class Subscription:
    subscription_id: str
    user_id: str
    product_id: str
    tier: PricingTier
    status: str = "trial"
    payment_provider: str = "stripe"
    amount_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "tier": self.tier.value,
            "status": self.status,
            "payment_provider": self.payment_provider,
            "amount_usd": self.amount_usd,
        }


class AIMarketplace:
    """
    Central marketplace for DreamCobots products.

    Supports product listing, subscription management, and basic search.
    """

    def __init__(self) -> None:
        self._products: Dict[str, Product] = {}
        self._subscriptions: List[Subscription] = []

    def add_product(
        self,
        name: str,
        description: str,
        category: str,
        pricing_tier: PricingTier = PricingTier.FREE,
        price_usd: float = 0.0,
        sdk_languages: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """List a new bot product and return its serialised record."""
        product = Product(
            product_id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            category=category,
            pricing_tier=pricing_tier,
            price_usd=price_usd,
            sdk_languages=sdk_languages or ["python"],
            tags=tags or [],
        )
        self._products[product.product_id] = product
        return product.to_dict()

    def subscribe(
        self,
        user_id: str,
        product_id: str,
        tier: PricingTier = PricingTier.FREE,
        payment_provider: str = "stripe",
    ) -> Dict[str, Any]:
        """Create a subscription for *user_id* to *product_id*."""
        if product_id not in self._products:
            raise KeyError(f"Product '{product_id}' not found.")
        product = self._products[product_id]
        sub = Subscription(
            subscription_id=str(uuid.uuid4())[:8],
            user_id=user_id,
            product_id=product_id,
            tier=tier,
            payment_provider=payment_provider,
            amount_usd=product.price_usd,
        )
        self._subscriptions.append(sub)
        return sub.to_dict()

    def search(
        self,
        category: Optional[str] = None,
        tier: Optional[PricingTier] = None,
        max_price: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Search the catalogue with optional filters."""
        products = list(self._products.values())
        if category:
            products = [p for p in products if p.category == category]
        if tier:
            products = [p for p in products if p.pricing_tier == tier]
        if max_price is not None:
            products = [p for p in products if p.price_usd <= max_price]
        return [p.to_dict() for p in products]

    def list_products(self) -> List[Dict[str, Any]]:
        """Return all products."""
        return [p.to_dict() for p in self._products.values()]

    def list_subscriptions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return subscriptions, optionally filtered by user."""
        subs = self._subscriptions
        if user_id:
            subs = [s for s in subs if s.user_id == user_id]
        return [s.to_dict() for s in subs]
