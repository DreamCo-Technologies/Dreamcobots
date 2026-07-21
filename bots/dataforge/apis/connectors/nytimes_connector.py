"""New York Times API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class NYTimesConnector:
    """NYTimesConnector for DataForge AI."""

    BASE_URL = "https://api.nytimes.com/svc"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("NYTIMES_API_KEY", "")
        if not self.api_key:
            logger.warning("NYTIMES_API_KEY not set.")

    def search_articles(self, query: str, page: int = 0) -> dict:
        """Search NY Times articles.

        Args:
            query: Search query string.
            page: Page number (default 0).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "page": page, "api-key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/search/v2/articlesearch.json", params=params, timeout=30)
            response.raise_for_status()
            logger.info("NYTimes article search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NYTimes search_articles error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_top_stories(self, section: str = "home") -> dict:
        """Get NY Times top stories for a section.

        Args:
            section: News section (default 'home').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/topstories/v2/{section}.json",
                params={"api-key": self.api_key}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NYTimes get_top_stories error: %s", e)
            return {"status": "error", "message": str(e)}
