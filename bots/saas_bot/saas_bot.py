"""
SaaS Bot

Manages SaaS customer subscriptions with full Stripe integration, including
creating and canceling subscriptions, handling upgrade/downgrade flows, and
processing real-time webhook events (cancellations, upgrades, renewals).

Tier-aware:
  - BASIC:        Monthly billing only, 5-day free trial.
  - PROFESSIONAL: Monthly + annual billing, subscription webhooks.
  - ENTERPRISE:   All features, white-label, dedicated support.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bots.saas_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_STRIPE_SUBSCRIPTIONS,
    FEATURE_SUBSCRIPTION_WEBHOOKS,
    FEATURE_ANNUAL_BILLING,
    FEATURE_TRIAL_PERIOD,
    FEATURE_USAGE_ANALYTICS,
    FEATURE_MULTI_USER,
)
from bots.stripe_integration.stripe_client import StripeClient, StripeClientError
from bots.stripe_integration.webhook_handler import (
    StripeWebhookHandler,
    WebhookEvent,
)
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SaasBotError(Exception):
    """Base exception for SaaS Bot errors."""


class SaasBotTierError(SaasBotError):
    """Raised when a feature requires a higher tier."""


# ---------------------------------------------------------------------------
# Subscription record
# ---------------------------------------------------------------------------

@dataclass
class Subscription:
    """Tracks a customer's SaaS subscription."""

    subscription_id: str = field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:12]}")
    customer_id: str = ""
    customer_email: str = ""
    stripe_subscription_id: str = ""
    stripe_customer_id: str = ""
    tier: Tier = Tier.BASIC
    billing_interval: str = "monthly"
    status: str = "active"
    trial_days: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    current_period_end: Optional[int] = None
    canceled_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Main SaaS bot
# ---------------------------------------------------------------------------

class SaasBot:
    """
    Tier-aware SaaS subscription management bot with Stripe integration.

    Parameters
    ----------
    tier : Tier
        Bot operator's own subscription tier.
    stripe_client : StripeClient | None
        Optional injected StripeClient.
    webhook_handler : StripeWebhookHandler | None
        Optional injected webhook handler.
    """

    # Default trial period per tier (days)
    DEFAULT_TRIAL_DAYS = {Tier.BASIC: 7, Tier.PROFESSIONAL: 14, Tier.ENTERPRISE: 30}

    def __init__(
        self,
        tier: Tier = Tier.BASIC,
        stripe_client: Optional[StripeClient] = None,
        webhook_handler: Optional[StripeWebhookHandler] = None,
    ) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._stripe = stripe_client or StripeClient()
        self._webhook_handler = webhook_handler or StripeWebhookHandler(
            client=self._stripe, verify_signatures=False
        )
        self._subscriptions: dict[str, Subscription] = {}
        self._setup_default_webhook_handlers()

    # ------------------------------------------------------------------
    # Webhook auto-handlers
    # ------------------------------------------------------------------

    def _setup_default_webhook_handlers(self) -> None:
        """Register built-in handlers for common Stripe subscription events."""

        @self._webhook_handler.on("customer.subscription.deleted")
        def _on_canceled(event: WebhookEvent) -> None:
            stripe_sub_id = event.data.get("id", "")
            for sub in self._subscriptions.values():
                if sub.stripe_subscription_id == stripe_sub_id:
                    sub.status = "canceled"
                    sub.canceled_at = datetime.now(timezone.utc).isoformat()
                    break

        @self._webhook_handler.on("customer.subscription.updated")
        def _on_updated(event: WebhookEvent) -> None:
            stripe_sub_id = event.data.get("id", "")
            new_status = event.data.get("status", "")
            for sub in self._subscriptions.values():
                if sub.stripe_subscription_id == stripe_sub_id and new_status:
                    sub.status = new_status
                    break

        @self._webhook_handler.on("invoice.payment_succeeded")
        def _on_payment_ok(event: WebhookEvent) -> None:
            stripe_sub_id = event.data.get("subscription", "")
            for sub in self._subscriptions.values():
                if sub.stripe_subscription_id == stripe_sub_id:
                    sub.status = "active"
                    break

        @self._webhook_handler.on("invoice.payment_failed")
        def _on_payment_failed(event: WebhookEvent) -> None:
            stripe_sub_id = event.data.get("subscription", "")
            for sub in self._subscriptions.values():
                if sub.stripe_subscription_id == stripe_sub_id:
                    sub.status = "past_due"
                    break

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            msg = f"Feature '{feature}' requires a higher tier."
            if upgrade:
                msg += f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly:.0f}/mo)."
            raise SaasBotTierError(msg)

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_email: str,
        billing_interval: str = "monthly",
        trial_days: Optional[int] = None,
        customer_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Subscription:
        """
        Create a new SaaS subscription for a customer.

        Parameters
        ----------
        customer_email : str
            Customer's email address.
        billing_interval : str
            ``"monthly"`` or ``"annual"``.
        trial_days : int | None
            Override the default free trial period.
        customer_id : str | None
            Internal customer identifier.
        metadata : dict | None
            Extra metadata to attach to the Stripe subscription.

        Returns
        -------
        Subscription
            The created subscription record.
        """
        self._require_feature(FEATURE_STRIPE_SUBSCRIPTIONS)

        if billing_interval == "annual":
            self._require_feature(FEATURE_ANNUAL_BILLING)
            price_id = self.config.stripe_annual_price_id
        else:
            price_id = self.config.stripe_monthly_price_id

        if trial_days is None:
            trial_days = (
                self.DEFAULT_TRIAL_DAYS[self.tier]
                if self.config.has_feature(FEATURE_TRIAL_PERIOD)
                else 0
            )

        # Create Stripe customer
        stripe_customer = self._stripe.create_customer(
            email=customer_email,
            name=customer_id,
        )

        # Create Stripe subscription
        stripe_sub = self._stripe.create_subscription(
            customer_id=stripe_customer["id"],
            price_id=price_id,
            trial_days=trial_days,
            metadata=metadata or {"bot": "saas_bot", "tier": self.tier.value},
        )

        sub = Subscription(
            customer_id=customer_id or f"cust_{uuid.uuid4().hex[:8]}",
            customer_email=customer_email,
            stripe_subscription_id=stripe_sub["id"],
            stripe_customer_id=stripe_customer["id"],
            tier=self.tier,
            billing_interval=billing_interval,
            status=stripe_sub.get("status", "active"),
            trial_days=trial_days,
            current_period_end=stripe_sub.get("current_period_end"),
        )

        self._subscriptions[sub.subscription_id] = sub
        return sub

    def cancel_subscription(self, subscription_id: str) -> Subscription:
        """
        Cancel a subscription immediately.

        Parameters
        ----------
        subscription_id : str
            Internal subscription ID.

        Returns
        -------
        Subscription
            Updated subscription with ``status="canceled"``.
        """
        self._require_feature(FEATURE_STRIPE_SUBSCRIPTIONS)

        if subscription_id not in self._subscriptions:
            raise SaasBotError(f"Subscription '{subscription_id}' not found.")

        sub = self._subscriptions[subscription_id]
        self._stripe.cancel_subscription(sub.stripe_subscription_id)
        sub.status = "canceled"
        sub.canceled_at = datetime.now(timezone.utc).isoformat()
        return sub

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Return a subscription by its internal ID."""
        return self._subscriptions.get(subscription_id)

    def list_subscriptions(
        self, status: Optional[str] = None
    ) -> list[Subscription]:
        """
        Return all subscriptions, optionally filtered by status.

        Parameters
        ----------
        status : str | None
            e.g. ``"active"``, ``"canceled"``, ``"past_due"``.
        """
        subs = list(self._subscriptions.values())
        if status:
            subs = [s for s in subs if s.status == status]
        return subs

    def upgrade_subscription(
        self, subscription_id: str, new_tier: Tier
    ) -> Subscription:
        """
        Upgrade an existing subscription to a higher tier.

        Parameters
        ----------
        subscription_id : str
            Internal subscription ID to upgrade.
        new_tier : Tier
            Target tier.

        Returns
        -------
        Subscription
            Updated subscription record.
        """
        self._require_feature(FEATURE_STRIPE_SUBSCRIPTIONS)

        if subscription_id not in self._subscriptions:
            raise SaasBotError(f"Subscription '{subscription_id}' not found.")

        sub = self._subscriptions[subscription_id]
        new_config = get_tier_config(new_tier)

        # Cancel old and create new in Stripe
        self._stripe.cancel_subscription(sub.stripe_subscription_id)
        stripe_sub = self._stripe.create_subscription(
            customer_id=sub.stripe_customer_id,
            price_id=new_config.stripe_monthly_price_id,
            metadata={"bot": "saas_bot", "upgraded_from": sub.tier.value},
        )

        sub.tier = new_tier
        sub.stripe_subscription_id = stripe_sub["id"]
        sub.status = stripe_sub.get("status", "active")
        sub.current_period_end = stripe_sub.get("current_period_end")
        return sub

    # ------------------------------------------------------------------
    # Webhook processing
    # ------------------------------------------------------------------

    def process_webhook(self, payload: bytes, sig_header: str = "") -> dict:
        """
        Process an incoming Stripe webhook payload.

        Parameters
        ----------
        payload : bytes
            Raw HTTP request body.
        sig_header : str
            ``Stripe-Signature`` header value.

        Returns
        -------
        dict
            ``received``, ``event_type``, ``event_id``.
        """
        self._require_feature(FEATURE_SUBSCRIPTION_WEBHOOKS)

        event = self._webhook_handler.dispatch(
            payload, sig_header, skip_verify=True
        )
        if event is None:
            return {"received": False, "event_type": None, "event_id": None}

        return {
            "received": True,
            "event_type": event.event_type,
            "event_id": event.event_id,
        }

    def register_webhook_handler(self, event_type: str, callback) -> None:
        """
        Register a custom callback for a Stripe event type.

        Parameters
        ----------
        event_type : str
            Stripe event type (e.g. ``"customer.subscription.deleted"``).
        callback : callable
            Function accepting a ``WebhookEvent`` argument.
        """
        self._require_feature(FEATURE_SUBSCRIPTION_WEBHOOKS)
        self._webhook_handler.register(event_type, callback)

    # ------------------------------------------------------------------
    # Usage analytics
    # ------------------------------------------------------------------

    def get_subscription_analytics(self) -> dict:
        """
        Return subscription analytics summary.

        Returns
        -------
        dict
            Counts by status and tier.
        """
        self._require_feature(FEATURE_USAGE_ANALYTICS)

        all_subs = list(self._subscriptions.values())
        by_status: dict[str, int] = {}
        by_tier: dict[str, int] = {}
        for sub in all_subs:
            by_status[sub.status] = by_status.get(sub.status, 0) + 1
            by_tier[sub.tier.value] = by_tier.get(sub.tier.value, 0) + 1

        monthly_revenue = sum(
            get_tier_config(s.tier).price_usd_monthly
            for s in all_subs
            if s.status == "active"
        )

        return {
            "total_subscriptions": len(all_subs),
            "active": by_status.get("active", 0),
            "canceled": by_status.get("canceled", 0),
            "past_due": by_status.get("past_due", 0),
            "trialing": by_status.get("trialing", 0),
            "by_tier": by_tier,
            "estimated_monthly_revenue_usd": round(monthly_revenue, 2),
        }

    # ------------------------------------------------------------------
    # Tier description
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return a human-readable tier summary."""
        cfg = self.config
        users = "Unlimited" if cfg.is_unlimited_users() else str(cfg.max_users)
        lines = [
            f"SaaS Bot — {cfg.name} Tier",
            f"  Price    : ${cfg.price_usd_monthly:.2f}/month",
            f"  Users    : {users}",
            f"  Support  : {cfg.support_level}",
            f"  Features : {', '.join(cfg.features)}",
        ]
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(
                f"  Upgrade  : {upgrade.name} (${upgrade.price_usd_monthly:.0f}/mo)"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        BuddyAI-compatible chat interface.

        Returns
        -------
        dict
            ``response``, ``bot_name``, ``tier``.
        """
        msg_lower = message.lower()

        if "tier" in msg_lower or "plan" in msg_lower:
            response = self.describe_tier()
        elif "subscri" in msg_lower and ("cancel" in msg_lower or "stop" in msg_lower):
            response = (
                "To cancel a subscription, call cancel_subscription(subscription_id). "
                "The cancellation takes effect immediately."
            )
        elif "subscri" in msg_lower:
            count = len(self._subscriptions)
            active = len([s for s in self._subscriptions.values() if s.status == "active"])
            response = (
                f"You have {count} subscription(s) total, {active} active. "
                "Use create_subscription(email) to add a new subscriber."
            )
        elif "webhook" in msg_lower:
            if self.config.has_feature(FEATURE_SUBSCRIPTION_WEBHOOKS):
                response = (
                    "Webhook processing is active. Supported events include: "
                    "subscription created/updated/deleted, invoice payment succeeded/failed."
                )
            else:
                response = "Webhook processing is available on Professional and Enterprise tiers."
        elif "revenue" in msg_lower or "analytic" in msg_lower:
            if self.config.has_feature(FEATURE_USAGE_ANALYTICS):
                analytics = self.get_subscription_analytics()
                response = (
                    f"Active subscriptions: {analytics['active']}, "
                    f"estimated MRR: ${analytics['estimated_monthly_revenue_usd']:.2f}."
                )
            else:
                response = "Analytics are available on Professional and Enterprise tiers."
        elif "stripe" in msg_lower:
            response = (
                "Stripe subscription management is fully integrated. "
                "Subscriptions are created, updated, and canceled via the Stripe API."
            )
        else:
            response = (
                f"Hello from SaaS Bot ({self.config.name} tier)! "
                "I manage SaaS subscriptions with Stripe. "
                "Ask about plans, subscriptions, webhooks, or analytics."
            )

        return {
            "response": response,
            "bot_name": "saas_bot",
            "tier": self.tier.value,
        }
