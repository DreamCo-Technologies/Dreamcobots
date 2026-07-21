"""CoinGecko cryptocurrency data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class CoinGeckoConnector:
    """CoinGeckoConnector for DataForge AI."""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        """Initialize connector (no API key required for basic use)."""
        self.api_key = os.environ.get("COINGECKO_API_KEY", "")

    def get_coin_price(self, ids: str, vs_currencies: str = "usd") -> dict:
        """Get current price of cryptocurrencies.

        Args:
            ids: Comma-separated coin IDs (e.g., 'bitcoin,ethereum').
            vs_currencies: Currency to compare against (default 'usd').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"ids": ids, "vs_currencies": vs_currencies}
        try:
            response = requests.get(f"{self.BASE_URL}/simple/price", params=params, timeout=30)
            response.raise_for_status()
            logger.info("CoinGecko price fetched for: %s", ids)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CoinGecko get_coin_price error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_markets(self, vs_currency: str = "usd", per_page: int = 10) -> dict:
        """Get cryptocurrency market data.

        Args:
            vs_currency: Currency to compare (default 'usd').
            per_page: Results per page (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"vs_currency": vs_currency, "per_page": per_page, "page": 1}
        try:
            response = requests.get(f"{self.BASE_URL}/coins/markets", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CoinGecko get_markets error: %s", e)
            return {"status": "error", "message": str(e)}
