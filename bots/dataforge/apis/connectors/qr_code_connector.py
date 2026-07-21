"""QR code generation connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class QRCodeConnector:
    """QRCodeConnector for DataForge AI."""

    BASE_URL = "https://api.qrserver.com/v1"

    def __init__(self):
        """Initialize connector (no API key required)."""
        logger.info("QRCodeConnector initialized.")

    def generate_qr(self, data: str, size: int = 200) -> dict:
        """Generate a QR code URL.

        Args:
            data: Data to encode in the QR code.
            size: Image size in pixels (default 200).

        Returns:
            Dict with QR code URL.
        """
        import urllib.parse
        encoded_data = urllib.parse.quote(data)
        url = f"{self.BASE_URL}/create-qr-code/?size={size}x{size}&data={encoded_data}"
        logger.info("QR code URL generated for data: %s", data[:30])
        return {"status": "success", "url": url, "size": size}

    def read_qr(self, image_url: str) -> dict:
        """Read/decode a QR code from an image URL.

        Args:
            image_url: URL of the QR code image.

        Returns:
            API response dict with decoded data or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/read-qr-code/", params={"fileurl": image_url}, timeout=30)
            response.raise_for_status()
            logger.info("QR code read from URL.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("QR Code read_qr error: %s", e)
            return {"status": "error", "message": str(e)}
