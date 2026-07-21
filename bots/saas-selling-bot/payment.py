"""
Payment gateway integration for the SaaS Selling Bot.
Handles subscription creation, webhook processing, and revenue recording.
Supports Stripe as the primary payment provider.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import os
import json

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

from database import add_subscription, record_conversion

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PLANS = {
    "free": {
        "name": "Free Explorer",
        "price_usd": 0,
        "features": [
            "Browse 200+ SaaS tools",
            "Basic search and filter",
            "Category browsing",
        ],
        "stripe_price_id": None,
    },
    "pro": {
        "name": "Pro Seller",
        "price_usd": 29,
        "features": [
            "Everything in Free",
            "AI-powered recommendations",
            "Priority affiliate commissions",
            "Advanced analytics dashboard",
            "Email alerts for new tools",
        ],
        "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_placeholder"),
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 99,
        "features": [
            "Everything in Pro",
            "Custom white-label portal",
            "Dedicated account manager",
            "API access with higher rate limits",
            "Custom tool integrations",
        ],
        "stripe_price_id": os.getenv(
            "STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise_placeholder"
        ),
    },
}


def create_checkout_session(email: str, plan: str) -> dict:
    """
    Create a Stripe Checkout session for the given plan.
    Returns a dict with 'url' (redirect URL) or 'error'.
    """
    if plan == "free":
        add_subscription(email=email, plan="free")
        return {"success": True, "message": "Free plan activated!", "url": None}

    if not STRIPE_AVAILABLE or not STRIPE_SECRET_KEY:
        return {
            "success": False,
            "error": (
                "Payment gateway not configured. "
                "Set STRIPE_SECRET_KEY to enable paid plans."
            ),
        }

    try:
        stripe.api_key = STRIPE_SECRET_KEY
        plan_data = PLANS.get(plan)
        if not plan_data or not plan_data.get("stripe_price_id"):
            return {"success": False, "error": f"Unknown plan: {plan}"}

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=email,
            line_items=[{"price": plan_data["stripe_price_id"], "quantity": 1}],
            success_url=os.getenv(
                "STRIPE_SUCCESS_URL",
                "http://localhost:5000/payment/success?session_id={CHECKOUT_SESSION_ID}",
            ),
            cancel_url=os.getenv(
                "STRIPE_CANCEL_URL", "http://localhost:5000/payment/cancel"
            ),
            metadata={"plan": plan},
        )
        return {"success": True, "url": session.url, "session_id": session.id}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Process a Stripe webhook event.
    Returns a dict with 'status' and optional 'message'.
    """
    if not STRIPE_AVAILABLE or not STRIPE_SECRET_KEY:
        return {"status": "ignored", "message": "Stripe not configured"}

    try:
        stripe.api_key = STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return {"status": "error", "message": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"status": "error", "message": "Invalid signature"}

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email", "")
        plan = session.get("metadata", {}).get("plan", "pro")
        customer_id = session.get("customer", "")
        add_subscription(email=email, plan=plan, stripe_customer_id=customer_id)
        return {"status": "ok", "message": f"Subscription activated for {email}"}

    if event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        return {"status": "ok", "message": f"Handled event: {event_type}"}

    return {"status": "ok", "message": f"Unhandled event type: {event_type}"}


def get_plans() -> list:
    """Return all available subscription plans."""
    return [
        {
            "id": plan_id,
            "name": plan["name"],
            "price_usd": plan["price_usd"],
            "features": plan["features"],
        }
        for plan_id, plan in PLANS.items()
    ]


if __name__ == "__main__":
    print("Available subscription plans:")
    for plan in get_plans():
        print(f"  {plan['name']} – ${plan['price_usd']}/month")
        for feature in plan["features"]:
            print(f"    ✓ {feature}")
