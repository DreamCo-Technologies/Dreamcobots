"""Alpha Vantage financial data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class AlphaVantageConnector:
    """AlphaVantageConnector for DataForge AI."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set.")

    def get_stock_quote(self, symbol: str) -> dict:
        """Get real-time stock quote.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key}
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            logger.info("Alpha Vantage quote fetched for %s.", symbol)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Alpha Vantage get_stock_quote error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_daily(self, symbol: str) -> dict:
        """Get daily time series for a stock.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": self.api_key}
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Alpha Vantage get_daily error: %s", e)
            return {"status": "error", "message": str(e)}
