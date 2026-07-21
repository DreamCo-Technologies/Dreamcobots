"""Deepgram speech-to-text connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class DeepgramConnector:
    """DeepgramConnector for DataForge AI."""

    BASE_URL = "https://api.deepgram.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("DEEPGRAM_API_KEY", "")
        if not self.api_key:
            logger.warning("DEEPGRAM_API_KEY not set.")

    def transcribe_url(self, audio_url: str, model: str = "nova-2") -> dict:
        """Transcribe audio from a URL using Deepgram.

        Args:
            audio_url: URL of the audio file to transcribe.
            model: Deepgram model identifier (default 'nova-2').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"}
        payload = {"url": audio_url}
        try:
            response = requests.post(
                f"{self.BASE_URL}/listen?model={model}",
                json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            logger.info("Deepgram transcription completed with model %s.", model)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Deepgram transcribe error: %s", e)
            return {"status": "error", "message": str(e)}
