# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Marketplace Builder Bot

Expands the AI Marketplace:

  Phase 1 — Foundation
    • Builds GUI-ready product listings and bot catalogue APIs.
    • Wires in Stripe/PayPal monetisation scaffold for tier subscriptions.
    • Generates Python and Node.js SDK stubs for external integrations.
    • Stamps milestones via TimestampButton.

  Phase 2 — Placeholders & Ideation
    • Scaffolds placeholder APIs for unexplored verticals (healthcare, education).
    • Logs marketplace bot ideas to bot_ideas_log.txt.

Adheres to the DreamCobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from core.timestamp_button import TimestampButton
from bots.builder_bots._shared import append_bot_ideas


# ---------------------------------------------------------------------------
# Enums / constants
# ---------------------------------------------------------------------------


class PricingTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    TRIAL = "trial"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class BotProduct:
    """A purchasable bot product listed in the marketplace."""

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
    """A user subscription to a bot product."""

    subscription_id: str
    user_id: str
    product_id: str
    tier: PricingTier
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    payment_provider: str = "stripe"   # stripe | paypal
    amount_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "tier": self.tier.value,
            "status": self.status.value,
            "payment_provider": self.payment_provider,
            "amount_usd": self.amount_usd,
        }


@dataclass
class SDKStub:
    """Represents a generated SDK stub for a bot product."""

    sdk_id: str
    product_id: str
    language: str   # python | nodejs
    package_name: str
    entry_point: str
    readme_snippet: str

    def to_dict(self) -> dict:
        return {
            "sdk_id": self.sdk_id,
            "product_id": self.product_id,
            "language": self.language,
            "package_name": self.package_name,
            "entry_point": self.entry_point,
            "readme_snippet": self.readme_snippet,
        }


# ---------------------------------------------------------------------------
# MarketplaceBuilderBot
# ---------------------------------------------------------------------------


class MarketplaceBuilderBot:
    """
    Builder bot that expands the AI Marketplace infrastructure.

    Parameters
    ----------
    timestamp_button : TimestampButton | None
        Shared milestone tracker.
    """

    bot_id = "marketplace_builder_bot"
    name = "Marketplace Builder Bot"
    category = "builder"

    PLACEHOLDER_TEMPLATES: List[str] = [
        "healthcare_api_marketplace_placeholder",
        "education_bot_marketplace_placeholder",
        "crm_integration_sdk_placeholder",
        "subscription_tier_management_placeholder",
        "bot_leasing_license_placeholder",
        "dynamic_pricing_engine_placeholder",
    ]

    BOT_IDEAS: List[str] = [
        "SubscriptionTierManagerBot — auto-manages user plan upgrades/downgrades",
        "BotLeasingBot — offers time-limited bot licenses with auto-expiry",
        "RevenueShareBot — splits marketplace revenue between creators automatically",
        "MarketplaceRecommenderBot — personalises bot suggestions based on usage",
        "WhiteLabelPackagerBot — repackages bots under custom branding for resellers",
        "APIGatewayBuilderBot — generates OpenAPI specs and rate-limited gateway for each bot",
        "HealthcareMarketplacePlaceholder — HIPAA-compliant bot listing for medical apps",
        "EduMarketplacePlaceholder — curriculum-aligned bot catalogue for EdTech",
    ]

    def __init__(self, timestamp_button: Optional[TimestampButton] = None) -> None:
        self._ts = timestamp_button or TimestampButton()
        self._products: Dict[str, BotProduct] = {}
        self._subscriptions: List[Subscription] = []
        self._sdks: List[SDKStub] = []

    # ------------------------------------------------------------------
    # Phase 1: Foundation — Product catalogue
    # ------------------------------------------------------------------

    def add_product(
        self,
        name: str,
        description: str,
        category: str,
        pricing_tier: PricingTier = PricingTier.FREE,
        price_usd: float = 0.0,
        sdk_languages: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> BotProduct:
        """List a new bot product in the marketplace."""
        product = BotProduct(
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
        self._ts.stamp(
            event="product_listed",
            detail=f"product={name} tier={pricing_tier.value}",
            bot=self.name,
        )
        return product

    def create_subscription(
        self,
        user_id: str,
        product_id: str,
        tier: PricingTier = PricingTier.FREE,
        payment_provider: str = "stripe",
    ) -> Subscription:
        """Create a subscription for a user to a bot product."""
        product = self._get_product(product_id)
        sub = Subscription(
            subscription_id=str(uuid.uuid4())[:8],
            user_id=user_id,
            product_id=product_id,
            tier=tier,
            status=SubscriptionStatus.TRIAL,
            payment_provider=payment_provider,
            amount_usd=product.price_usd,
        )
        self._subscriptions.append(sub)
        self._ts.stamp(
            event="subscription_created",
            detail=f"user={user_id} product={product_id} tier={tier.value}",
            bot=self.name,
        )
        return sub

    def generate_sdk_stub(self, product_id: str, language: str = "python") -> SDKStub:
        """
        Generate a lightweight SDK stub for a listed product.

        Supports ``python`` and ``nodejs``.
        """
        if language not in ("python", "nodejs"):
            raise ValueError(f"Language '{language}' not supported. Choose 'python' or 'nodejs'.")

        product = self._get_product(product_id)

        if language == "python":
            pkg = product.name.lower().replace(" ", "_")
            entry = f"from {pkg} import {product.name.replace(' ', '')}"
            readme = f"pip install {pkg}\n\n{entry}\nbot = {product.name.replace(' ', '')}()\nbot.run({{}})"
        else:
            pkg = product.name.lower().replace(" ", "-")
            entry = f"const {{ {product.name.replace(' ', '')} }} = require('{pkg}');"
            readme = f"npm install {pkg}\n\n{entry}\nconst bot = new {product.name.replace(' ', '')}();\nawait bot.run({{}});"

        stub = SDKStub(
            sdk_id=str(uuid.uuid4())[:8],
            product_id=product_id,
            language=language,
            package_name=pkg,
            entry_point=entry,
            readme_snippet=readme,
        )
        self._sdks.append(stub)
        self._ts.stamp(
            event="sdk_stub_generated",
            detail=f"product={product_id} lang={language}",
            bot=self.name,
        )
        return stub

    def list_products(
        self, category: Optional[str] = None, tier: Optional[PricingTier] = None
    ) -> List[Dict[str, Any]]:
        """Return marketplace products, optionally filtered."""
        products = self._products.values()
        if category:
            products = [p for p in products if p.category == category]
        if tier:
            products = [p for p in products if p.pricing_tier == tier]
        return [p.to_dict() for p in products]

    # ------------------------------------------------------------------
    # Phase 2: Placeholders & ideation
    # ------------------------------------------------------------------

    def generate_placeholders(self) -> List[str]:
        """Return scaffold template names for future marketplace verticals."""
        self._ts.stamp(
            event="marketplace_placeholders_generated",
            detail=f"{len(self.PLACEHOLDER_TEMPLATES)} templates",
            bot=self.name,
        )
        return list(self.PLACEHOLDER_TEMPLATES)

    def log_bot_ideas(self, log_path: str = "bot_ideas_log.txt") -> None:
        """Append marketplace bot ideas to bot_ideas_log.txt."""
        append_bot_ideas(log_path, self.name, self.BOT_IDEAS)
        self._ts.stamp(event="bot_ideas_logged", detail=f"section={self.name}", bot=self.name)

    # ------------------------------------------------------------------
    # Unified run()
    # ------------------------------------------------------------------

    def run(self, task: dict | None = None) -> dict:
        """Execute the full builder lifecycle for the marketplace."""
        task = task or {}

        # Phase 1 — list sample products and generate SDK stubs
        product = self.add_product(
            name="DreamMimic Voice Bot",
            description="AI-powered voice synthesis and cloning bot.",
            category="voice",
            pricing_tier=PricingTier.PRO,
            price_usd=29.99,
            sdk_languages=["python", "nodejs"],
            tags=["voice", "ai", "tts"],
        )
        py_sdk = self.generate_sdk_stub(product.product_id, language="python")
        js_sdk = self.generate_sdk_stub(product.product_id, language="nodejs")
        sub = self.create_subscription(
            user_id=task.get("demo_user", "demo_user_001"),
            product_id=product.product_id,
            tier=PricingTier.FREE,
        )

        # Phase 2
        placeholders = self.generate_placeholders()
        self.log_bot_ideas(task.get("ideas_log", "bot_ideas_log.txt"))

        return {
            "status": "success",
            "bot": self.name,
            "product": product.to_dict(),
            "python_sdk": py_sdk.to_dict(),
            "nodejs_sdk": js_sdk.to_dict(),
            "subscription": sub.to_dict(),
            "placeholders": placeholders,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_product(self, product_id: str) -> BotProduct:
        if product_id not in self._products:
            raise KeyError(f"Product '{product_id}' not found.")
        return self._products[product_id]
