"""Clarifai AI vision API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class ClarifaiConnector:
    """ClarifaiConnector for DataForge AI."""

    BASE_URL = "https://api.clarifai.com/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("CLARIFAI_API_KEY", "")
        if not self.api_key:
            logger.warning("CLARIFAI_API_KEY not set.")

    def predict(self, model_id: str, image_url: str) -> dict:
        """Run prediction on an image using Clarifai.

        Args:
            model_id: Clarifai model identifier.
            image_url: URL of the image to analyze.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload = {"inputs": [{"data": {"image": {"url": image_url}}}]}
        try:
            response = requests.post(f"{self.BASE_URL}/models/{model_id}/outputs", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Clarifai prediction completed for model %s.", model_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Clarifai predict error: %s", e)
            return {"status": "error", "message": str(e)}
