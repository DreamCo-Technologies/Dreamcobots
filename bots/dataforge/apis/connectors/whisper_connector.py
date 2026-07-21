"""OpenAI Whisper transcription connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class WhisperConnector:
    """WhisperConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector with default model size."""
        self.model_size = os.environ.get("WHISPER_MODEL_SIZE", "base")
        logger.info("WhisperConnector initialized with model size: %s", self.model_size)

    def transcribe(self, audio_path: str, model_size: str = "base") -> dict:
        """Transcribe audio using OpenAI Whisper.

        Args:
            audio_path: Path to the audio file.
            model_size: Whisper model size (tiny/base/small/medium/large).

        Returns:
            Dict with transcription text or error.
        """
        try:
            import whisper
            model = whisper.load_model(model_size)
            result = model.transcribe(audio_path)
            logger.info("Whisper transcription completed for %s.", audio_path)
            return {"status": "success", "text": result.get("text", ""), "data": result}
        except ImportError:
            logger.error("openai-whisper library not installed.")
            return {"status": "error", "message": "openai-whisper library not installed."}
        except Exception as e:
            logger.error("Whisper transcribe error: %s", e)
            return {"status": "error", "message": str(e)}
