"""
Governance and security layer for the DreamCo Global AI Learning System.

Implements role-based access control (RBAC) and immutable audit logging
for all system actions.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_GOVERNANCE
from framework import GlobalAISourcesFlow  # noqa: F401


class AccessRole(Enum):
    ADMIN = "admin"
    DATA_ENGINEER = "data_engineer"
    ML_ENGINEER = "ml_engineer"
    ANALYST = "analyst"
    VIEWER = "viewer"


@dataclass
class AuditLogEntry:
    """An immutable record of an access control decision.

    Attributes
    ----------
    id : str
        Unique log entry identifier (UUID4).
    timestamp : datetime.datetime
        UTC timestamp of the access attempt.
    actor : str
        Username or service account identifier.
    role : AccessRole
        Role held by the actor.
    action : str
        The action being attempted.
    resource : str
        The resource being accessed.
    status : str
        ``"allowed"`` or ``"denied"``.
    metadata : dict
        Additional context.
    """

    id: str
    timestamp: datetime.datetime
    actor: str
    role: AccessRole
    action: str
    resource: str
    status: str
    metadata: dict = field(default_factory=dict)


class GovernanceTierError(Exception):
    """Raised when the current tier does not support governance features."""


class RBACError(Exception):
    """Raised when an actor does not have permission to perform an action."""


# ---------------------------------------------------------------------------
# Permission matrix
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict = {
    AccessRole.ADMIN: [
        "ingest", "classify", "sandbox", "analytics",
        "hybrid", "deploy", "govern", "audit",
    ],
    AccessRole.DATA_ENGINEER: ["ingest", "classify"],
    AccessRole.ML_ENGINEER: ["classify", "sandbox", "analytics", "hybrid"],
    AccessRole.ANALYST: ["analytics", "audit"],
    AccessRole.VIEWER: ["audit"],
}


class GovernanceLayer:
    """Enforces RBAC and maintains an immutable audit log.

    Parameters
    ----------
    tier : Tier
        Subscription tier (PRO and above support governance).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._audit_log: List[AuditLogEntry] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_permission(
        self,
        actor: str,
        role: AccessRole,
        action: str,
        resource: str = "system",
    ) -> bool:
        """Check RBAC permission and log the attempt.

        Parameters
        ----------
        actor : str
            The actor's username or service account.
        role : AccessRole
            The role the actor is acting under.
        action : str
            The action to authorise.
        resource : str
            Resource being accessed (default: ``"system"``).

        Returns
        -------
        bool
            ``True`` if the action is permitted; ``False`` otherwise.

        Raises
        ------
        GovernanceTierError
            If the current tier does not support governance.
        """
        self._check_tier()
        allowed = action in ROLE_PERMISSIONS.get(role, [])
        status = "allowed" if allowed else "denied"
        self._log(actor, role, action, resource, status)
        return allowed

    def enforce(
        self,
        actor: str,
        role: AccessRole,
        action: str,
        resource: str = "system",
    ) -> None:
        """Check permission and raise RBACError if denied.

        Parameters
        ----------
        actor : str
            The actor's username.
        role : AccessRole
            Role to check against.
        action : str
            Action to authorise.
        resource : str
            Resource being accessed (default: ``"system"``).

        Raises
        ------
        RBACError
            If the actor is not permitted to perform *action*.
        GovernanceTierError
            If the current tier does not support governance.
        """
        if not self.check_permission(actor, role, action, resource):
            raise RBACError(
                f"Actor '{actor}' with role '{role.value}' is not permitted "
                f"to perform action '{action}' on resource '{resource}'."
            )

    def get_audit_log(self) -> List[AuditLogEntry]:
        """Return a copy of the immutable audit log."""
        return list(self._audit_log)

    def get_stats(self) -> dict:
        """Return a summary of governance activity."""
        allowed = sum(1 for e in self._audit_log if e.status == "allowed")
        denied = sum(1 for e in self._audit_log if e.status == "denied")
        return {
            "total_audit_entries": len(self._audit_log),
            "allowed": allowed,
            "denied": denied,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_GOVERNANCE):
            raise GovernanceTierError(
                f"Governance and security features are not available on the "
                f"{self.config.name} tier. Upgrade to Pro or Enterprise."
            )

    def _log(
        self,
        actor: str,
        role: AccessRole,
        action: str,
        resource: str,
        status: str,
    ) -> None:
        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
            actor=actor,
            role=role,
            action=action,
            resource=resource,
            status=status,
        )
        self._audit_log.append(entry)
