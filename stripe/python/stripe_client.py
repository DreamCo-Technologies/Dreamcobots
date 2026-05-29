"""
Stripe integration for Dreamcobots — Python

Install:
  pip install stripe python-dotenv

Configure .env (see ../../.env.example):
  STRIPE_SECRET_KEY=sk_live_...
  STRIPE_PUBLISHABLE_KEY=pk_live_...
  STRIPE_WEBHOOK_SECRET=whsec_...
"""

import os
import sys
import importlib.util

from dotenv import load_dotenv

load_dotenv()


def _load_stripe_sdk():
    """Load the installed Stripe SDK, skipping the local stripe/ stub."""
    _local_init = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "__init__.py")
    )
    for _sp in sys.path:
        _cand = os.path.join(_sp, "stripe", "__init__.py")
        if os.path.isfile(_cand) and os.path.abspath(_cand) != _local_init:
            _spec = importlib.util.spec_from_file_location(
                "stripe", _cand,
                submodule_search_locations=[os.path.dirname(_cand)],
            )
            if _spec and _spec.loader:
                _mod = importlib.util.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
                return _mod
    raise ImportError(
        "The 'stripe' package is not installed. Run: pip install stripe"
    )


_LIVE = False
stripe = None  # type: ignore[assignment]

try:
    stripe = _load_stripe_sdk()
    _key = os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_API_KEY", "")
    if not _key:
        raise KeyError("STRIPE_SECRET_KEY")
    stripe.api_key = _key
    _LIVE = True
except (ImportError, KeyError):
    _LIVE = False


def create_checkout_session(
    amount_cents: int,
    currency: str,
    customer_email: str,
    success_url: str,
    cancel_url: str,
):
    """Create a Stripe Checkout session and return the redirect URL."""
    if not _LIVE:
        return {"url": "https://checkout.stripe.com/pay/simulated", "live": False}
    session = stripe.checkout.Session.create(
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
        mode="payment",
        customer_email=customer_email,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"url": session.url, "session_id": session.id, "live": True}


def create_payment_link(amount_cents: int, currency: str, product_name: str):
    """Create a shareable Stripe Payment Link."""
    if not _LIVE:
        return {"url": "https://buy.stripe.com/simulated", "live": False}
    price = stripe.Price.create(
        unit_amount=amount_cents,
        currency=currency.lower(),
        product_data={"name": product_name},
    )
    link = stripe.PaymentLink.create(line_items=[{"price": price.id, "quantity": 1}])
    return {"url": link.url, "id": link.id, "live": True}


if __name__ == "__main__":
    mode = "live" if _LIVE else "simulation"
    print(f"Dreamcobots Stripe Python client initialised in {mode} mode.")
