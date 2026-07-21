"""NASA Open APIs connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class NASAConnector:
    """NASAConnector for DataForge AI."""

    BASE_URL = "https://api.nasa.gov"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")

    def get_apod(self, date: str = None) -> dict:
        """Get Astronomy Picture of the Day from NASA.

        Args:
            date: Optional date string (YYYY-MM-DD). Defaults to today.

        Returns:
            API response dict with APOD data or error dict.
        """
        import requests
        params = {"api_key": self.api_key}
        if date:
            params["date"] = date
        try:
            response = requests.get(f"{self.BASE_URL}/planetary/apod", params=params, timeout=30)
            response.raise_for_status()
            logger.info("NASA APOD fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NASA get_apod error: %s", e)
            return {"status": "error", "message": str(e)}

    def search_images(self, query: str) -> dict:
        """Search NASA image library.

        Args:
            query: Search query string.

        Returns:
            API response dict with images or error dict.
        """
        import requests
        try:
            response = requests.get(f"https://images-api.nasa.gov/search?q={query}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NASA search_images error: %s", e)
            return {"status": "error", "message": str(e)}
