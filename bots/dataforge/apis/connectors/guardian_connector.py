"""The Guardian news API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class GuardianConnector:
    """GuardianConnector for DataForge AI."""

    BASE_URL = "https://content.guardianapis.com"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("GUARDIAN_API_KEY", "test")

    def search(self, query: str, page: int = 1) -> dict:
        """Search The Guardian articles.

        Args:
            query: Search query string.
            page: Page number (default 1).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "page": page, "api-key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Guardian search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Guardian search error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_section(self, section_id: str) -> dict:
        """Get articles from a Guardian section.

        Args:
            section_id: Section identifier (e.g., 'technology').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"api-key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/{section_id}", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Guardian get_section error: %s", e)
            return {"status": "error", "message": str(e)}
