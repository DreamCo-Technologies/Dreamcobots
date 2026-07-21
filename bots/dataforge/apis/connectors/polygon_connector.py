"""Polygon.io stock market data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class PolygonConnector:
    """PolygonConnector for DataForge AI."""

    BASE_URL = "https://api.polygon.io/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("POLYGON_API_KEY", "")
        if not self.api_key:
            logger.warning("POLYGON_API_KEY not set.")

    def get_ticker_details(self, ticker: str) -> dict:
        """Get details for a stock ticker.

        Args:
            ticker: The stock ticker symbol.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"https://api.polygon.io/v3/reference/tickers/{ticker}",
                params={"apiKey": self.api_key}, timeout=30)
            response.raise_for_status()
            logger.info("Polygon ticker details fetched for %s.", ticker)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Polygon get_ticker_details error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_aggregates(self, ticker: str, from_date: str, to_date: str) -> dict:
        """Get aggregate bars for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            from_date: Start date (YYYY-MM-DD).
            to_date: End date (YYYY-MM-DD).

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(
                f"{self.BASE_URL}/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}",
                params={"apiKey": self.api_key}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Polygon get_aggregates error: %s", e)
            return {"status": "error", "message": str(e)}
