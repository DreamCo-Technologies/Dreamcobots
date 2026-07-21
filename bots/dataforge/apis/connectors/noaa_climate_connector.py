"""NOAA Climate Data Online API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class NOAAClimateConnector:
    """NOAAClimateConnector for DataForge AI."""

    BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("NOAA_API_KEY", "")
        if not self.api_key:
            logger.warning("NOAA_API_KEY not set.")

    def get_data(self, datasetid: str, startdate: str, enddate: str, locationid: str) -> dict:
        """Get climate data from NOAA CDO.

        Args:
            datasetid: Dataset identifier (e.g., 'GHCND').
            startdate: Start date string (YYYY-MM-DD).
            enddate: End date string (YYYY-MM-DD).
            locationid: Location identifier (e.g., 'CITY:US390029').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"token": self.api_key}
        params = {"datasetid": datasetid, "startdate": startdate, "enddate": enddate, "locationid": locationid}
        try:
            response = requests.get(f"{self.BASE_URL}/data", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("NOAA climate data fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NOAA get_data error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_datasets(self) -> dict:
        """Get list of available NOAA CDO datasets.

        Returns:
            API response dict with dataset list or error dict.
        """
        import requests
        headers = {"token": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/datasets", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NOAA get_datasets error: %s", e)
            return {"status": "error", "message": str(e)}
