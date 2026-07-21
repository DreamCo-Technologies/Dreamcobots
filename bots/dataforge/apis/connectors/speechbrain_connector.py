"""SpeechBrain emotion classification connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class SpeechBrainConnector:
    """SpeechBrainConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector with default model source."""
        self.model_source = os.environ.get("SPEECHBRAIN_MODEL", "speechbrain/emotion-recognition-wav2vec2-IEMOCAP")
        logger.info("SpeechBrainConnector initialized.")

    def classify_emotion(self, audio_path: str) -> dict:
        """Classify emotion in audio file using SpeechBrain.

        Args:
            audio_path: Path to the audio file to classify.

        Returns:
            Dict with emotion classification result or error.
        """
        try:
            from speechbrain.pretrained import EncoderClassifier
            classifier = EncoderClassifier.from_hparams(source=self.model_source)
            out_prob, score, index, text_lab = classifier.classify_file(audio_path)
            logger.info("SpeechBrain emotion classified: %s", text_lab)
            return {"status": "success", "emotion": str(text_lab), "score": float(score)}
        except ImportError:
            logger.error("speechbrain library not installed.")
            return {"status": "error", "message": "speechbrain library not installed."}
        except Exception as e:
            logger.error("SpeechBrain classify_emotion error: %s", e)
            return {"status": "error", "message": str(e)}
