"""
DreamCo Platform — Auth Workspace
=====================================

``AuthWorkspace`` is the auth-layer workspace object.  It tracks:
* Member identities and their permission sets
* API key associations
* OAuth token bindings

This is separate from ``registry/workspace_registry.py`` (metadata/quotas)
and from ``governance/rbac.py`` (role inheritance graph).

The three objects compose together in production; here we keep auth concerns
cleanly separated so each layer is independently testable.

Usage::

    ws = AuthWorkspace("ws_acme", owner_user_id="user:alice")
    ws.add_member("user:bob", permissions=PermissionSet({"read:bots", "run:workflow"}))
    ws.can("user:bob", "run:workflow")   # True
    ws.can("user:bob", "admin:users")    # False
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dreamco_platform.auth.permissions import PermissionSet


# ---------------------------------------------------------------------------
# Member record
# ---------------------------------------------------------------------------

@dataclass
class WorkspaceMember:
    user_id: str
    permissions: PermissionSet = field(default_factory=PermissionSet)
    api_key_ids: list[str] = field(default_factory=list)
    oauth_providers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "permissions": self.permissions.to_list(),
            "api_key_ids": self.api_key_ids,
            "oauth_providers": self.oauth_providers,
        }


# ---------------------------------------------------------------------------
# AuthWorkspace
# ---------------------------------------------------------------------------

class AuthWorkspace:
    """Auth-layer workspace: members, permissions, and key bindings."""

    def __init__(self, workspace_id: str, owner_user_id: str) -> None:
        self.workspace_id = workspace_id
        self.owner_user_id = owner_user_id
        self._members: dict[str, WorkspaceMember] = {}
        # Add owner as superadmin
        self.add_member(owner_user_id, permissions=PermissionSet({"*"}))

    # ------------------------------------------------------------------
    # Membership
    # ------------------------------------------------------------------

    def add_member(
        self,
        user_id: str,
        permissions: PermissionSet | None = None,
    ) -> WorkspaceMember:
        member = WorkspaceMember(
            user_id=user_id,
            permissions=permissions or PermissionSet(),
        )
        self._members[user_id] = member
        return member

    def remove_member(self, user_id: str) -> bool:
        if user_id not in self._members or user_id == self.owner_user_id:
            return False
        del self._members[user_id]
        return True

    def get_member(self, user_id: str) -> WorkspaceMember | None:
        return self._members.get(user_id)

    def is_member(self, user_id: str) -> bool:
        return user_id in self._members

    # ------------------------------------------------------------------
    # Permission checks
    # ------------------------------------------------------------------

    def can(self, user_id: str, permission: str) -> bool:
        """Return True if *user_id* holds *permission* in this workspace."""
        member = self._members.get(user_id)
        if member is None:
            return False
        return member.permissions.has(permission)

    def grant(self, user_id: str, *permissions: str) -> bool:
        """Grant additional *permissions* to *user_id*."""
        member = self._members.get(user_id)
        if member is None:
            return False
        member.permissions.add(*permissions)
        return True

    def revoke(self, user_id: str, permission: str) -> bool:
        member = self._members.get(user_id)
        if member is None:
            return False
        return member.permissions.remove(permission)

    # ------------------------------------------------------------------
    # Key / OAuth bindings
    # ------------------------------------------------------------------

    def bind_api_key(self, user_id: str, key_id: str) -> bool:
        member = self._members.get(user_id)
        if member is None:
            return False
        if key_id not in member.api_key_ids:
            member.api_key_ids.append(key_id)
        return True

    def bind_oauth(self, user_id: str, provider: str) -> bool:
        member = self._members.get(user_id)
        if member is None:
            return False
        if provider not in member.oauth_providers:
            member.oauth_providers.append(provider)
        return True

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "owner_user_id": self.owner_user_id,
            "members": {uid: m.to_dict() for uid, m in self._members.items()},
        }

    def __repr__(self) -> str:
        return f"AuthWorkspace(id={self.workspace_id!r}, members={len(self._members)})"
