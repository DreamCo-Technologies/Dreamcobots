"""PayPal payments API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class PayPalConnector:
    """PayPalConnector for DataForge AI."""

    BASE_URL = "https://api-m.sandbox.paypal.com"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.client_id = os.environ.get("PAYPAL_CLIENT_ID", "")
        self.client_secret = os.environ.get("PAYPAL_CLIENT_SECRET", "")
        if not self.client_id or not self.client_secret:
            logger.warning("PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET not set.")

    def get_access_token(self) -> dict:
        """Get a PayPal OAuth access token.

        Returns:
            Dict with access_token or error.
        """
        import requests
        try:
            response = requests.post(
                f"{self.BASE_URL}/v1/oauth2/token",
                headers={"Accept": "application/json"},
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                timeout=30
            )
            response.raise_for_status()
            logger.info("PayPal access token obtained.")
            return {"status": "success", "access_token": response.json().get("access_token")}
        except requests.RequestException as e:
            logger.error("PayPal get_access_token error: %s", e)
            return {"status": "error", "message": str(e)}

    def create_order(self, amount: float, currency: str = "USD") -> dict:
        """Create a PayPal order.

        Args:
            amount: Order amount as float.
            currency: Currency code (default 'USD').

        Returns:
            Dict with order ID or error.
        """
        import requests
        token_result = self.get_access_token()
        if token_result.get("status") != "success":
            return token_result
        access_token = token_result["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{"amount": {"currency_code": currency, "value": f"{amount:.2f}"}}]
        }
        try:
            response = requests.post(f"{self.BASE_URL}/v2/checkout/orders", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("PayPal order created: %s %s", amount, currency)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("PayPal create_order error: %s", e)
            return {"status": "error", "message": str(e)}
