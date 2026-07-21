"""Currents API news connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class CurrentsConnector:
    """CurrentsConnector for DataForge AI."""

    BASE_URL = "https://api.currentsapi.services/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("CURRENTS_API_KEY", "")
        if not self.api_key:
            logger.warning("CURRENTS_API_KEY not set.")

    def get_latest_news(self, language: str = "en") -> dict:
        """Get latest news from Currents API.

        Args:
            language: Language code (default 'en').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"language": language, "apiKey": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/latest-news", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Currents API latest news fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Currents get_latest_news error: %s", e)
            return {"status": "error", "message": str(e)}

    def search(self, keywords: str) -> dict:
        """Search news on Currents API.

        Args:
            keywords: Search keywords string.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"keywords": keywords, "apiKey": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Currents search error: %s", e)
            return {"status": "error", "message": str(e)}
