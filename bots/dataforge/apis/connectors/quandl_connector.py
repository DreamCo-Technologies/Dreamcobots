"""Quandl/Nasdaq Data Link financial data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class QuandlConnector:
    """QuandlConnector for DataForge AI."""

    BASE_URL = "https://data.nasdaq.com/api/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("QUANDL_API_KEY", "")
        if not self.api_key:
            logger.warning("QUANDL_API_KEY not set.")

    def get_dataset(self, database_code: str, dataset_code: str) -> dict:
        """Get a Quandl dataset.

        Args:
            database_code: Database code (e.g., 'WIKI').
            dataset_code: Dataset code (e.g., 'AAPL').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"api_key": self.api_key}
        try:
            response = requests.get(
                f"{self.BASE_URL}/datasets/{database_code}/{dataset_code}/data.json",
                params=params, timeout=30)
            response.raise_for_status()
            logger.info("Quandl dataset fetched: %s/%s", database_code, dataset_code)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Quandl get_dataset error: %s", e)
            return {"status": "error", "message": str(e)}
