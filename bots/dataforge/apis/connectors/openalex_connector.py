"""OpenAlex scholarly works API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenAlexConnector:
    """OpenAlexConnector for DataForge AI."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self):
        """Initialize connector with mailto for polite pool."""
        self.mailto = os.environ.get("OPENALEX_MAILTO", "dataforge@example.com")

    def search_works(self, query: str, per_page: int = 10) -> dict:
        """Search OpenAlex works.

        Args:
            query: Search query string.
            per_page: Results per page (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"search": query, "per-page": per_page, "mailto": self.mailto}
        try:
            response = requests.get(f"{self.BASE_URL}/works", params=params, timeout=30)
            response.raise_for_status()
            logger.info("OpenAlex search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenAlex search_works error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_author(self, author_id: str) -> dict:
        """Get author details from OpenAlex.

        Args:
            author_id: The OpenAlex author identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/authors/{author_id}?mailto={self.mailto}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenAlex get_author error: %s", e)
            return {"status": "error", "message": str(e)}
