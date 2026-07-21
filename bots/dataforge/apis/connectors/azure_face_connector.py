"""Azure Face API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class AzureFaceConnector:
    """AzureFaceConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector, reading endpoint and key from environment."""
        self.endpoint = os.environ.get("AZURE_FACE_ENDPOINT", "")
        self.api_key = os.environ.get("AZURE_FACE_API_KEY", "")
        if not self.endpoint or not self.api_key:
            logger.warning("AZURE_FACE_ENDPOINT or AZURE_FACE_API_KEY not set.")

    def detect_face(self, image_url: str) -> dict:
        """Detect faces in an image using Azure Face API.

        Args:
            image_url: URL of the image to analyze.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Ocp-Apim-Subscription-Key": self.api_key, "Content-Type": "application/json"}
        payload = {"url": image_url}
        try:
            response = requests.post(
                f"{self.endpoint}/face/v1.0/detect?returnFaceAttributes=age,gender,emotion",
                json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            logger.info("Azure Face detection completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Azure Face detect error: %s", e)
            return {"status": "error", "message": str(e)}
