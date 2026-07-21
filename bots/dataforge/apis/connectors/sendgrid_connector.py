"""SendGrid email API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class SendGridConnector:
    """SendGridConnector for DataForge AI."""

    BASE_URL = "https://api.sendgrid.com/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("SENDGRID_API_KEY", "")
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not set.")

    def send_email(self, to_email: str, subject: str, html_content: str, from_email: str = "noreply@dataforge.ai") -> dict:
        """Send an email using SendGrid.

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            html_content: HTML body content.
            from_email: Sender email (default noreply@dataforge.ai).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_content}],
        }
        try:
            response = requests.post(f"{self.BASE_URL}/mail/send", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("SendGrid email sent to %s.", to_email)
            return {"status": "success", "status_code": response.status_code}
        except requests.RequestException as e:
            logger.error("SendGrid send_email error: %s", e)
            return {"status": "error", "message": str(e)}
