"""
DreamCo SMS Sender — Twilio Integration

Sends SMS messages to leads and sellers.  When the ``TWILIO_SID`` and
``TWILIO_AUTH`` environment variables are absent the client operates in
mock mode so unit tests never make real HTTP calls.

Usage
-----
    sender = SMSSender()
    result = sender.send_sms("+15551234567", "Cash offer available!")
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class SMSRecord:
    to: str
    message: str
    from_number: str
    status: str  # "sent" | "mock" | "failed"
    sid: Optional[str] = None
    sent_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "to": self.to,
            "message": self.message,
            "from_number": self.from_number,
            "status": self.status,
            "sid": self.sid,
            "sent_at": self.sent_at,
        }


# ---------------------------------------------------------------------------
# SMSSender
# ---------------------------------------------------------------------------


class SMSSender:
    """
    Sends SMS messages via Twilio (or mock mode for testing).

    Parameters
    ----------
    account_sid  : Twilio Account SID (default: env TWILIO_SID).
    auth_token   : Twilio Auth Token  (default: env TWILIO_AUTH).
    from_number  : Sending phone number (default: env TWILIO_FROM or placeholder).
    mock         : Force mock mode regardless of credentials.
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        mock: bool = False,
    ) -> None:
        self.account_sid = account_sid or os.environ.get("TWILIO_SID", "")
        self.auth_token = auth_token or os.environ.get("TWILIO_AUTH", "")
        self.from_number = (
            from_number
            or os.environ.get("TWILIO_FROM", "+10000000000")
        )
        self._mock = mock or not (self.account_sid and self.auth_token)
        self._sent: List[SMSRecord] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_mock(self) -> bool:
        return self._mock

    def send_sms(self, to: str, message: str) -> SMSRecord:
        """
        Send an SMS to *to* with *message*.

        In mock mode the message is logged locally instead of being
        transmitted via the Twilio API.
        """
        if self._mock:
            record = SMSRecord(
                to=to,
                message=message,
                from_number=self.from_number,
                status="mock",
                sid=f"MOCK_{len(self._sent) + 1:04d}",
            )
        else:
            record = self._send_via_twilio(to, message)

        self._sent.append(record)
        return record

    def send_bulk(self, recipients: List[str], message: str) -> List[SMSRecord]:
        """Send the same message to multiple recipients."""
        return [self.send_sms(to, message) for to in recipients]

    def get_sent_log(self) -> List[dict]:
        """Return a list of all sent (or mocked) SMS records."""
        return [r.to_dict() for r in self._sent]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _send_via_twilio(self, to: str, message: str) -> SMSRecord:
        """Transmit via the Twilio REST API."""
        try:
            from twilio.rest import Client  # type: ignore[import]

            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(
                body=message,
                from_=self.from_number,
                to=to,
            )
            return SMSRecord(
                to=to,
                message=message,
                from_number=self.from_number,
                status="sent",
                sid=msg.sid,
            )
        except Exception as exc:
            return SMSRecord(
                to=to,
                message=message,
                from_number=self.from_number,
                status="failed",
                sid=f"ERROR: {exc}",
            )
