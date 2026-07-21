"""ArXiv open access paper search connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class ArXivConnector:
    """ArXivConnector for DataForge AI."""

    BASE_URL = "http://export.arxiv.org/api"

    def __init__(self):
        """Initialize connector (no API key required)."""
        logger.info("ArXivConnector initialized.")

    def search(self, query: str, max_results: int = 10) -> dict:
        """Search ArXiv papers.

        Args:
            query: Search query string.
            max_results: Maximum number of results (default 10).

        Returns:
            API response dict with papers or error dict.
        """
        import requests
        params = {"search_query": query, "max_results": max_results}
        try:
            response = requests.get(f"{self.BASE_URL}/query", params=params, timeout=30)
            response.raise_for_status()
            logger.info("ArXiv search completed for: %s", query)
            return {"status": "success", "data": response.text, "format": "atom"}
        except requests.RequestException as e:
            logger.error("ArXiv search error: %s", e)
            return {"status": "error", "message": str(e)}
