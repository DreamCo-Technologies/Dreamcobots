"""Stability AI image generation connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class StabilityAIConnector:
    """StabilityAIConnector for DataForge AI."""

    BASE_URL = "https://api.stability.ai/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("STABILITY_API_KEY", "")
        if not self.api_key:
            logger.warning("STABILITY_API_KEY not set.")

    def generate_image(self, prompt: str, engine: str = "stable-diffusion-xl-1024-v1-0") -> dict:
        """Generate an image using Stability AI API.

        Args:
            prompt: Text prompt for image generation.
            engine: Engine identifier (default stable-diffusion-xl-1024-v1-0).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"text_prompts": [{"text": prompt}], "cfg_scale": 7, "samples": 1, "steps": 30}
        try:
            url = f"{self.BASE_URL}/generation/{engine}/text-to-image"
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            logger.info("Stability AI image generated with engine %s.", engine)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Stability AI error: %s", e)
            return {"status": "error", "message": str(e)}
