"""World Bank Open Data API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class WorldBankConnector:
    """WorldBankConnector for DataForge AI."""

    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self):
        """Initialize connector (no API key required)."""
        logger.info("WorldBankConnector initialized.")

    def get_indicator(self, country: str, indicator: str) -> dict:
        """Get a World Bank indicator for a country.

        Args:
            country: Country code (e.g., 'US', 'GB').
            indicator: Indicator code (e.g., 'NY.GDP.MKTP.CD').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            url = f"{self.BASE_URL}/country/{country}/indicator/{indicator}?format=json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            logger.info("World Bank indicator %s for %s fetched.", indicator, country)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("World Bank get_indicator error: %s", e)
            return {"status": "error", "message": str(e)}

    def search_indicators(self, query: str) -> dict:
        """Search World Bank indicators.

        Args:
            query: Search query string.

        Returns:
            API response dict with indicators or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/indicators?format=json&per_page=10&mrv=1&search={query}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("World Bank search_indicators error: %s", e)
            return {"status": "error", "message": str(e)}
