"""Finnhub financial data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class FinnhubConnector:
    """FinnhubConnector for DataForge AI."""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("FINNHUB_API_KEY", "")
        if not self.api_key:
            logger.warning("FINNHUB_API_KEY not set.")

    def get_quote(self, symbol: str) -> dict:
        """Get real-time stock quote from Finnhub.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/quote", params={"symbol": symbol, "token": self.api_key}, timeout=30)
            response.raise_for_status()
            logger.info("Finnhub quote fetched for %s.", symbol)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Finnhub get_quote error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_company_profile(self, symbol: str) -> dict:
        """Get company profile from Finnhub.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/stock/profile2", params={"symbol": symbol, "token": self.api_key}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Finnhub get_company_profile error: %s", e)
            return {"status": "error", "message": str(e)}
