"""Stripe payments API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class StripeConnector:
    """StripeConnector for DataForge AI."""

    BASE_URL = "https://api.stripe.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not self.api_key:
            logger.warning("STRIPE_SECRET_KEY not set.")

    def create_payment_intent(self, amount: int, currency: str = "usd") -> dict:
        """Create a Stripe Payment Intent.

        Args:
            amount: Amount in cents (e.g., 1000 = $10.00).
            currency: Currency code (default 'usd').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.post(f"{self.BASE_URL}/payment_intents",
                data={"amount": amount, "currency": currency},
                auth=(self.api_key, ""), timeout=30)
            response.raise_for_status()
            logger.info("Stripe payment intent created: amount=%d %s", amount, currency)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Stripe create_payment_intent error: %s", e)
            return {"status": "error", "message": str(e)}

    def retrieve_customer(self, customer_id: str) -> dict:
        """Retrieve a Stripe customer by ID.

        Args:
            customer_id: The Stripe customer identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/customers/{customer_id}", auth=(self.api_key, ""), timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Stripe retrieve_customer error: %s", e)
            return {"status": "error", "message": str(e)}
