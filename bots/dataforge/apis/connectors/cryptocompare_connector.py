"""CryptoCompare cryptocurrency data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class CryptoCompareConnector:
    """CryptoCompareConnector for DataForge AI."""

    BASE_URL = "https://min-api.cryptocompare.com/data"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("CRYPTOCOMPARE_API_KEY", "")
        if not self.api_key:
            logger.warning("CRYPTOCOMPARE_API_KEY not set.")

    def get_price(self, fsym: str, tsyms: str = "USD") -> dict:
        """Get current cryptocurrency price.

        Args:
            fsym: From symbol (e.g., 'BTC').
            tsyms: To symbols (default 'USD').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"fsym": fsym, "tsyms": tsyms}
        if self.api_key:
            params["api_key"] = self.api_key
        try:
            response = requests.get(f"{self.BASE_URL}/price", params=params, timeout=30)
            response.raise_for_status()
            logger.info("CryptoCompare price fetched for %s.", fsym)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CryptoCompare get_price error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_historical_daily(self, fsym: str, tsym: str = "USD", limit: int = 30) -> dict:
        """Get historical daily price data.

        Args:
            fsym: From symbol (e.g., 'BTC').
            tsym: To symbol (default 'USD').
            limit: Number of data points (default 30).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"fsym": fsym, "tsym": tsym, "limit": limit}
        try:
            response = requests.get(f"{self.BASE_URL}/histoday", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CryptoCompare get_historical_daily error: %s", e)
            return {"status": "error", "message": str(e)}
