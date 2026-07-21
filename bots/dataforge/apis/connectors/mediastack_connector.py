"""MediaStack news API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class MediaStackConnector:
    """MediaStackConnector for DataForge AI."""

    BASE_URL = "https://api.mediastack.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("MEDIASTACK_API_KEY", "")
        if not self.api_key:
            logger.warning("MEDIASTACK_API_KEY not set.")

    def get_live_news(self, keywords: str = None, languages: str = "en") -> dict:
        """Get live news from MediaStack.

        Args:
            keywords: Optional search keywords.
            languages: Language codes (default 'en').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"access_key": self.api_key, "languages": languages}
        if keywords:
            params["keywords"] = keywords
        try:
            response = requests.get(f"{self.BASE_URL}/news", params=params, timeout=30)
            response.raise_for_status()
            logger.info("MediaStack live news fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("MediaStack get_live_news error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_sources(self) -> dict:
        """Get list of news sources from MediaStack.

        Returns:
            API response dict with sources or error dict.
        """
        import requests
        params = {"access_key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/sources", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("MediaStack get_sources error: %s", e)
            return {"status": "error", "message": str(e)}
