"""Open Exchange Rates connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenExchangeRatesConnector:
    """OpenExchangeRatesConnector for DataForge AI."""

    BASE_URL = "https://openexchangerates.org/api"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("OPEN_EXCHANGE_RATES_APP_ID", "")
        if not self.api_key:
            logger.warning("OPEN_EXCHANGE_RATES_APP_ID not set.")

    def get_latest(self, base: str = "USD") -> dict:
        """Get latest exchange rates.

        Args:
            base: Base currency (default 'USD').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/latest.json", params={"app_id": self.api_key, "base": base}, timeout=30)
            response.raise_for_status()
            logger.info("Open Exchange Rates latest fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Open Exchange Rates get_latest error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_currencies(self) -> dict:
        """Get list of supported currencies.

        Returns:
            API response dict with currency list or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/currencies.json", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Open Exchange Rates get_currencies error: %s", e)
            return {"status": "error", "message": str(e)}
