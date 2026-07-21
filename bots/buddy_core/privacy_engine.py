"""
Privacy Engine for the Buddy Core System.

Provides permission management, activity logging, an encrypted data vault
(simulated AES-256 via base64 + XOR), and safety guardrails for sensitive
actions.

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.
actions — all in-memory with no external dependencies.
"""

from __future__ import annotations

import base64
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DataVaultError(Exception):
    """Raised on vault access errors."""


class PrivacyEngineError(Exception):
    """Raised on general privacy engine errors."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PermissionLevel(Enum):
    READ_ONLY = "read_only"
    RESTRICTED = "restricted"
    FULL_AUTONOMY = "full_autonomy"


class ActionCategory(Enum):
    DATA_ACCESS = "data_access"
    FINANCIAL = "financial"
    COMMUNICATION = "communication"
    BOT_CREATION = "bot_creation"
    SYSTEM = "system"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ActivityLog:
    log_id: str
    user_id: str
    action: str
    category: ActionCategory
    timestamp: datetime
    status: str
    details: dict = field(default_factory=dict)


@dataclass
class UserPermission:
    user_id: str
    level: PermissionLevel
    allowed_categories: list
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Permission mapping: which categories are allowed per level
# ---------------------------------------------------------------------------

_LEVEL_CATEGORIES: dict[PermissionLevel, list[ActionCategory]] = {
    PermissionLevel.READ_ONLY: [ActionCategory.DATA_ACCESS],
    PermissionLevel.RESTRICTED: [
        ActionCategory.DATA_ACCESS,
        ActionCategory.COMMUNICATION,
        ActionCategory.BOT_CREATION,
    ],
    PermissionLevel.FULL_AUTONOMY: list(ActionCategory),
}


# ---------------------------------------------------------------------------
# Permission Manager
# ---------------------------------------------------------------------------

class PermissionManager:
    def __init__(self) -> None:
        self._permissions: dict[str, UserPermission] = {}

    def set_permission(
        self,
        user_id: str,
        level: PermissionLevel,
        categories: Optional[list] = None,
    ) -> UserPermission:
        allowed = categories if categories is not None else _LEVEL_CATEGORIES[level]
        now = datetime.utcnow()
        perm = UserPermission(
            user_id=user_id,
            level=level,
            allowed_categories=list(allowed),
            created_at=now,
            updated_at=now,
        )
        self._permissions[user_id] = perm
        return perm

    def get_permission(self, user_id: str) -> Optional[UserPermission]:
        return self._permissions.get(user_id)

    def can_perform(self, user_id: str, category: ActionCategory) -> bool:
        perm = self._permissions.get(user_id)
        if perm is None:
            return False
        return category in perm.allowed_categories

    def require_permission(self, user_id: str, category: ActionCategory) -> None:
        if not self.can_perform(user_id, category):
            raise PrivacyEngineError(
                f"User '{user_id}' does not have permission for {category.value}."
            )


# ---------------------------------------------------------------------------
# Activity Logger
# ---------------------------------------------------------------------------

class ActivityLogger:
    def __init__(self) -> None:
        self._logs: list[ActivityLog] = []

    def log(
        self,
        user_id: str,
        action: str,
        category: ActionCategory,
        status: str = "success",
        details: Optional[dict] = None,
    ) -> ActivityLog:
        entry = ActivityLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            category=category,
            timestamp=datetime.utcnow(),
            status=status,
            details=details or {},
        )
        self._logs.append(entry)
        return entry

    def get_logs(
        self, user_id: Optional[str] = None, limit: int = 100
    ) -> list[ActivityLog]:
        logs = self._logs if user_id is None else [l for l in self._logs if l.user_id == user_id]
        return logs[-limit:]

    def get_stats(self) -> dict:
        return {
            "total_logs": len(self._logs),
            "unique_users": len({l.user_id for l in self._logs}),
            "categories": {cat.value: sum(1 for l in self._logs if l.category == cat) for cat in ActionCategory},
        }


# ---------------------------------------------------------------------------
# Data Vault  (simulated AES-256 via base64 + XOR)
# ---------------------------------------------------------------------------

_VAULT_SECRET = b"DreamcobotsBuddyCoreVaultKey2024"  # 32 bytes → AES-256 sim


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))


class DataVault:
    """Stores and retrieves encrypted key-value pairs."""

    def __init__(self) -> None:
        # token → (user_id, encrypted_bytes)
        self._vault: dict[str, tuple[str, bytes]] = {}

    def store(self, key: str, value: str, user_id: str) -> str:
        """Encrypt *value* and return an opaque token."""
        raw = f"{key}:{value}".encode("utf-8")
        encrypted = _xor_bytes(raw, _VAULT_SECRET)
        token = base64.urlsafe_b64encode(encrypted).decode("ascii")
        self._vault[token] = (user_id, encrypted)
        return token

    def retrieve(self, token: str, user_id: str) -> str:
        """Decrypt and return the original value for *key*."""
        if token not in self._vault:
            raise DataVaultError("Token not found in vault.")
        owner, encrypted = self._vault[token]
        if owner != user_id:
            raise DataVaultError("Access denied: token belongs to a different user.")
        raw = _xor_bytes(encrypted, _VAULT_SECRET).decode("utf-8")
        # raw is "key:value"; return the value part
        _, _, value = raw.partition(":")
        return value

    def delete(self, token: str, user_id: str) -> bool:
        if token not in self._vault:
            return False
        owner, _ = self._vault[token]
        if owner != user_id:
            raise DataVaultError("Access denied.")
        del self._vault[token]
        return True


# ---------------------------------------------------------------------------
# Safety Guardrail
# ---------------------------------------------------------------------------

_HIGH_RISK_CATEGORIES = {ActionCategory.FINANCIAL, ActionCategory.SYSTEM}


class SafetyGuardrail:
    """Checks whether an action is safe and manages confirmation workflow."""

    def __init__(self) -> None:
        self._pending: dict[str, dict] = {}

    def check_action(
        self, action: str, category: ActionCategory, user_id: str
    ) -> dict:
        requires_confirmation = category in _HIGH_RISK_CATEGORIES
        action_id = str(uuid.uuid4())
        result: dict = {
            "action_id": action_id,
            "approved": not requires_confirmation,
            "requires_confirmation": requires_confirmation,
            "reason": (
                f"Action '{action}' in category '{category.value}' requires "
                "explicit confirmation."
            )
            if requires_confirmation
            else "Action approved.",
        }
        if requires_confirmation:
            self._pending[action_id] = {
                "action_id": action_id,
                "action": action,
                "category": category.value,
                "user_id": user_id,
                "status": "pending",
            }
        return result

    def confirm_action(self, action_id: str) -> bool:
        if action_id not in self._pending:
            return False
        self._pending[action_id]["status"] = "confirmed"
        return True

    def cancel_action(self, action_id: str) -> bool:
        if action_id not in self._pending:
            return False
        self._pending[action_id]["status"] = "cancelled"
        return True

    def get_pending_actions(self) -> list[dict]:
        return [a for a in self._pending.values() if a["status"] == "pending"]


# ---------------------------------------------------------------------------
# PrivacyEngine (facade)
# ---------------------------------------------------------------------------

class PrivacyEngine:
    """Composes all privacy sub-systems."""

    def __init__(self) -> None:
        self.permissions = PermissionManager()
        self.logger = ActivityLogger()
        self.vault = DataVault()
        self.guardrail = SafetyGuardrail()
