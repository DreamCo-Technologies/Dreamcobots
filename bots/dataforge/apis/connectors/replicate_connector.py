"""Replicate API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class ReplicateConnector:
    """ReplicateConnector for DataForge AI."""

    BASE_URL = "https://api.replicate.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("REPLICATE_API_TOKEN", "")
        if not self.api_key:
            logger.warning("REPLICATE_API_TOKEN not set.")

    def run(self, model_version: str, inputs: dict) -> dict:
        """Run a model on Replicate.

        Args:
            model_version: Full model version string (owner/name:version).
            inputs: Dict of input parameters for the model.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"}
        payload = {"version": model_version, "input": inputs}
        try:
            response = requests.post(f"{self.BASE_URL}/predictions", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Replicate prediction created for model %s.", model_version)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Replicate error: %s", e)
            return {"status": "error", "message": str(e)}
