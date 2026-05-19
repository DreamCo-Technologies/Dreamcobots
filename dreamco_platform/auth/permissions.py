"""
DreamCo Platform — Auth Permissions
=====================================

Defines the ``Permission`` model and the ``PermissionSet`` container.
All RBAC checks ultimately reduce to: does this actor hold the required
``Permission`` in the target workspace?

This module is intentionally separate from ``governance/rbac.py`` so that
auth-layer permissions (identity, API keys, OAuth) remain decoupled from the
governance-layer RBAC graph.

Usage::

    perms = PermissionSet({"read:bots", "invoke:capability"})
    perms.has("invoke:capability")  # True
    perms.add("write:bots")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Permission constants (well-known permission strings)
# ---------------------------------------------------------------------------

class Permissions:
    """Namespace of canonical permission strings."""

    # Bot permissions
    READ_BOTS = "read:bots"
    WRITE_BOTS = "write:bots"
    DEPLOY_BOTS = "deploy:bots"
    DELETE_BOTS = "delete:bots"

    # Capability permissions
    INVOKE_CAPABILITY = "invoke:capability"
    READ_CAPABILITY = "read:capability"
    WRITE_CAPABILITY = "write:capability"

    # Workflow permissions
    RUN_WORKFLOW = "run:workflow"
    READ_WORKFLOW = "read:workflow"
    WRITE_WORKFLOW = "write:workflow"

    # Marketplace permissions
    LIST_MARKETPLACE = "read:marketplace"
    PUBLISH_MARKETPLACE = "publish:marketplace"
    PURCHASE_MARKETPLACE = "purchase:marketplace"

    # Admin permissions
    ADMIN_WORKSPACE = "admin:workspace"
    ADMIN_USERS = "admin:users"
    ADMIN_BILLING = "admin:billing"
    ADMIN_POLICIES = "admin:policies"

    # Governance
    APPROVE_HIGH_COST = "approve:high_cost"
    OVERRIDE_POLICY = "override:policy"

    @classmethod
    def all_permissions(cls) -> list[str]:
        return [
            v for k, v in vars(cls).items()
            if not k.startswith("_") and isinstance(v, str)
        ]


# ---------------------------------------------------------------------------
# PermissionSet
# ---------------------------------------------------------------------------

class PermissionSet:
    """A mutable set of permission strings for a user/role."""

    def __init__(self, permissions: set[str] | list[str] | None = None) -> None:
        self._perms: set[str] = set(permissions or [])

    def has(self, permission: str) -> bool:
        return permission in self._perms or "*" in self._perms

    def has_all(self, permissions: list[str]) -> bool:
        return all(self.has(p) for p in permissions)

    def has_any(self, permissions: list[str]) -> bool:
        return any(self.has(p) for p in permissions)

    def add(self, *permissions: str) -> None:
        self._perms.update(permissions)

    def remove(self, permission: str) -> bool:
        if permission in self._perms:
            self._perms.remove(permission)
            return True
        return False

    def union(self, other: "PermissionSet") -> "PermissionSet":
        return PermissionSet(self._perms | other._perms)

    def to_list(self) -> list[str]:
        return sorted(self._perms)

    def __len__(self) -> int:
        return len(self._perms)

    def __repr__(self) -> str:
        return f"PermissionSet({sorted(self._perms)})"
