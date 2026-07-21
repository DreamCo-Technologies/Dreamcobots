"""
DreamCobots — Stripe Python Integration

Provides Payment Intent creation, subscription management, checkout sessions,
and webhook handling for all DreamCobots bots.

Setup:
    pip install stripe flask python-dotenv
    export STRIPE_SECRET_KEY=sk_...
    python app.py
"""

import os
import json
import stripe
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Payment Intent
# ---------------------------------------------------------------------------

def create_payment_intent(amount_in_cents: int, currency: str = "usd") -> dict:
    """Create a Stripe Payment Intent for a one-time charge.

    Parameters
    ----------
    amount_in_cents : int
        Amount in the smallest currency unit (e.g. cents for USD).
    currency : str
        ISO 4217 currency code (default ``"usd"``).

    Returns
    -------
    dict
        Stripe PaymentIntent object as a dict.
    """
    payment_intent = stripe.PaymentIntent.create(
        amount=amount_in_cents,
        currency=currency,
        automatic_payment_methods={"enabled": True},
    )
    return dict(payment_intent)


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

def create_subscription(email: str, price_id: str) -> dict:
    """Create a customer and subscribe them to a recurring price.

    Parameters
    ----------
    email : str
        Customer e-mail address.
    price_id : str
        Stripe Price ID (e.g. ``"price_xxx"``).

    Returns
    -------
    dict
        Stripe Subscription object as a dict.
    """
    customer = stripe.Customer.create(email=email)
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": price_id}],
        payment_behavior="default_incomplete",
        expand=["latest_invoice.payment_intent"],
    )
    return dict(subscription)


def cancel_subscription(subscription_id: str) -> dict:
    """Cancel an existing subscription immediately.

    Parameters
    ----------
    subscription_id : str
        Stripe Subscription ID to cancel.

    Returns
    -------
    dict
        Updated Stripe Subscription object as a dict.
    """
    subscription = stripe.Subscription.delete(subscription_id)
    return dict(subscription)


# ---------------------------------------------------------------------------
# Checkout Sessions
# ---------------------------------------------------------------------------

def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    mode: str = "subscription",
    customer_email: str | None = None,
) -> dict:
    """Create a Stripe Checkout session.

    Parameters
    ----------
    price_id : str
        Stripe Price ID for the item.
    success_url : str
        URL to redirect to after successful payment.
    cancel_url : str
        URL to redirect to if the user cancels.
    mode : str
        ``"payment"`` for one-time or ``"subscription"`` for recurring.
    customer_email : str or None
        Pre-fill the customer e-mail on the checkout page.

    Returns
    -------
    dict
        Stripe Session object as a dict (includes ``url``).
    """
    params: dict = {
        "payment_method_types": ["card"],
        "line_items": [{"price": price_id, "quantity": 1}],
        "mode": mode,
        "success_url": success_url,
        "cancel_url": cancel_url,
    }
    if customer_email:
        params["customer_email"] = customer_email

    session = stripe.checkout.Session.create(**params)
    return dict(session)


# ---------------------------------------------------------------------------
# Payout Tracking
# ---------------------------------------------------------------------------

def list_payouts(limit: int = 10) -> list:
    """Return a list of recent payouts from your Stripe account.

    Parameters
    ----------
    limit : int
        Maximum number of payouts to return (default 10).

    Returns
    -------
    list[dict]
        List of Stripe Payout objects.
    """
    payouts = stripe.Payout.list(limit=limit)
    return [dict(p) for p in payouts.data]


# ---------------------------------------------------------------------------
# Webhook Handler
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Stripe webhook events."""
    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature", "")

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError as exc:
            return jsonify({"error": str(exc)}), 400
    else:
        event = json.loads(payload)

    event_type = event.get("type", "")
    print(f"Webhook event received: {event_type}")

    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"Payment succeeded: {payment_intent['id']}")
    elif event_type == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Checkout completed: {session['id']}")
    elif event_type == "customer.subscription.created":
        subscription = event["data"]["object"]
        print(f"Subscription created: {subscription['id']}")
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        print(f"Subscription canceled: {subscription['id']}")
    else:
        print(f"Unhandled event type: {event_type}")

    return jsonify({"received": True}), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"DreamCobots Stripe webhook listener running on port {port}")
    print(f"Test locally: stripe listen --forward-to localhost:{port}/webhook")
    app.run(port=port, debug=False)
