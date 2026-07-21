"""
DreamCo Stripe Billing — Subscription tier management with Stripe integration.

Provides a StripeBillingService that handles subscription creation, upgrades,
cancellations, and webhook event processing.

Environment variables
---------------------
STRIPE_API_KEY            Your Stripe secret key (sk_live_... or sk_test_...)
STRIPE_WEBHOOK_SECRET     Webhook signing secret (whsec_...)

When STRIPE_API_KEY is not set the service runs in **simulation mode**,
returning synthetic responses without calling Stripe APIs.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Optional Stripe import — graceful simulation mode
# ---------------------------------------------------------------------------

try:
    import stripe as _stripe  # type: ignore[import]
    _STRIPE_AVAILABLE = True
except ImportError:
    _stripe = None  # type: ignore[assignment]
    _STRIPE_AVAILABLE = False

_API_KEY: Optional[str] = os.environ.get("STRIPE_API_KEY")
_WEBHOOK_SECRET: Optional[str] = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Map tier names to monthly Stripe price IDs (override via env)
STRIPE_PRICE_IDS: Dict[str, str] = {
    "pro": os.environ.get("STRIPE_PRICE_PRO", "price_pro_monthly"),
    "enterprise": os.environ.get("STRIPE_PRICE_ENTERPRISE", "price_enterprise_monthly"),
}

TIER_PRICES_USD: Dict[str, float] = {
    "free": 0.0,
    "pro": 29.0,
    "enterprise": 499.0,
}


# ---------------------------------------------------------------------------
# Billing Service
# ---------------------------------------------------------------------------


class StripeBillingService:
    """
    Handles Stripe subscription lifecycles.

    When Stripe is unavailable or STRIPE_API_KEY is unset, all methods
    return simulation responses so the rest of the system keeps working.

    Parameters
    ----------
    simulation_mode : bool
        Force simulation even if the Stripe library is installed.
    """

    def __init__(self, simulation_mode: bool = False) -> None:
        self._simulation = simulation_mode or not _API_KEY or not _STRIPE_AVAILABLE
        if not self._simulation and _stripe is not None:
            _stripe.api_key = _API_KEY

        # In-memory ledger for simulation / testing
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._revenue_log: list = []

    # ------------------------------------------------------------------
    # Customer management
    # ------------------------------------------------------------------

    def create_customer(self, user_id: str, email: str) -> dict:
        """
        Create or retrieve a Stripe customer for *user_id*.

        Returns
        -------
        dict
            ``{ success, customer_id }``
        """
        if self._simulation:
            cid = f"cus_sim_{user_id[-8:]}"
            return {"success": True, "customer_id": cid, "simulation": True}

        try:
            customer = _stripe.Customer.create(
                email=email,
                metadata={"dreamco_user_id": user_id},
            )
            return {"success": True, "customer_id": customer.id}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        tier: str,
        user_id: str = "",
    ) -> dict:
        """
        Create a Stripe subscription for *customer_id* at *tier*.

        Returns
        -------
        dict
            ``{ success, subscription_id, tier, amount_usd }``
        """
        if tier not in STRIPE_PRICE_IDS and tier != "free":
            return {"success": False, "error": f"unknown tier: {tier}"}

        amount = TIER_PRICES_USD.get(tier, 0.0)

        if tier == "free" or self._simulation:
            sub_id = f"sub_sim_{user_id[-8:]}_{tier}"
            self._subscriptions[sub_id] = {
                "subscription_id": sub_id,
                "customer_id": customer_id,
                "tier": tier,
                "amount_usd": amount,
                "created_at": time.time(),
                "status": "active",
            }
            self._revenue_log.append(
                {"event": "subscription_created", "tier": tier, "amount": amount, "ts": time.time()}
            )
            return {
                "success": True,
                "subscription_id": sub_id,
                "tier": tier,
                "amount_usd": amount,
                "simulation": self._simulation,
            }

        try:
            price_id = STRIPE_PRICE_IDS[tier]
            sub = _stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata={"dreamco_tier": tier, "dreamco_user_id": user_id},
            )
            self._revenue_log.append(
                {"event": "subscription_created", "tier": tier, "amount": amount, "ts": time.time()}
            )
            return {
                "success": True,
                "subscription_id": sub.id,
                "tier": tier,
                "amount_usd": amount,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel a Stripe subscription.

        Returns
        -------
        dict
            ``{ success, subscription_id, status }``
        """
        if self._simulation:
            if subscription_id in self._subscriptions:
                self._subscriptions[subscription_id]["status"] = "cancelled"
            return {"success": True, "subscription_id": subscription_id, "status": "cancelled"}

        try:
            sub = _stripe.Subscription.delete(subscription_id)
            return {"success": True, "subscription_id": sub.id, "status": sub.status}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def upgrade_subscription(
        self,
        subscription_id: str,
        new_tier: str,
        user_id: str = "",
    ) -> dict:
        """
        Upgrade an existing subscription to *new_tier*.

        Returns
        -------
        dict
            ``{ success, subscription_id, old_tier, new_tier }``
        """
        if self._simulation:
            old = self._subscriptions.get(subscription_id, {})
            old_tier = old.get("tier", "unknown")
            self._subscriptions[subscription_id] = {
                **old,
                "tier": new_tier,
                "amount_usd": TIER_PRICES_USD.get(new_tier, 0.0),
                "status": "active",
            }
            return {
                "success": True,
                "subscription_id": subscription_id,
                "old_tier": old_tier,
                "new_tier": new_tier,
            }

        if new_tier not in STRIPE_PRICE_IDS:
            return {"success": False, "error": f"unknown tier: {new_tier}"}

        try:
            sub = _stripe.Subscription.retrieve(subscription_id)
            _stripe.Subscription.modify(
                subscription_id,
                items=[{"id": sub["items"]["data"][0]["id"], "price": STRIPE_PRICE_IDS[new_tier]}],
                metadata={"dreamco_tier": new_tier, "dreamco_user_id": user_id},
                proration_behavior="always_invoice",
            )
            return {
                "success": True,
                "subscription_id": subscription_id,
                "new_tier": new_tier,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Webhook processing
    # ------------------------------------------------------------------

    def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """
        Verify and process a Stripe webhook event.

        Returns
        -------
        dict
            ``{ success, event_type }`` or ``{ error }``.
        """
        if self._simulation:
            return {"success": True, "event_type": "simulation", "simulation": True}

        if not _WEBHOOK_SECRET:
            return {"success": False, "error": "STRIPE_WEBHOOK_SECRET not configured"}

        try:
            event = _stripe.Webhook.construct_event(payload, sig_header, _WEBHOOK_SECRET)
        except Exception as exc:
            return {"success": False, "error": f"webhook verification failed: {exc}"}

        event_type = event["type"]
        if event_type == "customer.subscription.updated":
            pass  # handle tier change
        elif event_type == "invoice.payment_succeeded":
            data = event["data"]["object"]
            self._revenue_log.append(
                {"event": "payment_succeeded", "amount": data.get("amount_paid", 0) / 100, "ts": time.time()}
            )
        elif event_type == "customer.subscription.deleted":
            pass  # handle cancellation

        return {"success": True, "event_type": event_type}

    # ------------------------------------------------------------------
    # Revenue reporting
    # ------------------------------------------------------------------

    def revenue_summary(self) -> dict:
        """
        Return an aggregate revenue summary.

        Returns
        -------
        dict
            ``{ total_revenue_usd, total_subscriptions, revenue_log_count }``
        """
        total = sum(
            e.get("amount", 0)
            for e in self._revenue_log
            if e.get("event") in ("subscription_created", "payment_succeeded")
        )
        active_subs = sum(
            1 for s in self._subscriptions.values() if s.get("status") == "active"
        )
        return {
            "total_revenue_usd": round(total, 2),
            "active_subscriptions": active_subs,
            "total_subscriptions": len(self._subscriptions),
            "revenue_log_count": len(self._revenue_log),
            "simulation_mode": self._simulation,
        }
