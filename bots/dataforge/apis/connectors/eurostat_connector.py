"""Eurostat statistics API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class EurostatConnector:
    """EurostatConnector for DataForge AI."""

    BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0"

    def __init__(self):
        """Initialize connector (no API key required)."""
        logger.info("EurostatConnector initialized.")

    def get_dataset(self, dataset_code: str) -> dict:
        """Get a Eurostat dataset by code.

        Args:
            dataset_code: The Eurostat dataset code (e.g., 'nama_10_gdp').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/data/{dataset_code}?format=JSON&lang=EN", timeout=30)
            response.raise_for_status()
            logger.info("Eurostat dataset fetched: %s", dataset_code)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Eurostat get_dataset error: %s", e)
            return {"status": "error", "message": str(e)}

    def search_datasets(self, query: str) -> dict:
        """Search Eurostat datasets.

        Args:
            query: Search query string.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"https://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/search?query={query}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Eurostat search_datasets error: %s", e)
            return {"status": "error", "message": str(e)}
