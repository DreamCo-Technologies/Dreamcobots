"""NewsAPI news connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class NewsAPIConnector:
    """NewsAPIConnector for DataForge AI."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("NEWS_API_KEY", "")
        if not self.api_key:
            logger.warning("NEWS_API_KEY not set.")

    def get_top_headlines(self, country: str = "us", category: str = "general") -> dict:
        """Get top news headlines.

        Args:
            country: Country code (default 'us').
            category: News category (default 'general').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"country": country, "category": category, "apiKey": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/top-headlines", params=params, timeout=30)
            response.raise_for_status()
            logger.info("NewsAPI top headlines fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NewsAPI get_top_headlines error: %s", e)
            return {"status": "error", "message": str(e)}

    def search_everything(self, query: str) -> dict:
        """Search all news articles.

        Args:
            query: Search query string.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "apiKey": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/everything", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NewsAPI search_everything error: %s", e)
            return {"status": "error", "message": str(e)}
