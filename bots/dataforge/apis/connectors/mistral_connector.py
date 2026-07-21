"""Mistral AI API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class MistralConnector:
    """MistralConnector: Mistral AI API connector for DataForge AI."""

    BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("MISTRAL_API_KEY", "")
        if not self.api_key:
            logger.warning("MISTRAL_API_KEY not set.")

    def chat(self, messages: list, model: str = "mistral-tiny") -> dict:
        """Chat with Mistral AI API.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model identifier (default 'mistral-tiny').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages}
        try:
            response = requests.post(f"{self.BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Mistral chat completed with model %s.", model)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Mistral chat error: %s", e)
            return {"status": "error", "message": str(e)}
