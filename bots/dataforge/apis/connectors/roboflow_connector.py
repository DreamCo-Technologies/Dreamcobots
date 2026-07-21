"""Roboflow computer vision inference connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class RoboflowConnector:
    """RoboflowConnector for DataForge AI."""

    BASE_URL = "https://detect.roboflow.com"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("ROBOFLOW_API_KEY", "")
        if not self.api_key:
            logger.warning("ROBOFLOW_API_KEY not set.")

    def infer(self, model_id: str, image_path: str) -> dict:
        """Run inference on an image using Roboflow.

        Args:
            model_id: The Roboflow model identifier (model/version).
            image_path: Path to the image file.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            headers = {"api-key": self.api_key}
            with open(image_path, "rb") as f:
                response = requests.post(
                    f"{self.BASE_URL}/{model_id}",
                    files={"file": f},
                    headers=headers,
                    timeout=30
                )
            response.raise_for_status()
            logger.info("Roboflow inference completed for model %s.", model_id)
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error("Roboflow infer error: %s", e)
            return {"status": "error", "message": str(e)}
