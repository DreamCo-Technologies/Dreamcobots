"""Picovoice wake word detection connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class PicovoiceConnector:
    """PicovoiceConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.access_key = os.environ.get("PICOVOICE_ACCESS_KEY", "")
        if not self.access_key:
            logger.warning("PICOVOICE_ACCESS_KEY not set.")

    def wake_word_detect(self, audio_frame: list) -> dict:
        """Detect wake word in an audio frame using Picovoice Porcupine.

        Args:
            audio_frame: List of PCM audio samples (16-bit, 16kHz mono).

        Returns:
            Dict with detected keyword index or error.
        """
        try:
            import pvporcupine
            porcupine = pvporcupine.create(access_key=self.access_key, keywords=["porcupine"])
            keyword_index = porcupine.process(audio_frame)
            porcupine.delete()
            logger.info("Picovoice wake word detection completed. keyword_index=%s", keyword_index)
            return {"status": "success", "keyword_index": keyword_index}
        except ImportError:
            logger.error("pvporcupine library not installed.")
            return {"status": "error", "message": "pvporcupine library not installed."}
        except Exception as e:
            logger.error("Picovoice wake_word_detect error: %s", e)
            return {"status": "error", "message": str(e)}
