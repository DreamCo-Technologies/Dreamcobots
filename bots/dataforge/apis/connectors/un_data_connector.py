"""UN Data API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class UNDataConnector:
    """UNDataConnector for DataForge AI."""

    BASE_URL = "https://data.un.org/ws/rest"

    def __init__(self):
        """Initialize connector (no API key required)."""
        logger.info("UNDataConnector initialized.")

    def get_dataset(self, series_code: str) -> dict:
        """Get a UN dataset by series code.

        Args:
            series_code: The UN data series code.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/data/{series_code}?format=json", timeout=30)
            response.raise_for_status()
            logger.info("UN data fetched for series: %s", series_code)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("UN Data get_dataset error: %s", e)
            return {"status": "error", "message": str(e)}

    def search(self, query: str) -> dict:
        """Search UN Data.

        Args:
            query: Search query string.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/dataflow?q={query}&format=json", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("UN Data search error: %s", e)
            return {"status": "error", "message": str(e)}
