"""Data.gov open data API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class DataGovConnector:
    """DataGovConnector for DataForge AI."""

    BASE_URL = "https://catalog.data.gov/api/3"

    def __init__(self):
        """Initialize connector with optional API key from environment."""
        self.api_key = os.environ.get("DATAGOV_API_KEY", "")

    def search_datasets(self, query: str, limit: int = 10) -> dict:
        """Search datasets on Data.gov.

        Args:
            query: Search query string.
            limit: Maximum number of results to return (default 10).

        Returns:
            API response dict with datasets or error dict.
        """
        import requests
        params = {"q": query, "rows": limit, "fq": "res_format:JSON"}
        if self.api_key:
            params["api_key"] = self.api_key
        try:
            response = requests.get(f"{self.BASE_URL}/action/package_search", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Data.gov search completed for query: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Data.gov search_datasets error: %s", e)
            return {"status": "error", "message": str(e)}
