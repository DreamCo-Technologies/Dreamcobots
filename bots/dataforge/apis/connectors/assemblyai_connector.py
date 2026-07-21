"""AssemblyAI transcription connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class AssemblyAIConnector:
    """AssemblyAIConnector for DataForge AI."""

    BASE_URL = "https://api.assemblyai.com/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("ASSEMBLYAI_API_KEY", "")
        if not self.api_key:
            logger.warning("ASSEMBLYAI_API_KEY not set.")

    def transcribe(self, audio_url: str) -> dict:
        """Submit audio URL for transcription via AssemblyAI.

        Args:
            audio_url: URL of the audio file to transcribe.

        Returns:
            API response dict with transcript ID or error dict.
        """
        import requests
        headers = {"authorization": self.api_key, "content-type": "application/json"}
        payload = {"audio_url": audio_url}
        try:
            response = requests.post(f"{self.BASE_URL}/transcript", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("AssemblyAI transcription submitted.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("AssemblyAI transcribe error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_transcript(self, transcript_id: str) -> dict:
        """Get transcription result from AssemblyAI.

        Args:
            transcript_id: The transcript job identifier.

        Returns:
            API response dict with transcript or error dict.
        """
        import requests
        headers = {"authorization": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/transcript/{transcript_id}", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("AssemblyAI get_transcript error: %s", e)
            return {"status": "error", "message": str(e)}
