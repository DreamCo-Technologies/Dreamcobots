"""Fixer.io currency exchange rate connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class FixerConnector:
    """FixerConnector for DataForge AI."""

    BASE_URL = "https://data.fixer.io/api"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("FIXER_API_KEY", "")
        if not self.api_key:
            logger.warning("FIXER_API_KEY not set.")

    def get_latest_rates(self, base: str = "USD") -> dict:
        """Get latest exchange rates.

        Args:
            base: Base currency (default 'USD').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/latest", params={"access_key": self.api_key, "base": base}, timeout=30)
            response.raise_for_status()
            logger.info("Fixer latest rates fetched for base: %s", base)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Fixer get_latest_rates error: %s", e)
            return {"status": "error", "message": str(e)}

    def convert(self, from_currency: str, to_currency: str, amount: float) -> dict:
        """Convert currency using Fixer.io.

        Args:
            from_currency: Source currency code.
            to_currency: Target currency code.
            amount: Amount to convert.

        Returns:
            API response dict with conversion result or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/convert",
                params={"access_key": self.api_key, "from": from_currency, "to": to_currency, "amount": amount}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Fixer convert error: %s", e)
            return {"status": "error", "message": str(e)}
