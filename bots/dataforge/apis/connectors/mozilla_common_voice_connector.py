"""Mozilla Common Voice API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class MozillaCommonVoiceConnector:
    """MozillaCommonVoiceConnector for DataForge AI."""

    BASE_URL = "https://commonvoice.mozilla.org/api/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("MOZILLA_CV_TOKEN", "")
        if not self.api_key:
            logger.warning("MOZILLA_CV_TOKEN not set.")

    def get_clips(self, language: str = "en") -> dict:
        """Get voice clips for a language from Mozilla Common Voice.

        Args:
            language: Language code (default 'en').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(f"{self.BASE_URL}/{language}/clips", headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Mozilla Common Voice clips fetched for language %s.", language)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Mozilla Common Voice get_clips error: %s", e)
            return {"status": "error", "message": str(e)}

    def submit_clip(self, audio_path: str, sentence: str, language: str = "en") -> dict:
        """Submit a voice clip to Mozilla Common Voice.

        Args:
            audio_path: Path to the audio file.
            sentence: The sentence spoken in the clip.
            language: BCP-47 language code for the clip (default: 'en').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            with open(audio_path, "rb") as f:
                response = requests.post(
                    f"{self.BASE_URL}/{language}/clips",
                    files={"audio": f},
                    data={"sentence": sentence},
                    headers=headers,
                    timeout=30
                )
            response.raise_for_status()
            logger.info("Mozilla Common Voice clip submitted.")
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error("Mozilla Common Voice submit_clip error: %s", e)
            return {"status": "error", "message": str(e)}
