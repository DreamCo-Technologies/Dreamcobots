"""GNews API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class GNewsConnector:
    """GNewsConnector for DataForge AI."""

    BASE_URL = "https://gnews.io/api/v4"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("GNEWS_API_KEY", "")
        if not self.api_key:
            logger.warning("GNEWS_API_KEY not set.")

    def search(self, query: str, lang: str = "en", max: int = 10) -> dict:
        """Search news articles on GNews.

        Args:
            query: Search query string.
            lang: Language code (default 'en').
            max: Max results (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "lang": lang, "max": max, "token": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, timeout=30)
            response.raise_for_status()
            logger.info("GNews search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("GNews search error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_top_headlines(self, topic: str = "breaking-news") -> dict:
        """Get top news headlines from GNews.

        Args:
            topic: News topic (default 'breaking-news').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"topic": topic, "token": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/top-headlines", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("GNews get_top_headlines error: %s", e)
            return {"status": "error", "message": str(e)}
