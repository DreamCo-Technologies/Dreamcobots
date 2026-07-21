"""CrossRef scholarly metadata API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class CrossRefConnector:
    """CrossRefConnector for DataForge AI."""

    BASE_URL = "https://api.crossref.org"

    def __init__(self):
        """Initialize connector with mailto for polite pool access."""
        self.mailto = os.environ.get("CROSSREF_MAILTO", "dataforge@example.com")

    def search_works(self, query: str, rows: int = 10) -> dict:
        """Search CrossRef works (papers, books, etc.).

        Args:
            query: Search query string.
            rows: Max results to return (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"query": query, "rows": rows, "mailto": self.mailto}
        try:
            response = requests.get(f"{self.BASE_URL}/works", params=params, timeout=30)
            response.raise_for_status()
            logger.info("CrossRef search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CrossRef search_works error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_work(self, doi: str) -> dict:
        """Get a specific work by DOI from CrossRef.

        Args:
            doi: Digital Object Identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/works/{doi}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CrossRef get_work error: %s", e)
            return {"status": "error", "message": str(e)}
