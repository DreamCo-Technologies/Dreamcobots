"""DeepFace facial analysis connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class DeepFaceConnector:
    """DeepFaceConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector with default actions."""
        self.default_actions = ["emotion", "age", "gender", "race"]
        logger.info("DeepFaceConnector initialized.")

    def analyze(self, image_path: str, actions: list = None) -> dict:
        """Analyze a face image using DeepFace.

        Args:
            image_path: Path to the image file.
            actions: List of analysis actions (default: emotion, age, gender, race).

        Returns:
            Dict with analysis results or error.
        """
        try:
            from deepface import DeepFace
            acts = actions or self.default_actions
            result = DeepFace.analyze(img_path=image_path, actions=acts)
            logger.info("DeepFace analysis completed for %s.", image_path)
            return {"status": "success", "data": result}
        except ImportError:
            logger.error("deepface library not installed.")
            return {"status": "error", "message": "deepface library not installed."}
        except Exception as e:
            logger.error("DeepFace analyze error: %s", e)
            return {"status": "error", "message": str(e)}
