"""IP-API geolocation connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class IPAPIConnector:
    """IPAPIConnector for DataForge AI."""

    BASE_URL = "http://ip-api.com"

    def __init__(self):
        """Initialize connector (no API key required for basic use)."""
        logger.info("IPAPIConnector initialized.")

    def get_ip_info(self, ip_address: str = "") -> dict:
        """Get geolocation info for an IP address.

        Args:
            ip_address: IP address to lookup (empty string for current IP).

        Returns:
            API response dict or error dict.
        """
        import requests
        target = ip_address if ip_address else ""
        try:
            response = requests.get(f"{self.BASE_URL}/json/{target}", timeout=30)
            response.raise_for_status()
            logger.info("IP-API info fetched for: %s", ip_address or "self")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("IP-API get_ip_info error: %s", e)
            return {"status": "error", "message": str(e)}

    def batch_lookup(self, ip_list: list) -> dict:
        """Batch lookup multiple IP addresses.

        Args:
            ip_list: List of IP address strings.

        Returns:
            API response dict with list of results or error dict.
        """
        import requests
        try:
            response = requests.post(f"{self.BASE_URL}/batch", json=ip_list, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("IP-API batch_lookup error: %s", e)
            return {"status": "error", "message": str(e)}
