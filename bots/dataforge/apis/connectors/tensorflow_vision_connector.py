"""TensorFlow image classification connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class TensorFlowVisionConnector:
    """TensorFlowVisionConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector with optional model path."""
        self.model_path = os.environ.get("TF_MODEL_PATH", None)
        logger.info("TensorFlowVisionConnector initialized.")

    def classify_image(self, image_path: str, model_path: str = None) -> dict:
        """Classify an image using a TensorFlow model.

        Args:
            image_path: Path to the image file.
            model_path: Optional path to a saved TF model directory.

        Returns:
            Dict with classification results or error.
        """
        try:
            import tensorflow as tf
            import numpy as np
            from PIL import Image
            mp = model_path or self.model_path
            if not mp:
                return {"status": "error", "message": "No TensorFlow model path provided."}
            model = tf.saved_model.load(mp)
            img = Image.open(image_path).resize((224, 224))
            img_array = np.array(img) / 255.0
            img_tensor = tf.expand_dims(img_array, 0)
            predictions = model(img_tensor)
            logger.info("TensorFlow classification completed for %s.", image_path)
            return {"status": "success", "data": predictions.numpy().tolist()}
        except ImportError:
            logger.error("tensorflow library not installed.")
            return {"status": "error", "message": "tensorflow library not installed."}
        except Exception as e:
            logger.error("TensorFlow classify_image error: %s", e)
            return {"status": "error", "message": str(e)}
