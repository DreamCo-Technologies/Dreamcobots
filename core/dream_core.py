"""DreamCore: shared utility for outreach email generation."""
import logging
from typing import Dict, Optional


class DreamCore:
    """Generates personalised outreach emails for leads and clients."""

    DEFAULT_SIGNATURE = "The DreamCo Team"

    def __init__(self, signature: str = DEFAULT_SIGNATURE):
        self.signature = signature
        self.logger = logging.getLogger(__name__)

    def generate_email(
        self,
        recipient_name: str,
        subject: str,
        body: str,
        sender: Optional[str] = None,
    ) -> Dict[str, str]:
        """Compose an outreach email dict ready for delivery."""
        email = {
            "to": recipient_name,
            "subject": subject,
            "body": f"Hi {recipient_name},\n\n{body}\n\nBest regards,\n{self.signature}",
            "from": sender or "noreply@dreamco.io",
        }
        self.logger.info("Email generated for recipient: %s | subject: %s", recipient_name, subject)
        return email

    def generate_lead_outreach(self, lead: Dict) -> Dict[str, str]:
        """Generate a standard outreach email for a scraped lead."""
        name = lead.get("name", "there")
        subject = "Exciting Opportunity from DreamCo"
        body = (
            "We came across your profile and believe we have an exciting opportunity "
            "that aligns with your goals. We would love to connect and explore how we "
            "can add value to your business."
        )
        return self.generate_email(name, subject, body)
