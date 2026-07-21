"""Semantic Scholar API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class SemanticScholarConnector:
    """SemanticScholarConnector for DataForge AI."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self):
        """Initialize connector with optional API key from environment."""
        self.api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

    def search_papers(self, query: str, limit: int = 10) -> dict:
        """Search academic papers on Semantic Scholar.

        Args:
            query: Search query string.
            limit: Max results to return (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"query": query, "limit": limit, "fields": "title,authors,year,abstract"}
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        try:
            response = requests.get(f"{self.BASE_URL}/paper/search", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Semantic Scholar search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Semantic Scholar search_papers error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_paper(self, paper_id: str) -> dict:
        """Get details for a specific paper from Semantic Scholar.

        Args:
            paper_id: The paper identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        try:
            response = requests.get(f"{self.BASE_URL}/paper/{paper_id}", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Semantic Scholar get_paper error: %s", e)
            return {"status": "error", "message": str(e)}
