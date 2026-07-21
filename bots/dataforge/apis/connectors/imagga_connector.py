"""Imagga image tagging connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class ImaggaConnector:
    """ImaggaConnector for DataForge AI."""

    BASE_URL = "https://api.imagga.com/v2"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.api_key = os.environ.get("IMAGGA_API_KEY", "")
        self.api_secret = os.environ.get("IMAGGA_API_SECRET", "")
        if not self.api_key or not self.api_secret:
            logger.warning("IMAGGA_API_KEY or IMAGGA_API_SECRET not set.")

    def tag_image(self, image_url: str) -> dict:
        """Tag an image using Imagga.

        Args:
            image_url: URL of the image to tag.

        Returns:
            API response dict with tags or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/tags?image_url={image_url}", auth=(self.api_key, self.api_secret), timeout=30)
            response.raise_for_status()
            logger.info("Imagga tagging completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Imagga tag_image error: %s", e)
            return {"status": "error", "message": str(e)}

    def categorize(self, image_url: str) -> dict:
        """Categorize an image using Imagga.

        Args:
            image_url: URL of the image to categorize.

        Returns:
            API response dict with categories or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/categories/personal_photos?image_url={image_url}", auth=(self.api_key, self.api_secret), timeout=30)
            response.raise_for_status()
            logger.info("Imagga categorization completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Imagga categorize error: %s", e)
            return {"status": "error", "message": str(e)}
