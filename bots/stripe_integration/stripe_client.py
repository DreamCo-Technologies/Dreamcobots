"""
StripeClient — Thin wrapper around the Stripe Python SDK.

All credentials are read from environment variables.  When
``STRIPE_SECRET_KEY`` is absent (or starts with ``sk_test_placeholder``),
the client operates in **mock mode**: all API calls return realistic
simulated responses without hitting the Stripe API.

Environment variables
---------------------
STRIPE_SECRET_KEY       Your Stripe secret key (sk_test_... / sk_live_...).
STRIPE_PUBLISHABLE_KEY  Your Stripe publishable key (pk_test_... / pk_live_...).
STRIPE_WEBHOOK_SECRET   Endpoint signing secret (whsec_...) for webhook verification.

Usage
-----
    from bots.stripe_integration import StripeClient

    client = StripeClient()
    session = client.create_checkout_session(
        plan="pro",
        amount_cents=4900,
        currency="usd",
        customer_email="user@example.com",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )
    print(session["url"])
"""

from __future__ import annotations

import os
import uuid
import datetime
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class StripeError(Exception):
    """Raised when a Stripe API call fails."""


StripeClientError = StripeError


_PLACEHOLDER_PREFIXES = ("sk_test_placeholder", "sk_test_your_")


def _is_placeholder(key: str) -> bool:
    """Return True if *key* looks like a placeholder / missing value."""
    if not key:
        return True
    return any(key.startswith(prefix) for prefix in _PLACEHOLDER_PREFIXES)


class StripeClient:
    """
    Wrapper around the Stripe Python SDK with transparent mock mode.

    Parameters
    ----------
    secret_key : str | None
        Stripe secret key.  Defaults to the ``STRIPE_SECRET_KEY``
        environment variable.  If absent or a placeholder, mock mode
        is activated automatically.
    mock : bool | None
        Override mock mode.  ``None`` (default) auto-detects from the key.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        mock: Optional[bool] = None,
    ) -> None:
        self._secret_key: str = (
            secret_key
            or os.environ.get("STRIPE_SECRET_KEY", "")
        )
        self._publishable_key: str = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")

        if mock is None:
            self._mock = _is_placeholder(self._secret_key) or not self._secret_key
        else:
            self._mock = mock

        if not self._mock:
            try:
                import stripe as _stripe  # type: ignore
                _stripe.api_key = self._secret_key
                self._stripe = _stripe
            except ImportError as exc:  # pragma: no cover
                raise StripeError(
                    "The 'stripe' package is not installed. "
                    "Run: pip install stripe>=7.0.0"
                ) from exc

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_mock(self) -> bool:
        """Return True when operating in mock mode."""
        return self._mock

    @property
    def publishable_key(self) -> str:
        """Return the publishable key (safe to expose to clients)."""
        return self._publishable_key

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    @staticmethod
    def _new_id(prefix: str = "pi") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:24]}"

    # ------------------------------------------------------------------
    # Checkout Sessions
    # ------------------------------------------------------------------

    def create_checkout_session(
        self,
        plan: str = None,
        amount_cents: int = 0,
        currency: str = "usd",
        customer_email: Optional[str] = None,
        success_url: str = "https://example.com/success",
        cancel_url: str = "https://example.com/cancel",
        mode: str = "payment",
        metadata: Optional[dict] = None,
        product_name: Optional[str] = None,
    ) -> dict:
        """
        Create a Stripe Checkout session.

        Parameters
        ----------
        plan          Arbitrary plan name / identifier stored in metadata.
        amount_cents  Price in the smallest currency unit (e.g. 4900 = $49.00).
        currency      ISO 4217 lowercase currency code (default: "usd").
        customer_email  Pre-fill the customer's email in the checkout form.
        success_url   Redirect URL on successful payment.
        cancel_url    Redirect URL when the customer cancels.
        mode          "payment" (one-time) | "subscription".
        metadata      Extra key/value pairs attached to the session.

        Returns
        -------
        dict with keys: session_id, url, plan, amount_cents, currency,
                        mode, customer_email, status.
        """
        plan = plan or product_name or "payment"
        if self._mock:
            session_id = self._new_id("cs_test")
            return {
                "session_id": session_id,
                "id": session_id,
                "url": f"https://checkout.stripe.com/pay/{session_id}",
                "plan": plan,
                "amount_cents": amount_cents,
                "currency": currency,
                "mode": mode,
                "customer_email": customer_email,
                "status": "open",
                "mock": True,
            }

        try:
            line_items = [
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount_cents,
                        "product_data": {"name": plan},
                        **(
                            {"recurring": {"interval": "month"}}
                            if mode == "subscription"
                            else {}
                        ),
                    },
                    "quantity": 1,
                }
            ]
            params: dict = {
                "payment_method_types": ["card"],
                "line_items": line_items,
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {**(metadata or {}), "plan": plan},
            }
            if customer_email:
                params["customer_email"] = customer_email

            session = self._stripe.checkout.Session.create(**params)
            return {
                "session_id": session.id,
                "url": session.url,
                "plan": plan,
                "amount_cents": amount_cents,
                "currency": currency,
                "mode": mode,
                "customer_email": customer_email,
                "status": session.status,
                "mock": False,
            }
        except Exception as exc:
            raise StripeError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Payment Intents
    # ------------------------------------------------------------------

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Payment Intent for a one-time charge.

        Returns dict with keys: intent_id, client_secret, amount_cents,
                                currency, status, mock.
        """
        if self._mock:
            intent_id = self._new_id("pi")
            return {
                "intent_id": intent_id,
                "id": intent_id,
                "client_secret": f"{intent_id}_secret_{uuid.uuid4().hex[:16]}",
                "amount_cents": amount_cents,
                "currency": currency,
                "status": "requires_payment_method",
                "mock": True,
            }

        try:
            params: dict = {
                "amount": amount_cents,
                "currency": currency,
                "metadata": metadata or {},
            }
            if customer_id:
                params["customer"] = customer_id
            if description:
                params["description"] = description

            intent = self._stripe.PaymentIntent.create(**params)
            return {
                "intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount_cents": amount_cents,
                "currency": currency,
                "status": intent.status,
                "mock": False,
            }
        except Exception as exc:
            raise StripeError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Subscription for an existing customer.

        Parameters
        ----------
        customer_id  Stripe customer ID (cus_...).
        price_id     Stripe Price ID (price_...) for the recurring plan.
        trial_days   Number of free trial days (0 = no trial).
        metadata     Extra key/value pairs.

        Returns
        -------
        dict with keys: subscription_id, customer_id, price_id, status,
                        trial_end, mock.
        """
        if self._mock:
            sub_id = self._new_id("sub")
            trial_end = None
            if trial_days > 0:
                trial_end = (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(days=trial_days)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            return {
                "subscription_id": sub_id,
                "id": sub_id,
                "customer_id": customer_id,
                "price_id": price_id,
                "status": "trialing" if trial_days > 0 else "active",
                "trial_end": trial_end,
                "mock": True,
            }

        try:
            params: dict = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {},
            }
            if trial_days > 0:
                params["trial_period_days"] = trial_days

            sub = self._stripe.Subscription.create(**params)
            return {
                "subscription_id": sub.id,
                "customer_id": customer_id,
                "price_id": price_id,
                "status": sub.status,
                "trial_end": (
                    datetime.datetime.fromtimestamp(
                        sub.trial_end, tz=datetime.timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
                    if sub.trial_end
                    else None
                ),
                "mock": False,
            }
        except Exception as exc:
            raise StripeError(str(exc)) from exc

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel a Stripe Subscription immediately.

        Returns dict with keys: subscription_id, status, mock.
        """
        if self._mock:
            return {
                "subscription_id": subscription_id,
                "status": "canceled",
                "mock": True,
            }

        try:
            sub = self._stripe.Subscription.delete(subscription_id)
            return {
                "subscription_id": subscription_id,
                "status": sub.status,
                "mock": False,
            }
        except Exception as exc:
            raise StripeError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Payment Links
    # ------------------------------------------------------------------

    def create_payment_link(
        self,
        plan: str = None,
        amount_cents: int = 0,
        currency: str = "usd",
        quantity: int = 1,
        product_name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Payment Link (shareable URL).

        Returns dict with keys: link_id, id, url, plan, amount_cents,
                                currency, mock.
        """
        if self._mock:
            link_id = self._new_id("plink")
            return {
                "link_id": link_id,
                "id": link_id,
                "url": f"https://buy.stripe.com/{link_id}",
                "plan": plan or product_name,
                "amount_cents": amount_cents,
                "currency": currency,
                "mock": True,
            }

        try:
            price = self._stripe.Price.create(
                currency=currency,
                unit_amount=amount_cents,
                product_data={"name": plan or product_name},
            )
            link = self._stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": quantity}]
            )
            return {
                "link_id": link.id,
                "id": link.id,
                "url": link.url,
                "plan": plan or product_name,
                "amount_cents": amount_cents,
                "currency": currency,
                "mock": False,
            }
        except Exception as exc:
            raise StripeError(str(exc)) from exc


def _create_customer(self, email: str = "", name: str = "") -> dict:
    """Create a Stripe customer. Returns dict with 'id', 'email', 'name'."""
    if self._mock:
        cust_id = self._new_id("cus")
        return {"id": cust_id, "email": email, "name": name, "mock": True}
    try:
        customer = self._stripe.Customer.create(email=email, name=name)
        return {"id": customer.id, "email": email, "name": name, "mock": False}
    except Exception as exc:
        raise StripeError(str(exc)) from exc


StripeClient.create_customer = _create_customer


def _refund_payment(self, payment_intent_id: str, reason: str = "requested_by_customer") -> dict:
    """Refund a payment intent."""
    if self._mock:
        refund_id = self._new_id("re")
        return {"id": refund_id, "status": "succeeded", "payment_intent": payment_intent_id, "reason": reason}
    try:
        refund = self._stripe.Refund.create(payment_intent=payment_intent_id, reason=reason)
        return {"id": refund.id, "status": refund.status, "payment_intent": payment_intent_id}
    except Exception as exc:
        raise StripeError(str(exc)) from exc


def _get_balance(self) -> dict:
    """Get Stripe account balance."""
    if self._mock:
        return {"available": [{"amount": 1000000, "currency": "usd"}], "pending": [{"amount": 50000, "currency": "usd"}]}
    try:
        balance = self._stripe.Balance.retrieve()
        return {"available": [{"amount": a.amount, "currency": a.currency} for a in balance.available],
                "pending": [{"amount": p.amount, "currency": p.currency} for p in balance.pending]}
    except Exception as exc:
        raise StripeError(str(exc)) from exc


def _list_payouts(self, limit: int = 10) -> list:
    """List recent payouts."""
    if self._mock:
        return [{"id": self._new_id("po"), "amount": 50000, "currency": "usd", "status": "paid"}]
    try:
        payouts = self._stripe.Payout.list(limit=limit)
        return [{"id": p.id, "amount": p.amount, "currency": p.currency, "status": p.status} for p in payouts.data]
    except Exception as exc:
        raise StripeError(str(exc)) from exc


StripeClient.refund_payment = _refund_payment
StripeClient.get_balance = _get_balance
StripeClient.list_payouts = _list_payouts
