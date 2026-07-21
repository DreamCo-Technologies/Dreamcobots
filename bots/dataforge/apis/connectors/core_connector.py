"""CORE open access research connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class COREConnector:
    """COREConnector for DataForge AI."""

    BASE_URL = "https://api.core.ac.uk/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("CORE_API_KEY", "")
        if not self.api_key:
            logger.warning("CORE_API_KEY not set.")

    def search_papers(self, query: str, limit: int = 10) -> dict:
        """Search open access papers on CORE.

        Args:
            query: Search query string.
            limit: Max results (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"q": query, "limit": limit}
        try:
            response = requests.get(f"{self.BASE_URL}/search/works", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("CORE paper search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CORE search_papers error: %s", e)
            return {"status": "error", "message": str(e)}
