"""Google Cloud Vision API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class GoogleVisionConnector:
    """GoogleVisionConnector for DataForge AI."""

    BASE_URL = "https://vision.googleapis.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("GOOGLE_VISION_API_KEY", "")
        if not self.api_key:
            logger.warning("GOOGLE_VISION_API_KEY not set.")

    def annotate_image(self, image_url: str, features: list) -> dict:
        """Annotate an image using Google Cloud Vision API.

        Args:
            image_url: URL of the image to annotate.
            features: List of feature dicts (e.g., [{"type": "FACE_DETECTION"}]).

        Returns:
            API response dict or error dict.
        """
        import requests
        payload = {"requests": [{"image": {"source": {"imageUri": image_url}}, "features": features}]}
        try:
            response = requests.post(f"{self.BASE_URL}/images:annotate?key={self.api_key}", json=payload, timeout=30)
            response.raise_for_status()
            logger.info("Google Vision annotation completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Google Vision error: %s", e)
            return {"status": "error", "message": str(e)}
