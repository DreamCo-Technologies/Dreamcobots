"""
Stripe Payment Bot — DreamCo Empire

A tier-aware Stripe payment integration bot.  Handles one-time checkouts,
subscription plans, coupon codes, invoices, webhook event processing,
Stripe Connect split payments, and revenue analytics.

All network calls are simulated; swap ``_stripe_api_call`` for real
``stripe`` SDK calls once you have a live API key.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

30 Revenue Use Cases
--------------------
 1. SaaS monthly subscription billing
 2. Lead-generation bot access fee (pay-per-lead)
 3. Real-estate deal report one-time purchase
 4. Fiverr-style gig payment gateway
 5. Digital product instant download checkout
 6. Affiliate commission payout (Connect)
 7. Token top-up for AI model usage
 8. Job-application bot per-application fee
 9. Crypto bot signal subscription
10. Car-flipping deal alert subscription
11. Government grant finder annual plan
12. Side-hustle course upsell checkout
13. White-label reseller seat licensing
14. Enterprise API key issuance payment
15. Marketplace bot listing fee
16. Revenue-share split (Stripe Connect)
17. Discount coupon for first-month promo
18. Invoice-based B2B billing cycle
19. Metered billing for high-volume API users
20. Dunning / retry logic for failed payments
21. Refund workflow for dissatisfied customers
22. Multi-currency checkout (USD/EUR/GBP)
23. Annual plan with discount applied
24. Upsell to ENTERPRISE on checkout success
25. Webhook handler for Stripe payment_intent events
26. Fraud Radar score integration (ENTERPRISE)
27. Custom receipt email trigger post-payment
28. Proration on mid-cycle tier upgrade
29. Revenue analytics dashboard export
30. Automated SLA-breach credit issuer
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.stripe_payment_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_CHECKOUT,
    FEATURE_SUBSCRIPTIONS,
    FEATURE_WEBHOOKS,
    FEATURE_REFUNDS,
    FEATURE_COUPONS,
    FEATURE_INVOICES,
    FEATURE_CONNECT,
    FEATURE_SPLIT_PAYMENTS,
    FEATURE_ANALYTICS,
    FEATURE_FRAUD_RADAR,
)

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "CAD", "AUD", "JPY", "MXN"}

# Mock FX rates (relative to USD)
_FX: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.36,
    "AUD": 1.53,
    "JPY": 149.50,
    "MXN": 17.15,
}

# Canonical plan catalogue (name → monthly price USD)
PLAN_CATALOGUE: dict[str, float] = {
    "lead_generator_starter": 29.0,
    "lead_generator_pro": 99.0,
    "lead_generator_enterprise": 299.0,
    "real_estate_starter": 29.0,
    "real_estate_pro": 99.0,
    "real_estate_enterprise": 299.0,
    "hustle_bot_starter": 29.0,
    "hustle_bot_pro": 99.0,
    "crypto_bot_starter": 29.0,
    "crypto_bot_pro": 99.0,
    "fiverr_bot_starter": 29.0,
    "fiverr_bot_pro": 99.0,
    "empire_enterprise": 299.0,
}


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class StripePaymentBotError(Exception):
    """Base exception for StripePaymentBot errors."""


class StripeTierError(StripePaymentBotError):
    """Raised when a feature is not available on the current tier."""


class StripeValidationError(StripePaymentBotError):
    """Raised on invalid input."""


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class StripePaymentBot:
    """
    Tier-aware Stripe Payment Bot.

    Provides checkout sessions, subscriptions, webhook processing,
    Stripe Connect split payments, coupons, invoices, and analytics.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    api_key : str, optional
        Stripe secret key (``sk_live_…`` or ``sk_test_…``).
        Defaults to the ``STRIPE_SECRET_KEY`` environment variable if
        not supplied.  When absent, all calls remain simulated.
    """

    def __init__(
        self,
        tier: Tier = Tier.STARTER,
        api_key: Optional[str] = None,
    ) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._api_key: str = api_key or os.environ.get("STRIPE_SECRET_KEY", "")

        # In-memory stores (replace with DB in production)
        self._checkouts: dict[str, dict] = {}
        self._subscriptions: dict[str, dict] = {}
        self._invoices: dict[str, dict] = {}
        self._refunds: dict[str, dict] = {}
        self._webhook_log: list[dict] = []
        self._connect_accounts: dict[str, dict] = {}
        self._payment_count: int = 0
        self._revenue_usd: float = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade
                else ""
            )
            raise StripeTierError(
                f"Feature '{feature}' is not available on the "
                f"{self._config.name} tier.{hint}"
            )

    @staticmethod
    def _new_id(prefix: str = "pi") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _validate_currency(self, currency: str) -> None:
        if currency.upper() not in SUPPORTED_CURRENCIES:
            raise StripeValidationError(
                f"Unsupported currency '{currency}'. "
                f"Supported: {sorted(SUPPORTED_CURRENCIES)}"
            )

    def _validate_amount(self, amount: float) -> None:
        if amount <= 0:
            raise StripeValidationError("Amount must be a positive number.")

    def _check_monthly_cap(self) -> None:
        cap = self._config.payments_per_month
        if cap is not None and self._payment_count >= cap:
            upgrade = get_upgrade_path(self.tier)
            hint = f" Upgrade to {upgrade.name}." if upgrade else ""
            raise StripeTierError(
                f"Monthly payment limit ({cap}) reached on "
                f"{self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # 1. Checkout Session (all tiers)
    # ------------------------------------------------------------------

    def create_checkout_session(
        self,
        amount: float,
        currency: str,
        product_name: str,
        customer_email: str,
        success_url: str = "https://dreamco.ai/success",
        cancel_url: str = "https://dreamco.ai/cancel",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Checkout session for a one-time payment.

        Parameters
        ----------
        amount : float
            Charge amount in the given currency.
        currency : str
            ISO 4217 currency code (e.g. "USD").
        product_name : str
            Name of the product or service being sold.
        customer_email : str
            Customer's email address.
        success_url : str
            URL to redirect to on payment success.
        cancel_url : str
            URL to redirect to on payment cancellation.
        metadata : dict, optional
            Arbitrary key-value metadata attached to the session.

        Returns
        -------
        dict
            Simulated Stripe CheckoutSession object.
        """
        self._require(FEATURE_CHECKOUT)
        self._validate_amount(amount)
        self._validate_currency(currency)
        self._check_monthly_cap()

        session_id = self._new_id("cs")
        fee_pct = self._config.platform_fee_pct / 100
        net_amount = round(amount * (1 - fee_pct), 2)

        session = {
            "id": session_id,
            "object": "checkout.session",
            "status": "open",
            "payment_status": "unpaid",
            "amount_total": int(amount * 100),  # Stripe uses cents
            "currency": currency.upper(),
            "customer_email": customer_email,
            "product_name": product_name,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "url": f"https://checkout.stripe.com/pay/{session_id}",
            "platform_fee_pct": self._config.platform_fee_pct,
            "net_amount_usd": net_amount,
            "metadata": metadata or {},
            "created_at": self._now(),
            "tier": self.tier.value,
        }
        self._checkouts[session_id] = session
        self._payment_count += 1

        # Convert to USD for revenue tracking
        rate = _FX.get(currency.upper(), 1.0)
        self._revenue_usd += net_amount / rate

        return session

    def confirm_checkout(self, session_id: str) -> dict:
        """
        Confirm a checkout session (simulate successful payment).

        Parameters
        ----------
        session_id : str
            The checkout session to confirm.

        Returns
        -------
        dict
            Updated session with ``payment_status = 'paid'``.
        """
        self._require(FEATURE_CHECKOUT)
        if session_id not in self._checkouts:
            raise StripeValidationError(f"Session '{session_id}' not found.")
        self._checkouts[session_id]["payment_status"] = "paid"
        self._checkouts[session_id]["status"] = "complete"
        self._checkouts[session_id]["confirmed_at"] = self._now()
        return dict(self._checkouts[session_id])

    # ------------------------------------------------------------------
    # 2. Subscriptions (GROWTH+)
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        interval: str = "monthly",
        trial_days: int = 0,
        coupon_id: Optional[str] = None,
    ) -> dict:
        """
        Create a recurring Stripe subscription.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.
        plan_id : str
            Plan identifier from ``PLAN_CATALOGUE``.
        interval : str
            Billing interval: ``'monthly'`` or ``'yearly'``.
        trial_days : int
            Free trial period in days (0 = no trial).
        coupon_id : str, optional
            Coupon code to apply (requires COUPONS feature).

        Returns
        -------
        dict
            Subscription record.
        """
        self._require(FEATURE_SUBSCRIPTIONS)

        if interval not in {"monthly", "yearly"}:
            raise StripeValidationError(f"Invalid interval '{interval}'.")

        amount = PLAN_CATALOGUE.get(plan_id, 29.0)
        if interval == "yearly":
            amount = round(amount * 10, 2)  # 2 months free on annual

        discount_pct = 0.0
        if coupon_id:
            self._require(FEATURE_COUPONS)
            discount_pct = self._apply_coupon(coupon_id)
            amount = round(amount * (1 - discount_pct / 100), 2)

        sub_id = self._new_id("sub")
        record = {
            "id": sub_id,
            "object": "subscription",
            "customer_id": customer_id,
            "plan_id": plan_id,
            "amount_usd": amount,
            "interval": interval,
            "status": "trialing" if trial_days > 0 else "active",
            "trial_days": trial_days,
            "coupon_applied": coupon_id,
            "discount_pct": discount_pct,
            "created_at": self._now(),
            "tier": self.tier.value,
        }
        self._subscriptions[sub_id] = record
        if not trial_days:
            self._revenue_usd += amount
        return record

    def cancel_subscription(self, sub_id: str) -> dict:
        """
        Cancel an active subscription immediately.

        Parameters
        ----------
        sub_id : str
            Subscription ID to cancel.

        Returns
        -------
        dict
            Updated subscription record.
        """
        self._require(FEATURE_SUBSCRIPTIONS)
        if sub_id not in self._subscriptions:
            raise StripeValidationError(f"Subscription '{sub_id}' not found.")
        self._subscriptions[sub_id]["status"] = "canceled"
        self._subscriptions[sub_id]["canceled_at"] = self._now()
        return dict(self._subscriptions[sub_id])

    def list_subscriptions(self, customer_id: str) -> list[dict]:
        """Return all subscriptions for a customer."""
        self._require(FEATURE_SUBSCRIPTIONS)
        return [
            dict(s)
            for s in self._subscriptions.values()
            if s["customer_id"] == customer_id
        ]

    # ------------------------------------------------------------------
    # 3. Coupons (GROWTH+)
    # ------------------------------------------------------------------

    # Predefined coupon library
    _COUPONS: dict[str, float] = {
        "DREAMCO10": 10.0,
        "DREAMCO20": 20.0,
        "LAUNCH50": 50.0,
        "ANNUAL17": 17.0,
        "VIP30": 30.0,
    }

    def _apply_coupon(self, code: str) -> float:
        """Return discount percentage for *code*, or 0 if invalid."""
        return self._COUPONS.get(code.upper(), 0.0)

    def validate_coupon(self, code: str) -> dict:
        """
        Validate a coupon code.

        Parameters
        ----------
        code : str
            Coupon code (case-insensitive).

        Returns
        -------
        dict
            ``{"valid": bool, "discount_pct": float, "code": str}``
        """
        self._require(FEATURE_COUPONS)
        pct = self._apply_coupon(code)
        return {"valid": pct > 0, "discount_pct": pct, "code": code.upper()}

    # ------------------------------------------------------------------
    # 4. Invoices (GROWTH+)
    # ------------------------------------------------------------------

    def create_invoice(
        self,
        customer_id: str,
        line_items: list[dict],
        currency: str = "USD",
        due_days: int = 30,
    ) -> dict:
        """
        Create a Stripe Invoice for B2B billing.

        Parameters
        ----------
        customer_id : str
            Customer identifier.
        line_items : list[dict]
            Each item must have ``description`` (str) and ``amount`` (float).
        currency : str
            Billing currency code.
        due_days : int
            Days until the invoice is due.

        Returns
        -------
        dict
            Invoice record.
        """
        self._require(FEATURE_INVOICES)
        self._validate_currency(currency)

        total = sum(item.get("amount", 0) for item in line_items)
        self._validate_amount(total)

        inv_id = self._new_id("in")
        record = {
            "id": inv_id,
            "object": "invoice",
            "customer_id": customer_id,
            "currency": currency.upper(),
            "line_items": line_items,
            "total_amount": round(total, 2),
            "status": "open",
            "due_in_days": due_days,
            "created_at": self._now(),
            "tier": self.tier.value,
        }
        self._invoices[inv_id] = record
        return record

    def pay_invoice(self, invoice_id: str) -> dict:
        """
        Mark an invoice as paid.

        Parameters
        ----------
        invoice_id : str
            Invoice ID to mark paid.

        Returns
        -------
        dict
            Updated invoice record.
        """
        self._require(FEATURE_INVOICES)
        if invoice_id not in self._invoices:
            raise StripeValidationError(f"Invoice '{invoice_id}' not found.")
        inv = self._invoices[invoice_id]
        inv["status"] = "paid"
        inv["paid_at"] = self._now()
        self._revenue_usd += inv["total_amount"]
        return dict(inv)

    # ------------------------------------------------------------------
    # 5. Webhooks (GROWTH+)
    # ------------------------------------------------------------------

    def process_webhook(self, event: dict) -> dict:
        """
        Process a Stripe webhook event payload.

        Handles the following event types:
        - ``payment_intent.succeeded``
        - ``payment_intent.payment_failed``
        - ``customer.subscription.created``
        - ``customer.subscription.deleted``
        - ``invoice.payment_succeeded``
        - ``invoice.payment_failed``

        Parameters
        ----------
        event : dict
            The parsed Stripe event object.

        Returns
        -------
        dict
            Processing result with ``{"handled": bool, "event_type": str, ...}``.
        """
        self._require(FEATURE_WEBHOOKS)

        event_type = event.get("type", "unknown")
        data = event.get("data", {}).get("object", {})

        result: dict = {
            "handled": True,
            "event_type": event_type,
            "processed_at": self._now(),
        }

        if event_type == "payment_intent.succeeded":
            result["action"] = "revenue_recorded"
            self._revenue_usd += data.get("amount", 0) / 100  # cents→USD
        elif event_type == "payment_intent.payment_failed":
            result["action"] = "payment_failed_logged"
        elif event_type == "customer.subscription.created":
            result["action"] = "subscription_activated"
        elif event_type == "customer.subscription.deleted":
            result["action"] = "subscription_deactivated"
        elif event_type == "invoice.payment_succeeded":
            result["action"] = "invoice_paid"
            self._revenue_usd += data.get("amount_paid", 0) / 100
        elif event_type == "invoice.payment_failed":
            result["action"] = "invoice_payment_failed_logged"
        else:
            result["handled"] = False
            result["action"] = "unhandled_event"

        self._webhook_log.append(result)
        return result

    def get_webhook_log(self) -> list[dict]:
        """Return all processed webhook events."""
        self._require(FEATURE_WEBHOOKS)
        return list(self._webhook_log)

    # ------------------------------------------------------------------
    # 6. Refunds (all tiers)
    # ------------------------------------------------------------------

    def create_refund(
        self,
        checkout_id: str,
        amount: Optional[float] = None,
        reason: str = "requested_by_customer",
    ) -> dict:
        """
        Issue a full or partial refund for a completed checkout session.

        Parameters
        ----------
        checkout_id : str
            Checkout session to refund.
        amount : float, optional
            Refund amount in USD.  Defaults to full session amount.
        reason : str
            Stripe refund reason code.

        Returns
        -------
        dict
            Refund record.
        """
        self._require(FEATURE_REFUNDS)

        if checkout_id not in self._checkouts:
            raise StripeValidationError(f"Checkout '{checkout_id}' not found.")

        session = self._checkouts[checkout_id]
        original = session["amount_total"] / 100  # cents → USD
        refund_amount = amount if amount is not None else original

        if refund_amount > original:
            raise StripeValidationError("Refund amount exceeds original payment.")

        ref_id = self._new_id("re")
        record = {
            "id": ref_id,
            "object": "refund",
            "checkout_id": checkout_id,
            "amount": round(refund_amount, 2),
            "currency": session["currency"],
            "reason": reason,
            "status": "succeeded",
            "created_at": self._now(),
        }
        self._refunds[ref_id] = record
        self._revenue_usd -= refund_amount
        return record

    # ------------------------------------------------------------------
    # 7. Stripe Connect — split payments (ENTERPRISE)
    # ------------------------------------------------------------------

    def create_connect_account(self, email: str, country: str = "US") -> dict:
        """
        Create a Stripe Connect (Express) account for a marketplace seller.

        Parameters
        ----------
        email : str
            Seller's email address.
        country : str
            ISO 3166-1 alpha-2 country code.

        Returns
        -------
        dict
            Connect account record with ``onboarding_url``.
        """
        self._require(FEATURE_CONNECT)

        acct_id = self._new_id("acct")
        record = {
            "id": acct_id,
            "object": "account",
            "type": "express",
            "email": email,
            "country": country.upper(),
            "status": "pending",
            "onboarding_url": f"https://connect.stripe.com/setup/e/{acct_id}",
            "created_at": self._now(),
        }
        self._connect_accounts[acct_id] = record
        return record

    def split_payment(
        self,
        amount: float,
        currency: str,
        destination_account_id: str,
        platform_fee_usd: float,
        description: str = "Marketplace split",
    ) -> dict:
        """
        Execute a split payment to a Connect account.

        Parameters
        ----------
        amount : float
            Total charge amount.
        currency : str
            ISO 4217 currency code.
        destination_account_id : str
            Stripe Connect account to receive the net amount.
        platform_fee_usd : float
            DreamCo platform fee retained.
        description : str
            Payment description.

        Returns
        -------
        dict
            Transfer record with net and fee amounts.
        """
        self._require(FEATURE_SPLIT_PAYMENTS)
        self._validate_amount(amount)
        self._validate_currency(currency)
        self._check_monthly_cap()

        if destination_account_id not in self._connect_accounts:
            raise StripeValidationError(
                f"Connect account '{destination_account_id}' not registered."
            )

        transfer_id = self._new_id("tr")
        net = round(amount - platform_fee_usd, 2)
        record = {
            "id": transfer_id,
            "object": "transfer",
            "amount": amount,
            "currency": currency.upper(),
            "destination": destination_account_id,
            "platform_fee_usd": platform_fee_usd,
            "net_to_seller": net,
            "description": description,
            "status": "paid",
            "created_at": self._now(),
        }
        self._revenue_usd += platform_fee_usd
        self._payment_count += 1
        return record

    # ------------------------------------------------------------------
    # 8. Fraud Radar (ENTERPRISE)
    # ------------------------------------------------------------------

    def check_fraud_score(self, payment_method: str, amount: float, ip: str) -> dict:
        """
        Return a simulated Stripe Radar fraud risk score.

        Parameters
        ----------
        payment_method : str
            Payment method token (e.g. ``pm_card_visa``).
        amount : float
            Transaction amount in USD.
        ip : str
            Customer IP address.

        Returns
        -------
        dict
            Fraud assessment with ``risk_level`` and ``score``.
        """
        self._require(FEATURE_FRAUD_RADAR)

        # Heuristic: large amounts from unusual IPs get medium risk
        score = min(100, int(amount / 10) + len(ip) % 20)
        level = "high" if score > 70 else "elevated" if score > 40 else "normal"
        return {
            "payment_method": payment_method,
            "amount_usd": amount,
            "ip": ip,
            "risk_score": score,
            "risk_level": level,
            "recommendation": "block" if level == "high" else "review" if level == "elevated" else "allow",
            "assessed_at": self._now(),
        }

    # ------------------------------------------------------------------
    # 9. Analytics (GROWTH+)
    # ------------------------------------------------------------------

    def get_revenue_summary(self) -> dict:
        """
        Return a revenue analytics summary.

        Returns
        -------
        dict
            Aggregate revenue, payment counts, and per-plan breakdown.
        """
        self._require(FEATURE_ANALYTICS)

        plan_revenue: dict[str, float] = {}
        for sub in self._subscriptions.values():
            plan_id = sub.get("plan_id", "unknown")
            if sub.get("status") == "active":
                plan_revenue[plan_id] = plan_revenue.get(plan_id, 0) + sub.get("amount_usd", 0)

        return {
            "total_revenue_usd": round(self._revenue_usd, 2),
            "total_checkouts": len(self._checkouts),
            "total_subscriptions": len(self._subscriptions),
            "active_subscriptions": sum(
                1 for s in self._subscriptions.values() if s.get("status") == "active"
            ),
            "total_invoices": len(self._invoices),
            "total_refunds": len(self._refunds),
            "revenue_by_plan": plan_revenue,
            "payment_count": self._payment_count,
            "tier": self.tier.value,
            "generated_at": self._now(),
        }

    # ------------------------------------------------------------------
    # 10. BuddyAI chat + GLOBAL AI SOURCES FLOW interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Natural-language routing for BuddyAI integration."""
        msg = message.lower()
        if any(kw in msg for kw in ("checkout", "pay", "buy", "purchase")):
            session = self.create_checkout_session(
                amount=99.0,
                currency="USD",
                product_name="DreamCo Bot Access",
                customer_email="user@example.com",
            )
            return {
                "message": f"Checkout session created. Proceed to: {session['url']}",
                "data": session,
            }
        if "subscription" in msg or "subscribe" in msg:
            sub = self.create_subscription(
                customer_id="cus_demo",
                plan_id="lead_generator_pro",
            )
            return {
                "message": f"Subscription '{sub['id']}' created for plan '{sub['plan_id']}'.",
                "data": sub,
            }
        if "revenue" in msg or "summary" in msg or "analytics" in msg:
            if self._config.has_feature(FEATURE_ANALYTICS):
                return {"message": "Revenue summary retrieved.", "data": self.get_revenue_summary()}
            return {"message": "Analytics available on GROWTH tier and above."}
        if "refund" in msg:
            return {"message": "To refund, call create_refund(checkout_id) directly."}
        return {
            "message": (
                f"Stripe Payment Bot online (tier: {self.tier.value}). "
                "Commands: 'create checkout', 'subscribe', 'revenue summary', 'refund'."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.chat(payload.get("command", ""))


# Alias for framework compatibility
Bot = StripePaymentBot
