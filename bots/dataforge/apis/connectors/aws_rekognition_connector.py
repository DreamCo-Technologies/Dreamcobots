"""AWS Rekognition vision connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class AWSRekognitionConnector:
    """AWSRekognitionConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector, reading AWS credentials from environment."""
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        self.region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        if not self.access_key or not self.secret_key:
            logger.warning("AWS credentials not set.")

    def detect_faces(self, image_bytes: bytes) -> dict:
        """Detect faces in image bytes using AWS Rekognition.

        Args:
            image_bytes: Raw image bytes to analyze.

        Returns:
            Dict with face detection results or error.
        """
        try:
            import boto3
            client = boto3.client("rekognition", region_name=self.region,
                                  aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
            response = client.detect_faces(Image={"Bytes": image_bytes}, Attributes=["ALL"])
            logger.info("AWS Rekognition face detection completed.")
            return {"status": "success", "data": response}
        except Exception as e:
            logger.error("AWS Rekognition detect_faces error: %s", e)
            return {"status": "error", "message": str(e)}

    def detect_labels(self, image_bytes: bytes) -> dict:
        """Detect labels in image bytes using AWS Rekognition.

        Args:
            image_bytes: Raw image bytes to analyze.

        Returns:
            Dict with label detection results or error.
        """
        try:
            import boto3
            client = boto3.client("rekognition", region_name=self.region,
                                  aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
            response = client.detect_labels(Image={"Bytes": image_bytes}, MaxLabels=10)
            logger.info("AWS Rekognition label detection completed.")
            return {"status": "success", "data": response}
        except Exception as e:
            logger.error("AWS Rekognition detect_labels error: %s", e)
            return {"status": "error", "message": str(e)}
