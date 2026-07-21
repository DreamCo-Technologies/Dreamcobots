"""Mailchimp email marketing connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class MailchimpConnector:
    """MailchimpConnector for DataForge AI."""

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.api_key = os.environ.get("MAILCHIMP_API_KEY", "")
        server_prefix = os.environ.get("MAILCHIMP_SERVER_PREFIX", "us1")
        self.base_url = f"https://{server_prefix}.api.mailchimp.com/3.0"
        if not self.api_key:
            logger.warning("MAILCHIMP_API_KEY not set.")

    def get_lists(self) -> dict:
        """Get all Mailchimp lists/audiences.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.base_url}/lists", auth=("anystring", self.api_key), timeout=30)
            response.raise_for_status()
            logger.info("Mailchimp lists fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Mailchimp get_lists error: %s", e)
            return {"status": "error", "message": str(e)}

    def add_member(self, list_id: str, email: str, status: str = "subscribed") -> dict:
        """Add a member to a Mailchimp list.

        Args:
            list_id: The Mailchimp list identifier.
            email: Member email address.
            status: Subscription status (default 'subscribed').

        Returns:
            API response dict or error dict.
        """
        import requests
        payload = {"email_address": email, "status": status}
        try:
            response = requests.post(f"{self.base_url}/lists/{list_id}/members",
                json=payload, auth=("anystring", self.api_key), timeout=30)
            response.raise_for_status()
            logger.info("Mailchimp member added to list %s.", list_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Mailchimp add_member error: %s", e)
            return {"status": "error", "message": str(e)}
