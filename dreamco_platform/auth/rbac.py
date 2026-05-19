"""
DreamCo Platform — Auth RBAC
================================

``AuthRBAC`` is the auth-layer enforcement gate.

CORE RULE (from the blueprint):

    Every execution checks:

        if not has_permission(user, capability):
            deny()

``AuthRBAC`` wires together:
* ``AuthWorkspace`` — per-workspace members and permission sets
* The broader role hierarchy (delegates to ``governance/rbac.py``)
* API-key and OAuth identity resolution

Usage::

    rbac = AuthRBAC()
    ws = rbac.create_workspace("ws_acme", owner="user:alice")
    ws.add_member("user:bob", PermissionSet({"invoke:capability"}))

    rbac.check("user:bob", "invoke:capability", workspace_id="ws_acme")  # True
    rbac.check("user:bob", "admin:users", workspace_id="ws_acme")        # False

    # Or raise on denial:
    rbac.enforce("user:bob", "invoke:capability", workspace_id="ws_acme")
"""

from __future__ import annotations

from typing import Any

from dreamco_platform.auth.permissions import PermissionSet
from dreamco_platform.auth.workspace import AuthWorkspace


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class AccessDeniedError(PermissionError):
    """Raised when ``AuthRBAC.enforce()`` denies an operation."""


# ---------------------------------------------------------------------------
# AuthRBAC
# ---------------------------------------------------------------------------

class AuthRBAC:
    """Auth-layer RBAC enforcement gate.

    Manages a collection of ``AuthWorkspace`` objects and provides a single
    ``check()`` / ``enforce()`` entry point.
    """

    def __init__(self) -> None:
        self._workspaces: dict[str, AuthWorkspace] = {}

    # ------------------------------------------------------------------
    # Workspace management
    # ------------------------------------------------------------------

    def create_workspace(
        self,
        workspace_id: str,
        owner: str,
        initial_permissions: PermissionSet | None = None,
    ) -> AuthWorkspace:
        if workspace_id in self._workspaces:
            raise ValueError(f"Workspace '{workspace_id}' already exists")
        ws = AuthWorkspace(workspace_id=workspace_id, owner_user_id=owner)
        if initial_permissions:
            owner_member = ws.get_member(owner)
            if owner_member:
                owner_member.permissions = initial_permissions
        self._workspaces[workspace_id] = ws
        return ws

    def get_workspace(self, workspace_id: str) -> AuthWorkspace | None:
        return self._workspaces.get(workspace_id)

    def delete_workspace(self, workspace_id: str) -> bool:
        if workspace_id not in self._workspaces:
            return False
        del self._workspaces[workspace_id]
        return True

    # ------------------------------------------------------------------
    # Permission check / enforcement
    # ------------------------------------------------------------------

    def check(
        self,
        user_id: str,
        permission: str,
        workspace_id: str,
    ) -> bool:
        """Return True if *user_id* holds *permission* in *workspace_id*."""
        ws = self._workspaces.get(workspace_id)
        if ws is None:
            return False
        return ws.can(user_id, permission)

    def enforce(
        self,
        user_id: str,
        permission: str,
        workspace_id: str,
    ) -> None:
        """Raise ``AccessDeniedError`` if the check fails."""
        if not self.check(user_id, permission, workspace_id):
            raise AccessDeniedError(
                f"User '{user_id}' lacks permission '{permission}' "
                f"in workspace '{workspace_id}'"
            )

    def workspaces_for_user(self, user_id: str) -> list[str]:
        """Return all workspace_ids where *user_id* is a member."""
        return [
            ws_id for ws_id, ws in self._workspaces.items()
            if ws.is_member(user_id)
        ]

    def stats(self) -> dict[str, Any]:
        return {
            "workspaces": len(self._workspaces),
            "total_members": sum(len(ws._members) for ws in self._workspaces.values()),
        }
