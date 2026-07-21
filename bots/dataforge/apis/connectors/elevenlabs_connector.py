"""ElevenLabs TTS connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class ElevenLabsConnector:
    """ElevenLabsConnector for DataForge AI."""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not set.")

    def text_to_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> dict:
        """Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech.
            voice_id: ElevenLabs voice identifier.

        Returns:
            Dict with audio bytes or error.
        """
        import requests
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {"text": text, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        try:
            response = requests.post(f"{self.BASE_URL}/text-to-speech/{voice_id}", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("ElevenLabs TTS completed for voice %s.", voice_id)
            return {"status": "success", "audio_bytes": len(response.content), "content_type": "audio/mpeg"}
        except requests.RequestException as e:
            logger.error("ElevenLabs TTS error: %s", e)
            return {"status": "error", "message": str(e)}

    def list_voices(self) -> dict:
        """List available voices on ElevenLabs.

        Returns:
            Dict with list of voices or error.
        """
        import requests
        headers = {"xi-api-key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/voices", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("ElevenLabs list_voices error: %s", e)
            return {"status": "error", "message": str(e)}
