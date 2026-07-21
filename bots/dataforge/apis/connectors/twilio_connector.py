"""Twilio SMS and voice connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class TwilioConnector:
    """TwilioConnector for DataForge AI."""

    BASE_URL = "https://api.twilio.com/2010-04-01"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.environ.get("TWILIO_FROM_NUMBER", "")
        if not self.account_sid or not self.auth_token:
            logger.warning("TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not set.")

    def send_sms(self, to: str, body: str) -> dict:
        """Send an SMS message using Twilio.

        Args:
            to: Recipient phone number.
            body: SMS message body.

        Returns:
            API response dict or error dict.
        """
        import requests
        url = f"{self.BASE_URL}/Accounts/{self.account_sid}/Messages.json"
        payload = {"To": to, "From": self.from_number, "Body": body}
        try:
            response = requests.post(url, data=payload, auth=(self.account_sid, self.auth_token), timeout=30)
            response.raise_for_status()
            logger.info("Twilio SMS sent to %s.", to)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Twilio send_sms error: %s", e)
            return {"status": "error", "message": str(e)}

    def make_call(self, to: str, twiml_url: str) -> dict:
        """Make a voice call using Twilio.

        Args:
            to: Recipient phone number.
            twiml_url: URL returning TwiML instructions.

        Returns:
            API response dict or error dict.
        """
        import requests
        url = f"{self.BASE_URL}/Accounts/{self.account_sid}/Calls.json"
        payload = {"To": to, "From": self.from_number, "Url": twiml_url}
        try:
            response = requests.post(url, data=payload, auth=(self.account_sid, self.auth_token), timeout=30)
            response.raise_for_status()
            logger.info("Twilio call initiated to %s.", to)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Twilio make_call error: %s", e)
            return {"status": "error", "message": str(e)}
