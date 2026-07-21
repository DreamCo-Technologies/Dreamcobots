"""Speechly speech recognition connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class SpeechlyConnector:
    """SpeechlyConnector for DataForge AI."""

    BASE_URL = "https://api.speechly.com/sal/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("SPEECHLY_APP_ID", "")
        if not self.api_key:
            logger.warning("SPEECHLY_APP_ID not set.")

    def transcribe_audio(self, audio_data: bytes) -> dict:
        """Transcribe audio data using Speechly.

        Args:
            audio_data: Raw audio bytes to transcribe.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.post(f"{self.BASE_URL}/stream", data=audio_data, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Speechly audio transcription completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Speechly transcribe error: %s", e)
            return {"status": "error", "message": str(e)}
