"""
DreamCo Platform — RBAC and Workspace Isolation
=================================================

Role-Based Access Control for the DreamCo platform.  Extends the existing
``ClientApiKeyRegistry`` permission model with:

* Named roles composed of fine-grained ``Permission`` tokens
* Workspaces that provide organisational isolation
* Hierarchical role inheritance
* Policy-enforcement-ready permission checks at execution boundaries

Design
------
This module is intentionally decoupled from the existing ``saas/auth/``
layer so it can be adopted incrementally.  In a future consolidation, the
``ClientApiKeyRegistry`` categories (``read_only``, ``full_access``, etc.)
map directly to roles defined here.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Set


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

class Permission(str, Enum):
    # Bot management
    BOT_READ = "bot:read"
    BOT_RUN = "bot:run"
    BOT_DEPLOY = "bot:deploy"
    BOT_ADMIN = "bot:admin"

    # Workflow management
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_EXECUTE = "workflow:execute"
    WORKFLOW_ADMIN = "workflow:admin"

    # Marketplace
    MARKETPLACE_READ = "marketplace:read"
    MARKETPLACE_PUBLISH = "marketplace:publish"
    MARKETPLACE_ADMIN = "marketplace:admin"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    BILLING_ADMIN = "billing:admin"

    # Governance
    POLICY_READ = "policy:read"
    POLICY_WRITE = "policy:write"
    POLICY_ADMIN = "policy:admin"

    # Learning
    LEARNING_READ = "learning:read"
    LEARNING_TRIGGER = "learning:trigger"
    LEARNING_ADMIN = "learning:admin"

    # Analytics / observability
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_ADMIN = "analytics:admin"

    # Security / RBAC
    RBAC_READ = "rbac:read"
    RBAC_WRITE = "rbac:write"
    RBAC_ADMIN = "rbac:admin"

    # Platform-wide super permission
    SUPERADMIN = "superadmin"


# Convenience permission sets for common role archetypes
_READ_ONLY_PERMISSIONS: FrozenSet[Permission] = frozenset({
    Permission.BOT_READ,
    Permission.WORKFLOW_READ,
    Permission.MARKETPLACE_READ,
    Permission.BILLING_READ,
    Permission.POLICY_READ,
    Permission.LEARNING_READ,
    Permission.ANALYTICS_READ,
    Permission.RBAC_READ,
})

_DEVELOPER_PERMISSIONS: FrozenSet[Permission] = _READ_ONLY_PERMISSIONS | frozenset({
    Permission.BOT_RUN,
    Permission.WORKFLOW_EXECUTE,
    Permission.MARKETPLACE_PUBLISH,
})

_OPERATOR_PERMISSIONS: FrozenSet[Permission] = _DEVELOPER_PERMISSIONS | frozenset({
    Permission.BOT_DEPLOY,
    Permission.BOT_ADMIN,
    Permission.WORKFLOW_ADMIN,
    Permission.BILLING_WRITE,
    Permission.POLICY_WRITE,
    Permission.LEARNING_TRIGGER,
    Permission.ANALYTICS_ADMIN,
    Permission.RBAC_READ,
})

_ADMIN_PERMISSIONS: FrozenSet[Permission] = frozenset(Permission)  # all permissions


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------

@dataclass
class Role:
    """
    A named collection of ``Permission`` tokens.

    Attributes
    ----------
    role_id : str
        Unique identifier (e.g. ``"developer"``, ``"operator"``).
    name : str
        Human-readable display name.
    permissions : set[Permission]
        The permissions granted by this role.
    description : str
        Optional description.
    parent_role_id : str | None
        ID of a parent role whose permissions this role inherits.
    metadata : dict
        Arbitrary extra metadata.
    """

    role_id: str
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""
    parent_role_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_permission(self, permission: Permission) -> bool:
        """Return ``True`` if this role directly grants *permission*."""
        return permission in self.permissions or Permission.SUPERADMIN in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "name": self.name,
            "permissions": sorted(p.value for p in self.permissions),
            "description": self.description,
            "parent_role_id": self.parent_role_id,
            "metadata": dict(self.metadata),
        }

    # ------------------------------------------------------------------
    # Built-in role factories
    # ------------------------------------------------------------------

    @classmethod
    def read_only(cls) -> "Role":
        return cls(
            role_id="read_only",
            name="Read Only",
            permissions=set(_READ_ONLY_PERMISSIONS),
            description="Can view all platform data but cannot modify anything.",
        )

    @classmethod
    def developer(cls) -> "Role":
        return cls(
            role_id="developer",
            name="Developer",
            permissions=set(_DEVELOPER_PERMISSIONS),
            description="Can read, run bots, execute workflows, and publish to marketplace.",
            parent_role_id="read_only",
        )

    @classmethod
    def operator(cls) -> "Role":
        return cls(
            role_id="operator",
            name="Operator",
            permissions=set(_OPERATOR_PERMISSIONS),
            description="Full operational access; cannot manage RBAC assignments.",
            parent_role_id="developer",
        )

    @classmethod
    def admin(cls) -> "Role":
        return cls(
            role_id="admin",
            name="Administrator",
            permissions=set(_ADMIN_PERMISSIONS),
            description="Unrestricted platform access.",
        )


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------

@dataclass
class Workspace:
    """
    An isolated operational boundary within DreamCo.

    All bots, workflows, and data within a workspace are logically
    separated from other workspaces.  Members have roles scoped to
    their workspace.

    Attributes
    ----------
    workspace_id : str
        Unique identifier.
    name : str
        Human-readable workspace name.
    owner_id : str
        User ID of the workspace owner.
    members : dict[str, str]
        Mapping ``user_id → role_id`` for workspace members.
    created_at : float
        Unix timestamp of creation.
    metadata : dict
        Arbitrary extra metadata.
    """

    workspace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    owner_id: str = ""
    members: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_member(self, user_id: str, role_id: str) -> None:
        """Add *user_id* to this workspace with *role_id*."""
        self.members[user_id] = role_id

    def remove_member(self, user_id: str) -> Optional[str]:
        """Remove *user_id* from this workspace. Returns their old role_id or None."""
        return self.members.pop(user_id, None)

    def get_member_role(self, user_id: str) -> Optional[str]:
        """Return the role_id assigned to *user_id*, or ``None``."""
        return self.members.get(user_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "owner_id": self.owner_id,
            "members": dict(self.members),
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    def __repr__(self) -> str:
        return f"Workspace(id={self.workspace_id!r}, name={self.name!r}, members={len(self.members)})"


# ---------------------------------------------------------------------------
# RBAC registry
# ---------------------------------------------------------------------------

class RBACRegistry:
    """
    Central registry for roles and workspaces.

    Provides:
    * Role CRUD (with inheritance resolution)
    * Workspace CRUD with member management
    * Permission checks (``user_has_permission``)
    * Effective permission enumeration (with role inheritance)
    """

    def __init__(self) -> None:
        self._roles: Dict[str, Role] = {}
        self._workspaces: Dict[str, Workspace] = {}
        # Seed built-in roles
        for role in (Role.read_only(), Role.developer(), Role.operator(), Role.admin()):
            self._roles[role.role_id] = role

    # ------------------------------------------------------------------
    # Role management
    # ------------------------------------------------------------------

    def add_role(self, role: Role) -> None:
        """Register *role*. Replaces any existing role with the same ``role_id``."""
        self._roles[role.role_id] = role

    def get_role(self, role_id: str) -> Optional[Role]:
        return self._roles.get(role_id)

    def list_roles(self) -> List[Role]:
        return sorted(self._roles.values(), key=lambda r: r.role_id)

    def effective_permissions(self, role_id: str) -> Set[Permission]:
        """
        Return the full set of permissions for *role_id*, including
        any inherited from parent roles.
        """
        visited: Set[str] = set()
        permissions: Set[Permission] = set()
        queue = [role_id]
        while queue:
            rid = queue.pop(0)
            if rid in visited:
                continue
            visited.add(rid)
            role = self._roles.get(rid)
            if role is None:
                continue
            permissions.update(role.permissions)
            if role.parent_role_id:
                queue.append(role.parent_role_id)
        return permissions

    # ------------------------------------------------------------------
    # Workspace management
    # ------------------------------------------------------------------

    def create_workspace(self, name: str, owner_id: str, **kwargs: Any) -> Workspace:
        """Create and register a new workspace."""
        ws = Workspace(name=name, owner_id=owner_id, **kwargs)
        ws.add_member(owner_id, "admin")
        self._workspaces[ws.workspace_id] = ws
        return ws

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

    def list_workspaces(self) -> List[Workspace]:
        return sorted(self._workspaces.values(), key=lambda w: w.name)

    def delete_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.pop(workspace_id, None)

    # ------------------------------------------------------------------
    # Permission checks
    # ------------------------------------------------------------------

    def user_has_permission(
        self,
        user_id: str,
        workspace_id: str,
        permission: Permission,
    ) -> bool:
        """
        Return ``True`` if *user_id* holds *permission* in *workspace_id*.

        Looks up the user's workspace role, then resolves effective
        permissions (including inheritance).
        """
        ws = self._workspaces.get(workspace_id)
        if ws is None:
            return False
        role_id = ws.get_member_role(user_id)
        if role_id is None:
            return False
        effective = self.effective_permissions(role_id)
        return permission in effective or Permission.SUPERADMIN in effective

    def get_user_permissions(self, user_id: str, workspace_id: str) -> Set[Permission]:
        """Return all effective permissions for *user_id* in *workspace_id*."""
        ws = self._workspaces.get(workspace_id)
        if ws is None:
            return set()
        role_id = ws.get_member_role(user_id)
        if role_id is None:
            return set()
        return self.effective_permissions(role_id)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"RBACRegistry(roles={len(self._roles)}, "
            f"workspaces={len(self._workspaces)})"
        )
