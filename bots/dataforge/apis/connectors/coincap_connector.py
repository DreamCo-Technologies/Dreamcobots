"""CoinCap cryptocurrency market data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class CoinCapConnector:
    """CoinCapConnector for DataForge AI."""

    BASE_URL = "https://api.coincap.io/v2"

    def __init__(self):
        """Initialize connector (no API key required for basic use)."""
        self.api_key = os.environ.get("COINCAP_API_KEY", "")

    def get_assets(self, limit: int = 10) -> dict:
        """Get list of cryptocurrency assets.

        Args:
            limit: Number of assets to return (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/assets", params={"limit": limit}, timeout=30)
            response.raise_for_status()
            logger.info("CoinCap assets fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CoinCap get_assets error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_asset(self, asset_id: str) -> dict:
        """Get details for a specific cryptocurrency asset.

        Args:
            asset_id: The asset identifier (e.g., 'bitcoin').

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/assets/{asset_id}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("CoinCap get_asset error: %s", e)
            return {"status": "error", "message": str(e)}
