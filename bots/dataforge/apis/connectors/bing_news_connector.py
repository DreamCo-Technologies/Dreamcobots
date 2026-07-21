"""Microsoft Bing News Search connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class BingNewsConnector:
    """BingNewsConnector for DataForge AI."""

    BASE_URL = "https://api.bing.microsoft.com/v7.0/news"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("BING_NEWS_API_KEY", "")
        if not self.api_key:
            logger.warning("BING_NEWS_API_KEY not set.")

    def search(self, query: str, market: str = "en-US", count: int = 10) -> dict:
        """Search news using Bing News API.

        Args:
            query: Search query string.
            market: Market locale (default 'en-US').
            count: Number of results (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "mkt": market, "count": count}
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Bing News search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Bing News search error: %s", e)
            return {"status": "error", "message": str(e)}
