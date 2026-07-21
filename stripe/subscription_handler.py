"""
SubscriptionHandler — Stripe subscription management for DreamCobots.

Handles:
  • Creating and retrieving Stripe customers + subscriptions.
  • Processing incoming Stripe webhook events.
  • Mapping Stripe subscription status to DreamCobots tier capabilities
    (free / pro / enterprise) driven by ``config/master_config.yaml``.

Usage
-----
    from stripe.subscription_handler import SubscriptionHandler

    handler = SubscriptionHandler(api_key="sk_test_...")

    # Create a new pro subscription
    sub = handler.create_subscription("cus_xxx", tier="pro")

    # Process a webhook payload
    result = handler.process_webhook(raw_body, stripe_signature)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional imports
# ---------------------------------------------------------------------------

try:
    # Import the real Stripe SDK from site-packages, bypassing the local
    # ``stripe/`` directory which would shadow it on sys.path.
    import importlib.util as _ilu
    import sys as _sys
    import os as _os

    _stripe_lib = None
    for _sp in _sys.path:
        _cand = _os.path.join(_sp, "stripe", "__init__.py")
        if _os.path.abspath(_cand) == _os.path.abspath(__file__.replace("subscription_handler.py", "__init__.py")):
            continue
        if _os.path.isfile(_cand):
            _spec = _ilu.spec_from_file_location(
                "_stripe_sdk_real", _cand,
                submodule_search_locations=[_os.path.dirname(_cand)],
            )
            if _spec and _spec.loader:
                _stripe_lib = _ilu.module_from_spec(_spec)
                _spec.loader.exec_module(_stripe_lib)  # type: ignore[union-attr]
            break
    if _stripe_lib is None:
        raise ImportError("Stripe SDK not found in site-packages")
    _STRIPE_AVAILABLE = True
except Exception:
    _stripe_lib = None  # type: ignore[assignment]
    _STRIPE_AVAILABLE = False

try:
    from config.config_manager import config as _master_config
except Exception:
    _master_config = None  # type: ignore[assignment]


def _cfg(key: str, default: Any) -> Any:
    if _master_config is not None:
        return _master_config.get(key, default)
    return default


# ---------------------------------------------------------------------------
# Tier capabilities
# ---------------------------------------------------------------------------

TIER_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "free": {
        "requests_per_month": 500,
        "models": ["gpt-3.5-turbo"],
        "concurrent_bots": 2,
        "price_monthly": 0.0,
    },
    "pro": {
        "requests_per_month": 10_000,
        "models": ["gpt-4", "dalle-3"],
        "concurrent_bots": 10,
        "price_monthly": 49.0,
    },
    "enterprise": {
        "requests_per_month": 999_999,
        "models": ["gpt-4-vision", "claude-3"],
        "concurrent_bots": 50,
        "price_monthly": 299.0,
    },
}


def _tier_capabilities(tier: str) -> Dict[str, Any]:
    """Return capabilities for *tier*, falling back to master config."""
    # Prefer live config values when available
    config_tiers: Dict[str, Any] = _cfg("tiers", {}) or {}
    if tier in config_tiers:
        return dict(config_tiers[tier])
    return dict(TIER_CAPABILITIES.get(tier.lower(), TIER_CAPABILITIES["free"]))


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class SubscriptionRecord:
    """In-memory record for a customer subscription."""

    customer_id: str
    subscription_id: str
    tier: str
    status: str  # active | past_due | canceled | trialing | …
    current_period_end: Optional[int] = None  # Unix timestamp
    created_at: str = ""
    capabilities: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(tz=timezone.utc).isoformat()
        if not self.capabilities:
            self.capabilities = _tier_capabilities(self.tier)

    @property
    def is_active(self) -> bool:
        return self.status in ("active", "trialing")


# ---------------------------------------------------------------------------
# SubscriptionHandler
# ---------------------------------------------------------------------------


class SubscriptionHandler:
    """
    Manages Stripe subscriptions and maps them to DreamCobots tiers.

    When ``api_key`` is not provided the handler falls back to the
    ``STRIPE_API_KEY`` environment variable.  If Stripe is unavailable the
    handler operates in *simulation mode* — all operations succeed but no
    real API calls are made.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> None:
        self._api_key = (
            api_key
            or os.getenv("STRIPE_API_KEY")
            or os.getenv("STRIPE_SECRET_KEY")
        )
        self._webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self._simulation = not _STRIPE_AVAILABLE or not self._api_key

        if _STRIPE_AVAILABLE and self._api_key:
            _stripe_lib.api_key = self._api_key  # type: ignore[union-attr]

        if self._simulation:
            logger.warning(
                "SubscriptionHandler running in simulation mode "
                "(Stripe SDK unavailable or no API key configured)."
            )

        # In-memory store: customer_id → SubscriptionRecord
        self._subscriptions: Dict[str, SubscriptionRecord] = {}

    # ------------------------------------------------------------------
    # Customer helpers
    # ------------------------------------------------------------------

    def get_or_create_customer(
        self, email: str, name: Optional[str] = None
    ) -> str:
        """Return an existing Stripe customer ID or create a new one."""
        if self._simulation:
            cid = "cus_sim_" + hashlib.md5(email.encode()).hexdigest()[:12]
            logger.info("[sim] customer %s for %s", cid, email)
            return cid

        customers = _stripe_lib.Customer.list(email=email, limit=1)  # type: ignore[union-attr]
        if customers.data:
            return customers.data[0].id

        customer = _stripe_lib.Customer.create(email=email, name=name or email)  # type: ignore[union-attr]
        return customer.id

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        tier: str = "free",
        price_id: Optional[str] = None,
    ) -> SubscriptionRecord:
        """
        Create a Stripe subscription for *customer_id* at the given *tier*.

        When *price_id* is not supplied the handler looks for
        ``STRIPE_PRICE_<TIER>`` environment variables (e.g.
        ``STRIPE_PRICE_PRO``).  In simulation mode a stub record is returned.
        """
        tier = tier.lower()
        capabilities = _tier_capabilities(tier)

        if self._simulation:
            sub_id = "sub_sim_" + hashlib.md5(
                f"{customer_id}:{tier}:{time.time()}".encode()
            ).hexdigest()[:12]
            record = SubscriptionRecord(
                customer_id=customer_id,
                subscription_id=sub_id,
                tier=tier,
                status="active",
                capabilities=capabilities,
            )
            self._subscriptions[customer_id] = record
            logger.info("[sim] subscription %s created for %s (tier=%s)", sub_id, customer_id, tier)
            return record

        effective_price_id = (
            price_id
            or os.getenv(f"STRIPE_PRICE_{tier.upper()}")
        )
        if not effective_price_id:
            raise ValueError(
                f"No price ID configured for tier '{tier}'. "
                f"Set STRIPE_PRICE_{tier.upper()} or pass price_id."
            )

        sub = _stripe_lib.Subscription.create(  # type: ignore[union-attr]
            customer=customer_id,
            items=[{"price": effective_price_id}],
        )
        record = SubscriptionRecord(
            customer_id=customer_id,
            subscription_id=sub.id,
            tier=tier,
            status=sub.status,
            current_period_end=sub.current_period_end,
            capabilities=capabilities,
        )
        self._subscriptions[customer_id] = record
        return record

    def cancel_subscription(self, customer_id: str) -> bool:
        """Cancel the active subscription for *customer_id*."""
        record = self._subscriptions.get(customer_id)
        if record is None:
            logger.warning("No subscription found for customer %s", customer_id)
            return False

        if not self._simulation:
            _stripe_lib.Subscription.delete(record.subscription_id)  # type: ignore[union-attr]

        record.status = "canceled"
        logger.info("Subscription %s canceled for %s", record.subscription_id, customer_id)
        return True

    def get_subscription(self, customer_id: str) -> Optional[SubscriptionRecord]:
        """Return the in-memory subscription record for *customer_id*."""
        return self._subscriptions.get(customer_id)

    def get_capabilities(self, customer_id: str) -> Dict[str, Any]:
        """Return the capabilities dict for *customer_id*'s active tier."""
        record = self._subscriptions.get(customer_id)
        if record and record.is_active:
            return record.capabilities
        return _tier_capabilities("free")

    # ------------------------------------------------------------------
    # Webhook processing
    # ------------------------------------------------------------------

    def process_webhook(
        self,
        raw_body: bytes,
        stripe_signature: str = "",
    ) -> Dict[str, Any]:
        """
        Validate and dispatch a Stripe webhook event.

        Returns a dict with ``event_type`` and ``handled`` keys.
        In simulation mode signature verification is skipped.
        """
        event: Dict[str, Any] = {}

        if not self._simulation and _STRIPE_AVAILABLE and self._webhook_secret:
            try:
                evt = _stripe_lib.Webhook.construct_event(  # type: ignore[union-attr]
                    raw_body, stripe_signature, self._webhook_secret
                )
                event = dict(evt)
            except Exception as exc:
                logger.error("Webhook verification failed: %s", exc)
                return {"event_type": "error", "handled": False, "error": str(exc)}
        else:
            try:
                event = json.loads(raw_body)
            except (json.JSONDecodeError, ValueError) as exc:
                return {"event_type": "error", "handled": False, "error": str(exc)}

        event_type: str = event.get("type", "")
        handled = self._dispatch_event(event_type, event.get("data", {}).get("object", {}))
        return {"event_type": event_type, "handled": handled}

    def _dispatch_event(self, event_type: str, obj: Dict[str, Any]) -> bool:
        """Route a webhook event to the appropriate handler."""
        handlers = {
            "customer.subscription.created": self._on_subscription_created,
            "customer.subscription.updated": self._on_subscription_updated,
            "customer.subscription.deleted": self._on_subscription_deleted,
            "invoice.payment_succeeded": self._on_payment_succeeded,
            "invoice.payment_failed": self._on_payment_failed,
        }
        handler = handlers.get(event_type)
        if handler:
            try:
                handler(obj)
                return True
            except Exception as exc:
                logger.exception("Error handling event %s: %s", event_type, exc)
        else:
            logger.debug("Unhandled Stripe event: %s", event_type)
        return False

    def _on_subscription_created(self, obj: Dict[str, Any]) -> None:
        cid = obj.get("customer", "")
        sub_id = obj.get("id", "")
        status = obj.get("status", "active")
        tier = self._infer_tier(obj)
        record = SubscriptionRecord(
            customer_id=cid,
            subscription_id=sub_id,
            tier=tier,
            status=status,
        )
        self._subscriptions[cid] = record
        logger.info("Subscription created: %s tier=%s", sub_id, tier)

    def _on_subscription_updated(self, obj: Dict[str, Any]) -> None:
        cid = obj.get("customer", "")
        record = self._subscriptions.get(cid)
        if record:
            record.status = obj.get("status", record.status)
            new_tier = self._infer_tier(obj)
            if new_tier != record.tier:
                record.tier = new_tier
                record.capabilities = _tier_capabilities(new_tier)
                logger.info("Subscription %s upgraded to %s", record.subscription_id, new_tier)

    def _on_subscription_deleted(self, obj: Dict[str, Any]) -> None:
        cid = obj.get("customer", "")
        record = self._subscriptions.get(cid)
        if record:
            record.status = "canceled"
            logger.info("Subscription %s deleted", record.subscription_id)

    def _on_payment_succeeded(self, obj: Dict[str, Any]) -> None:
        amount = obj.get("amount_paid", 0) / 100  # cents → dollars
        cid = obj.get("customer", "")
        logger.info("Payment succeeded: $%.2f from %s", amount, cid)

    def _on_payment_failed(self, obj: Dict[str, Any]) -> None:
        cid = obj.get("customer", "")
        logger.warning("Payment failed for customer %s", cid)
        record = self._subscriptions.get(cid)
        if record:
            record.status = "past_due"

    @staticmethod
    def _infer_tier(subscription_obj: Dict[str, Any]) -> str:
        """
        Try to infer tier from the Stripe subscription object metadata.

        Falls back to ``"free"`` when unable to determine tier.
        """
        metadata: Dict[str, Any] = subscription_obj.get("metadata", {}) or {}
        tier = metadata.get("tier", "").lower()
        if tier in ("free", "pro", "enterprise"):
            return tier

        # Attempt to infer from plan nickname
        items = subscription_obj.get("items", {}).get("data", [])
        for item in items:
            nickname = (item.get("plan", {}).get("nickname") or "").lower()
            for t in ("enterprise", "pro", "free"):
                if t in nickname:
                    return t

        return "free"

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> List[Dict[str, Any]]:
        """Return a list of all tracked subscription records."""
        return [
            {
                "customer_id": r.customer_id,
                "subscription_id": r.subscription_id,
                "tier": r.tier,
                "status": r.status,
                "is_active": r.is_active,
                "capabilities": r.capabilities,
            }
            for r in self._subscriptions.values()
        ]
