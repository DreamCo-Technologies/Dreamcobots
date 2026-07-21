"""Yahoo Finance API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class YahooFinanceConnector:
    """YahooFinanceConnector for DataForge AI."""

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance"

    def __init__(self):
        """Initialize connector (no API key required)."""
        self.headers = {"User-Agent": "DataForge-AI-Bot/1.0"}

    def get_quote(self, symbol: str) -> dict:
        """Get stock quote from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote",
                params={"symbols": symbol}, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info("Yahoo Finance quote fetched for %s.", symbol)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Yahoo Finance get_quote error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_chart(self, symbol: str, interval: str = "1d", range: str = "1mo") -> dict:
        """Get chart data from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol.
            interval: Data interval (default '1d').
            range: Time range (default '1mo').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(
                f"{self.BASE_URL}/chart/{symbol}",
                params={"interval": interval, "range": range},
                headers=self.headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Yahoo Finance get_chart error: %s", e)
            return {"status": "error", "message": str(e)}
