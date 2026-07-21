"""Face++ facial recognition connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class FacePPConnector:
    """FacePPConnector for DataForge AI."""

    BASE_URL = "https://api-us.faceplusplus.com/facepp/v3"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.api_key = os.environ.get("FACEPP_API_KEY", "")
        self.api_secret = os.environ.get("FACEPP_API_SECRET", "")
        if not self.api_key or not self.api_secret:
            logger.warning("FACEPP_API_KEY or FACEPP_API_SECRET not set.")

    def detect(self, image_url: str) -> dict:
        """Detect faces in an image using Face++.

        Args:
            image_url: URL of the image to analyze.

        Returns:
            API response dict or error dict.
        """
        import requests
        payload = {"api_key": self.api_key, "api_secret": self.api_secret, "image_url": image_url}
        try:
            response = requests.post(f"{self.BASE_URL}/detect", data=payload, timeout=30)
            response.raise_for_status()
            logger.info("Face++ detection completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Face++ detect error: %s", e)
            return {"status": "error", "message": str(e)}

    def compare(self, image_url1: str, image_url2: str) -> dict:
        """Compare two faces using Face++.

        Args:
            image_url1: URL of the first image.
            image_url2: URL of the second image.

        Returns:
            API response dict with confidence score or error dict.
        """
        import requests
        payload = {"api_key": self.api_key, "api_secret": self.api_secret, "image_url1": image_url1, "image_url2": image_url2}
        try:
            response = requests.post(f"{self.BASE_URL}/compare", data=payload, timeout=30)
            response.raise_for_status()
            logger.info("Face++ comparison completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Face++ compare error: %s", e)
            return {"status": "error", "message": str(e)}
