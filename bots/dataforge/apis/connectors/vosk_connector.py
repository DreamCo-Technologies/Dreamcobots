"""Vosk offline speech recognition connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class VoskConnector:
    """VoskConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector with default model path."""
        self.model_path = os.environ.get("VOSK_MODEL_PATH", "model")
        logger.info("VoskConnector initialized with model path: %s", self.model_path)

    def transcribe_audio(self, audio_path: str, model_path: str = "model") -> dict:
        """Transcribe audio using Vosk offline model.

        Args:
            audio_path: Path to the audio file.
            model_path: Path to the Vosk model directory.

        Returns:
            Dict with transcript or error message.
        """
        try:
            import vosk
            import wave
            import json
            model = vosk.Model(model_path)
            with wave.open(audio_path, "rb") as wf:
                rec = vosk.KaldiRecognizer(model, wf.getframerate())
                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        results.append(json.loads(rec.Result()))
                results.append(json.loads(rec.FinalResult()))
            logger.info("Vosk transcription completed for %s.", audio_path)
            return {"status": "success", "data": results}
        except ImportError:
            logger.error("Vosk library not installed.")
            return {"status": "error", "message": "vosk library not installed."}
        except Exception as e:
            logger.error("Vosk transcription error: %s", e)
            return {"status": "error", "message": str(e)}
