"""
StripeBot — Main Stripe integration bot for Dreamcobots.

All Stripe calls are proxied through environment variables so that no secret
credentials are ever hard-coded in the repository.  Set the following
environment variables before using this bot:

  STRIPE_SECRET_KEY      — sk_live_... or sk_test_...
  STRIPE_PUBLISHABLE_KEY — pk_live_... or pk_test_...
  STRIPE_WEBHOOK_SECRET  — whsec_... (from your Stripe webhook endpoint)

Usage
-----
    from bots.stripe_integration import StripeBot

    bot = StripeBot()
    session = bot.create_checkout_session(
        amount_cents=2500,
        currency="usd",
        customer_email="buyer@example.com",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )
    print(session["checkout_url"])
"""

import os
import uuid
import datetime
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class StripeBotError(Exception):
    """Raised when a Stripe operation cannot be completed."""


class StripeBot:
    """
    Full-featured Stripe integration bot for Dreamcobots.

    Supports one-time payments, subscriptions, payouts, customer management,
    refunds, and BuddyAI-compatible chat routing.  When the ``stripe`` package
    is installed and STRIPE_SECRET_KEY is set, live Stripe calls are made.
    Otherwise the bot falls back to a simulation mode for testing purposes.

    Parameters
    ----------
    secret_key : str, optional
        Stripe secret key.  Defaults to the ``STRIPE_SECRET_KEY`` env var.
    publishable_key : str, optional
        Stripe publishable key.  Defaults to the ``STRIPE_PUBLISHABLE_KEY``
        env var.
    simulation_mode : bool
        When ``True``, skip live Stripe calls and return simulated responses.
        Defaults to ``False`` unless no secret key is found.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        publishable_key: Optional[str] = None,
        simulation_mode: bool = False,
    ) -> None:
        self.secret_key = secret_key or os.environ.get("STRIPE_SECRET_KEY", "")
        self.publishable_key = publishable_key or os.environ.get(
            "STRIPE_PUBLISHABLE_KEY", ""
        )
        self.simulation_mode = simulation_mode or not self.secret_key

        self._stripe = None
        if not self.simulation_mode:
            self._stripe = self._load_stripe()

        self._customers: dict[str, dict] = {}
        self._sessions: dict[str, dict] = {}
        self._subscriptions: dict[str, dict] = {}
        self._payouts: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_stripe(self):
        """Attempt to import and configure the stripe library."""
        try:
            import stripe  # noqa: PLC0415
            stripe.api_key = self.secret_key
            return stripe
        except ImportError:
            self.simulation_mode = True
            return None

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @staticmethod
    def _new_id(prefix: str = "sim") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16]}"

    # ------------------------------------------------------------------
    # Customer management
    # ------------------------------------------------------------------

    def create_customer(self, email: str, name: str = "", metadata: Optional[dict] = None) -> dict:
        """
        Create a Stripe customer.

        Parameters
        ----------
        email : str
            Customer e-mail address.
        name : str
            Optional display name.
        metadata : dict, optional
            Extra key-value pairs attached to the customer.

        Returns
        -------
        dict
            Customer record with ``id``, ``email``, ``name``, ``created``.
        """
        if not self.simulation_mode and self._stripe:
            customer = self._stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            result = {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name or "",
                "created": self._now_iso(),
                "live": True,
            }
        else:
            cid = self._new_id("cus")
            result = {
                "id": cid,
                "email": email,
                "name": name,
                "created": self._now_iso(),
                "live": False,
            }
        self._customers[result["id"]] = result
        return result

    def get_customer(self, customer_id: str) -> dict:
        """Retrieve a customer by ID (simulation or Stripe)."""
        if not self.simulation_mode and self._stripe:
            c = self._stripe.Customer.retrieve(customer_id)
            return {"id": c.id, "email": c.email, "name": c.name or "", "live": True}
        if customer_id not in self._customers:
            raise StripeBotError(f"Customer not found: {customer_id}")
        return self._customers[customer_id]

    # ------------------------------------------------------------------
    # Checkout sessions
    # ------------------------------------------------------------------

    def create_checkout_session(
        self,
        amount_cents: int,
        currency: str,
        customer_email: str,
        success_url: str,
        cancel_url: str,
        mode: str = "payment",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Checkout session for one-time payment or subscription.

        Parameters
        ----------
        amount_cents : int
            Price in the smallest currency unit (e.g. cents for USD).
        currency : str
            ISO 4217 currency code, e.g. ``"usd"``.
        customer_email : str
            Pre-fill the customer e-mail on the Checkout page.
        success_url : str
            Redirect URL after successful payment.
        cancel_url : str
            Redirect URL when the customer cancels.
        mode : str
            ``"payment"`` (one-time) or ``"subscription"``.
        metadata : dict, optional
            Key-value pairs attached to the session.

        Returns
        -------
        dict
            Session record including ``session_id`` and ``checkout_url``.
        """
        if not self.simulation_mode and self._stripe:
            session = self._stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency.lower(),
                            "product_data": {"name": "Dreamcobots Service"},
                            "unit_amount": amount_cents,
                        },
                        "quantity": 1,
                    }
                ],
                mode=mode,
                customer_email=customer_email,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            result = {
                "session_id": session.id,
                "checkout_url": session.url,
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "mode": mode,
                "status": session.status,
                "created": self._now_iso(),
                "live": True,
            }
        else:
            sid = self._new_id("cs")
            result = {
                "session_id": sid,
                "checkout_url": f"https://checkout.stripe.com/pay/simulated_{sid}",
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "mode": mode,
                "status": "open",
                "created": self._now_iso(),
                "live": False,
            }
        self._sessions[result["session_id"]] = result
        return result

    # ------------------------------------------------------------------
    # Payment intents
    # ------------------------------------------------------------------

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        customer_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe PaymentIntent for custom payment flows.

        Parameters
        ----------
        amount_cents : int
            Amount in smallest currency unit.
        currency : str
            ISO 4217 currency code.
        customer_id : str, optional
            Stripe customer ID to attach the intent to.
        metadata : dict, optional
            Key-value metadata.

        Returns
        -------
        dict
            PaymentIntent record with ``id``, ``client_secret``, ``status``.
        """
        if not self.simulation_mode and self._stripe:
            intent = self._stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "live": True,
            }
        return {
            "id": self._new_id("pi"),
            "client_secret": f"sim_secret_{uuid.uuid4().hex}",
            "status": "requires_payment_method",
            "amount_cents": amount_cents,
            "currency": currency.lower(),
            "live": False,
        }

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a recurring Stripe subscription for a customer.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.
        price_id : str
            Stripe Price ID (``price_...``).
        metadata : dict, optional
            Key-value metadata.

        Returns
        -------
        dict
            Subscription record with ``id``, ``status``, ``current_period_end``.
        """
        if not self.simulation_mode and self._stripe:
            sub = self._stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
            )
            result = {
                "id": sub.id,
                "customer_id": customer_id,
                "price_id": price_id,
                "status": sub.status,
                "current_period_end": sub.current_period_end,
                "created": self._now_iso(),
                "live": True,
            }
        else:
            sub_id = self._new_id("sub")
            future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
            result = {
                "id": sub_id,
                "customer_id": customer_id,
                "price_id": price_id,
                "status": "active",
                "current_period_end": future.isoformat(),
                "created": self._now_iso(),
                "live": False,
            }
        self._subscriptions[result["id"]] = result
        return result

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel an existing subscription immediately.

        Parameters
        ----------
        subscription_id : str
            Stripe Subscription ID.

        Returns
        -------
        dict
            Updated subscription with ``status`` set to ``"canceled"``.
        """
        if not self.simulation_mode and self._stripe:
            sub = self._stripe.Subscription.delete(subscription_id)
            result = {
                "id": sub.id,
                "status": sub.status,
                "live": True,
            }
        else:
            if subscription_id not in self._subscriptions:
                raise StripeBotError(f"Subscription not found: {subscription_id}")
            self._subscriptions[subscription_id]["status"] = "canceled"
            result = {
                "id": subscription_id,
                "status": "canceled",
                "live": False,
            }
        return result

    # ------------------------------------------------------------------
    # Refunds
    # ------------------------------------------------------------------

    def create_refund(
        self,
        payment_intent_id: str,
        amount_cents: Optional[int] = None,
        reason: str = "requested_by_customer",
    ) -> dict:
        """
        Issue a full or partial refund for a payment.

        Parameters
        ----------
        payment_intent_id : str
            Stripe PaymentIntent ID.
        amount_cents : int, optional
            Amount to refund in cents.  Omit for full refund.
        reason : str
            Refund reason code accepted by Stripe.

        Returns
        -------
        dict
            Refund record with ``id`` and ``status``.
        """
        if not self.simulation_mode and self._stripe:
            kwargs: dict = {"payment_intent": payment_intent_id, "reason": reason}
            if amount_cents is not None:
                kwargs["amount"] = amount_cents
            refund = self._stripe.Refund.create(**kwargs)
            return {
                "id": refund.id,
                "status": refund.status,
                "amount_cents": refund.amount,
                "live": True,
            }
        return {
            "id": self._new_id("re"),
            "status": "succeeded",
            "amount_cents": amount_cents,
            "live": False,
        }

    # ------------------------------------------------------------------
    # Payouts
    # ------------------------------------------------------------------

    def create_payout(
        self,
        amount_cents: int,
        currency: str = "usd",
        method: str = "standard",
    ) -> dict:
        """
        Create a payout to the connected bank account.

        Parameters
        ----------
        amount_cents : int
            Payout amount in cents.
        currency : str
            ISO 4217 currency code.
        method : str
            ``"standard"`` or ``"instant"``.

        Returns
        -------
        dict
            Payout record with ``id``, ``status``, ``arrival_date``.
        """
        if not self.simulation_mode and self._stripe:
            payout = self._stripe.Payout.create(
                amount=amount_cents,
                currency=currency.lower(),
                method=method,
            )
            result = {
                "id": payout.id,
                "status": payout.status,
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "arrival_date": payout.arrival_date,
                "live": True,
            }
        else:
            pid = self._new_id("po")
            arrival = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)
            result = {
                "id": pid,
                "status": "pending",
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "arrival_date": arrival.isoformat(),
                "live": False,
            }
        self._payouts[result["id"]] = result
        return result

    # ------------------------------------------------------------------
    # Balance
    # ------------------------------------------------------------------

    def get_balance(self) -> dict:
        """
        Retrieve the current Stripe account balance.

        Returns
        -------
        dict
            Balance with ``available`` and ``pending`` amounts by currency.
        """
        if not self.simulation_mode and self._stripe:
            bal = self._stripe.Balance.retrieve()
            return {
                "available": [{"amount": a.amount, "currency": a.currency} for a in bal.available],
                "pending": [{"amount": p.amount, "currency": p.currency} for p in bal.pending],
                "live": True,
            }
        return {
            "available": [{"amount": 0, "currency": "usd"}],
            "pending": [{"amount": 0, "currency": "usd"}],
            "live": False,
        }

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Process a plain-text message and return a structured response.

        Provides a BuddyAI-compatible interface so the bot can be registered
        with BuddyBot and receive routed messages.

        Parameters
        ----------
        message : str
            Incoming message text.

        Returns
        -------
        dict
            ``response``, ``bot_name``, ``mode``.
        """
        msg_lower = message.lower()

        if "balance" in msg_lower:
            bal = self.get_balance()
            avail = bal["available"]
            response = "Balance — available: " + ", ".join(
                f"{a['amount']} {a['currency'].upper()}" for a in avail
            )
        elif "checkout" in msg_lower or "session" in msg_lower:
            response = (
                "Use create_checkout_session(amount_cents, currency, "
                "customer_email, success_url, cancel_url) to start a payment."
            )
        elif "subscription" in msg_lower or "subscribe" in msg_lower:
            response = (
                "Use create_subscription(customer_id, price_id) to start "
                "a recurring subscription."
            )
        elif "refund" in msg_lower:
            response = (
                "Use create_refund(payment_intent_id) or "
                "create_refund(payment_intent_id, amount_cents) for partial refunds."
            )
        elif "payout" in msg_lower:
            response = (
                "Use create_payout(amount_cents) to transfer funds to "
                "your connected bank account."
            )
        elif "webhook" in msg_lower:
            response = (
                "Use WebhookHandler.handle_event(payload, sig_header) to "
                "process incoming Stripe webhook events securely."
            )
        elif "payment link" in msg_lower or "payment_link" in msg_lower:
            response = (
                "Use PaymentLinks.create_link(amount_cents, currency, name) "
                "to generate a shareable Stripe Payment Link."
            )
        elif "mode" in msg_lower:
            mode = "simulation" if self.simulation_mode else "live"
            response = f"StripeBot is running in {mode} mode."
        else:
            mode = "simulation" if self.simulation_mode else "live"
            response = (
                f"Dreamcobots StripeBot ({mode} mode) — I can help with "
                "checkout sessions, subscriptions, refunds, payouts, balances, "
                "payment links, and webhook handling."
            )

        return {
            "response": response,
            "bot_name": "stripe_integration",
            "mode": "simulation" if self.simulation_mode else "live",
        }

    # ------------------------------------------------------------------
    # BuddyAI integration
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """
        Register this bot with a BuddyBot instance.

        Parameters
        ----------
        buddy_bot_instance : BuddyBot
            The BuddyBot orchestrator to register with.
        """
        buddy_bot_instance.register_bot("stripe_integration", self)
