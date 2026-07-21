"""OpenCV face detection connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenCVConnector:
    """OpenCVConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector with default Haar cascade path."""
        self.cascade_path = os.environ.get("OPENCV_CASCADE_PATH", "haarcascade_frontalface_default.xml")
        logger.info("OpenCVConnector initialized.")

    def detect_faces_haar(self, image_path: str) -> dict:
        """Detect faces using OpenCV Haar Cascade classifier.

        Args:
            image_path: Path to the image file.

        Returns:
            Dict with detected face coordinates or error.
        """
        try:
            import cv2
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, self.cascade_path))
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            face_list = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]
            logger.info("OpenCV detected %d faces in %s.", len(face_list), image_path)
            return {"status": "success", "faces": face_list, "count": len(face_list)}
        except ImportError:
            logger.error("cv2 (OpenCV) library not installed.")
            return {"status": "error", "message": "cv2 library not installed."}
        except Exception as e:
            logger.error("OpenCV detect_faces_haar error: %s", e)
            return {"status": "error", "message": str(e)}
