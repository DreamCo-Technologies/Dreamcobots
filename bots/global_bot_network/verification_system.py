"""
Verification System — DreamCo Global Bot Communication Network.

Manages trust levels for all bots on the network.

Verification levels
-------------------
  NONE     — Bot has been registered but not yet verified.
  BASIC    — Email or account confirmation received.
  VERIFIED — Owner has confirmed the bot (signed in, approved).
  TRUSTED  — Network-level trust; requires strong confirmation
             (wallet address or extended activity history).

Each level unlocks additional capabilities on the network
(e.g. higher rate limits, marketplace access, admin actions).
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VerificationLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    VERIFIED = "verified"
    TRUSTED = "trusted"


class VerificationMethod(Enum):
    EMAIL = "email"
    WALLET = "wallet"
    PHONE = "phone"
    OWNER_CONFIRM = "owner_confirm"
    ADMIN_GRANT = "admin_grant"


# Minimum method required for each level
_LEVEL_REQUIREMENTS: dict[VerificationLevel, list[VerificationMethod]] = {
    VerificationLevel.NONE: [],
    VerificationLevel.BASIC: [VerificationMethod.EMAIL],
    VerificationLevel.VERIFIED: [VerificationMethod.OWNER_CONFIRM],
    VerificationLevel.TRUSTED: [VerificationMethod.WALLET, VerificationMethod.ADMIN_GRANT],
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class VerificationError(Exception):
    """Base exception for the Verification System."""


class InsufficientVerificationMethod(VerificationError):
    """Raised when the provided method is not sufficient for the requested level."""


class BotNotRegistered(VerificationError):
    """Raised when operating on a bot that has not been registered."""


# ---------------------------------------------------------------------------
# Verification record
# ---------------------------------------------------------------------------

@dataclass
class VerificationRecord:
    """
    Tracks the verification state of a single bot.

    Attributes
    ----------
    bot_id : str
        Unique bot identifier.
    owner_id : str
        Owner's user identifier.
    level : VerificationLevel
        Current verification level.
    methods_completed : list[VerificationMethod]
        Confirmation methods that have been successfully executed.
    notes : str
        Optional notes from the verifier.
    created_at : str
        ISO-8601 UTC creation timestamp.
    updated_at : str
        ISO-8601 UTC last-update timestamp.
    """

    bot_id: str
    owner_id: str
    level: VerificationLevel = VerificationLevel.NONE
    methods_completed: list = field(default_factory=list)
    notes: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_method(self, method: VerificationMethod) -> None:
        if method not in self.methods_completed:
            self.methods_completed.append(method)
        self._touch()

    def has_method(self, method: VerificationMethod) -> bool:
        return method in self.methods_completed

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "owner_id": self.owner_id,
            "level": self.level.value,
            "methods_completed": [m.value for m in self.methods_completed],
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Verification System
# ---------------------------------------------------------------------------

class VerificationSystem:
    """
    Manages trust levels for all bots in the DreamCo network.

    Usage::

        vs = VerificationSystem()
        vs.register_bot("bot_001", owner_id="user_123")
        vs.verify(
            "bot_001",
            method=VerificationMethod.EMAIL,
            target_level=VerificationLevel.BASIC,
        )
    """

    def __init__(self) -> None:
        self._records: dict[str, VerificationRecord] = {}

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(
        self,
        bot_id: str,
        owner_id: str,
        notes: str = "",
    ) -> VerificationRecord:
        """
        Register a bot in the verification system at level NONE.

        Returns the newly created (or existing) VerificationRecord.
        """
        if bot_id in self._records:
            return self._records[bot_id]
        record = VerificationRecord(bot_id=bot_id, owner_id=owner_id, notes=notes)
        self._records[bot_id] = record
        return record

    def unregister_bot(self, bot_id: str) -> None:
        """Remove a bot's verification record."""
        self._records.pop(bot_id, None)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(
        self,
        bot_id: str,
        method: VerificationMethod,
        target_level: VerificationLevel,
        admin: bool = False,
    ) -> VerificationRecord:
        """
        Advance a bot's verification level.

        Parameters
        ----------
        bot_id : str
            The bot to verify.
        method : VerificationMethod
            The confirmation method being applied.
        target_level : VerificationLevel
            The desired level to reach.
        admin : bool
            When *True*, bypasses method requirements (admin grant).

        Raises
        ------
        BotNotRegistered
            If *bot_id* has not been registered.
        InsufficientVerificationMethod
            If *method* alone is not sufficient for *target_level* and
            not all required methods have been completed.
        """
        record = self._get(bot_id)
        record.add_method(method)

        if not admin:
            required = _LEVEL_REQUIREMENTS.get(target_level, [])
            missing = [m for m in required if not record.has_method(m)]
            if missing:
                raise InsufficientVerificationMethod(
                    f"Bot '{bot_id}' is missing verification methods for "
                    f"level '{target_level.value}': "
                    f"{[m.value for m in missing]}"
                )

        # Only advance; never lower an existing level
        if _level_order(target_level) > _level_order(record.level):
            record.level = target_level
            record._touch()

        return record

    def revoke(self, bot_id: str, reason: str = "") -> VerificationRecord:
        """Revoke a bot's verification (reset to NONE)."""
        record = self._get(bot_id)
        record.level = VerificationLevel.NONE
        record.methods_completed.clear()
        record.notes = reason
        record._touch()
        return record

    def admin_grant(
        self, bot_id: str, level: VerificationLevel, notes: str = ""
    ) -> VerificationRecord:
        """Admin-level grant of any verification level, bypassing requirements."""
        record = self._get(bot_id)
        record.level = level
        if notes:
            record.notes = notes
        record.add_method(VerificationMethod.ADMIN_GRANT)
        return record

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_record(self, bot_id: str) -> Optional[VerificationRecord]:
        """Return the VerificationRecord for *bot_id*, or *None*."""
        return self._records.get(bot_id)

    def get_level(self, bot_id: str) -> VerificationLevel:
        """Return current verification level; NONE if not registered."""
        record = self._records.get(bot_id)
        return record.level if record else VerificationLevel.NONE

    def is_at_least(self, bot_id: str, level: VerificationLevel) -> bool:
        """Return *True* if *bot_id*'s level ≥ *level*."""
        return _level_order(self.get_level(bot_id)) >= _level_order(level)

    def list_bots(self, level: Optional[VerificationLevel] = None) -> list[dict]:
        """Return all records, optionally filtered by level."""
        records = self._records.values()
        if level is not None:
            records = [r for r in records if r.level == level]
        return [r.to_dict() for r in records]

    def get_stats(self) -> dict:
        """Return verification statistics."""
        counts: dict[str, int] = {v.value: 0 for v in VerificationLevel}
        for r in self._records.values():
            counts[r.level.value] += 1
        return {
            "total_bots": len(self._records),
            "by_level": counts,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, bot_id: str) -> VerificationRecord:
        if bot_id not in self._records:
            raise BotNotRegistered(
                f"Bot '{bot_id}' is not registered in the verification system."
            )
        return self._records[bot_id]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LEVEL_ORDER = {
    VerificationLevel.NONE: 0,
    VerificationLevel.BASIC: 1,
    VerificationLevel.VERIFIED: 2,
    VerificationLevel.TRUSTED: 3,
}


def _level_order(level: VerificationLevel) -> int:
    return _LEVEL_ORDER.get(level, 0)
