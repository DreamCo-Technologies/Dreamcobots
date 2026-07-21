"""
Universal Bot Protocol (UBP) — DreamCo Global Bot Communication Network.

Defines the standard message structure and validation rules for all bot
communication inside the DreamCo network and with external systems.

Message structure:
    {
        "id":          "<uuid>",
        "from":        "<sender_bot_id>",
        "to":          "<receiver_bot_id | broadcast>",
        "type":        "message | request | response | ping | error | task",
        "message":     "<text payload>",
        "data":        {...},           # optional structured data
        "permissions": ["read", "execute", "respond"],
        "timestamp":   "<ISO-8601 UTC>",
        "metadata":    {...}            # optional extra info
    }
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MessageType(Enum):
    MESSAGE = "message"
    REQUEST = "request"
    RESPONSE = "response"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    TASK = "task"
    STATUS = "status"
    BROADCAST = "broadcast"


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    RESPOND = "respond"
    ADMIN = "admin"


BROADCAST_TARGET = "broadcast"

# Default permissions for unverified bots
DEFAULT_PERMISSIONS: list[str] = [Permission.READ.value, Permission.RESPOND.value]

# All valid message types and permissions as strings
VALID_MESSAGE_TYPES = {m.value for m in MessageType}
VALID_PERMISSIONS = {p.value for p in Permission}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class UBPError(Exception):
    """Base exception for Universal Bot Protocol errors."""


class UBPValidationError(UBPError):
    """Raised when a UBP message fails validation."""


class UBPPermissionError(UBPError):
    """Raised when a bot lacks the required permission for an action."""


# ---------------------------------------------------------------------------
# UBP Message dataclass
# ---------------------------------------------------------------------------

@dataclass
class UBPMessage:
    """
    A single message conforming to the Universal Bot Protocol.

    Attributes
    ----------
    from_bot : str
        Identifier of the sending bot.
    to_bot : str
        Identifier of the receiving bot, or ``"broadcast"`` for all.
    type : MessageType
        Semantic category of the message.
    message : str
        Human-readable text payload.
    permissions : list[str]
        Actions the receiver is authorised to perform upon receiving this.
    id : str
        Auto-generated UUID for deduplication / tracing.
    data : dict
        Optional structured payload (command args, results, etc.).
    timestamp : str
        ISO-8601 UTC creation time.
    metadata : dict
        Arbitrary key/value pairs for routing, tracing, versioning, etc.
    """

    from_bot: str
    to_bot: str
    type: MessageType
    message: str
    permissions: list = field(default_factory=lambda: list(DEFAULT_PERMISSIONS))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise to a plain dict (JSON-safe)."""
        return {
            "id": self.id,
            "from": self.from_bot,
            "to": self.to_bot,
            "type": self.type.value,
            "message": self.message,
            "permissions": list(self.permissions),
            "data": dict(self.data),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "UBPMessage":
        """Deserialise from a plain dict, raising UBPValidationError on bad input."""
        _validate_raw(payload)
        raw_type = payload["type"]
        try:
            msg_type = MessageType(raw_type)
        except ValueError as exc:
            raise UBPValidationError(
                f"Unknown message type '{raw_type}'. "
                f"Valid types: {sorted(VALID_MESSAGE_TYPES)}"
            ) from exc

        return cls(
            from_bot=payload["from"],
            to_bot=payload["to"],
            type=msg_type,
            message=payload.get("message", ""),
            permissions=list(payload.get("permissions", DEFAULT_PERMISSIONS)),
            id=payload.get("id", str(uuid.uuid4())),
            data=dict(payload.get("data", {})),
            timestamp=payload.get(
                "timestamp", datetime.now(timezone.utc).isoformat()
            ),
            metadata=dict(payload.get("metadata", {})),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_broadcast(self) -> bool:
        return self.to_bot == BROADCAST_TARGET

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __repr__(self) -> str:
        return (
            f"UBPMessage(id={self.id!r}, from={self.from_bot!r}, "
            f"to={self.to_bot!r}, type={self.type.value!r})"
        )


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_raw(payload: Any) -> None:
    """Validate a raw dict, raising UBPValidationError on any issue."""
    if not isinstance(payload, dict):
        raise UBPValidationError("UBP payload must be a dict.")

    required = ("from", "to", "type")
    missing = [k for k in required if k not in payload]
    if missing:
        raise UBPValidationError(
            f"UBP message missing required fields: {missing}"
        )

    for key in ("from", "to", "type"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise UBPValidationError(
                f"Field '{key}' must be a non-empty string."
            )

    perms = payload.get("permissions", [])
    if not isinstance(perms, list):
        raise UBPValidationError("'permissions' must be a list.")
    unknown = [p for p in perms if p not in VALID_PERMISSIONS]
    if unknown:
        raise UBPValidationError(
            f"Unknown permissions: {unknown}. "
            f"Valid: {sorted(VALID_PERMISSIONS)}"
        )


def validate_message(payload: dict) -> None:
    """
    Validate a raw UBP message dict.

    Raises
    ------
    UBPValidationError
        If the payload does not conform to the UBP spec.
    """
    _validate_raw(payload)
    raw_type = payload["type"]
    if raw_type not in VALID_MESSAGE_TYPES:
        raise UBPValidationError(
            f"Unknown message type '{raw_type}'. "
            f"Valid types: {sorted(VALID_MESSAGE_TYPES)}"
        )


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def create_message(
    from_bot: str,
    to_bot: str,
    message: str,
    *,
    msg_type: MessageType = MessageType.MESSAGE,
    permissions: Optional[list] = None,
    data: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> UBPMessage:
    """Convenience factory for creating UBPMessage instances."""
    return UBPMessage(
        from_bot=from_bot,
        to_bot=to_bot,
        type=msg_type,
        message=message,
        permissions=permissions if permissions is not None else list(DEFAULT_PERMISSIONS),
        data=data or {},
        metadata=metadata or {},
    )


def create_ping(from_bot: str, to_bot: str) -> UBPMessage:
    """Create a PING message."""
    return create_message(
        from_bot, to_bot, "ping",
        msg_type=MessageType.PING,
        permissions=[Permission.RESPOND.value],
    )


def create_pong(from_bot: str, to_bot: str, ping_id: str) -> UBPMessage:
    """Create a PONG reply to a PING."""
    return create_message(
        from_bot, to_bot, "pong",
        msg_type=MessageType.PONG,
        permissions=[Permission.READ.value],
        metadata={"reply_to": ping_id},
    )


def create_error(from_bot: str, to_bot: str, error_msg: str) -> UBPMessage:
    """Create an ERROR message."""
    return create_message(
        from_bot, to_bot, error_msg,
        msg_type=MessageType.ERROR,
        permissions=[Permission.READ.value],
    )


def create_broadcast(from_bot: str, message: str, *, data: Optional[dict] = None) -> UBPMessage:
    """Create a BROADCAST message to all bots."""
    return create_message(
        from_bot, BROADCAST_TARGET, message,
        msg_type=MessageType.BROADCAST,
        data=data or {},
    )
