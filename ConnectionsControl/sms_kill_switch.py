"""
SMS Kill Switch for DreamCobots — mock Twilio-like implementation.

Enables SMS-triggered emergency stop and alert notifications.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class SMSMessage:
    message_id: str
    from_number: str
    to_number: str
    body: str
    direction: str   # "outbound" | "inbound"
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SMSKillSwitch:
    """SMS-based kill switch and alert system (mock — no network calls)."""

    KILL_COMMANDS = {"STOP", "KILL", "HALT", "EMERGENCY"}
    RESTORE_COMMANDS = {"START", "RESTORE", "RESUME"}

    def __init__(self) -> None:
        self._account_sid: Optional[str] = None
        self._auth_token: Optional[str] = None
        self._from_number: Optional[str] = None
        self._to_numbers: List[str] = []
        self._message_log: List[SMSMessage] = []
        self._kill_active: bool = False

    def configure(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        to_numbers: List[str],
    ) -> None:
        """Configure SMS gateway credentials and recipient numbers."""
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self._to_numbers = list(to_numbers)

    def send_alert(self, message: str) -> List[SMSMessage]:
        """Send an SMS alert to all configured recipient numbers."""
        sent = []
        for to in self._to_numbers:
            msg = SMSMessage(
                message_id=str(uuid.uuid4()),
                from_number=self._from_number or "unknown",
                to_number=to,
                body=message,
                direction="outbound",
            )
            self._message_log.append(msg)
            sent.append(msg)
        return sent

    def trigger_kill_switch(self) -> dict:
        """Send SMS notifications and activate the kill switch."""
        self._kill_active = True
        sent = self.send_alert("🚨 DREAMCOBOTS KILL SWITCH ACTIVATED. All bots halted.")
        return {
            "kill_switch_active": True,
            "notifications_sent": len(sent),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def handle_incoming_sms(self, from_number: str, body: str) -> dict:
        """Parse an incoming SMS and execute the corresponding command."""
        msg = SMSMessage(
            message_id=str(uuid.uuid4()),
            from_number=from_number,
            to_number=self._from_number or "system",
            body=body,
            direction="inbound",
        )
        self._message_log.append(msg)
        command = body.strip().upper()
        if command in self.KILL_COMMANDS:
            self._kill_active = True
            return {"action": "kill_switch_activated", "command": command}
        if command in self.RESTORE_COMMANDS:
            self._kill_active = False
            return {"action": "kill_switch_deactivated", "command": command}
        return {"action": "unknown_command", "command": command}

    @property
    def is_configured(self) -> bool:
        """Return True if the SMS gateway is fully configured."""
        return bool(self._account_sid and self._from_number and self._to_numbers)

    def get_message_log(self) -> List[SMSMessage]:
        """Return all logged SMS messages."""
        return list(self._message_log)

    def get_status(self) -> dict:
        """Return current configuration and kill switch status."""
        return {
            "is_configured": self.is_configured,
            "kill_active": self._kill_active,
            "recipient_count": len(self._to_numbers),
            "messages_sent": sum(1 for m in self._message_log if m.direction == "outbound"),
        }
