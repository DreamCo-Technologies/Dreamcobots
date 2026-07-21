"""
compliance_engine.py — Enforces compliance and logging processes.

Manages audit logging, policy enforcement, and regulatory compliance
(e.g. GDPR, HIPAA) for operations performed within the DreamCo platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Supported compliance standards
# ---------------------------------------------------------------------------

POLICY_GDPR = "GDPR"
POLICY_HIPAA = "HIPAA"
POLICY_SOC2 = "SOC2"
POLICY_ISO27001 = "ISO27001"

ALL_POLICIES = [POLICY_GDPR, POLICY_HIPAA, POLICY_SOC2, POLICY_ISO27001]


@dataclass
class AuditEntry:
    """A single immutable audit log entry."""

    event_id: str
    actor: str
    action: str
    resource: str
    outcome: str  # "success" | "denied" | "error"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceEngine:
    """
    Enforces governance policies and maintains an immutable audit log.

    Parameters
    ----------
    active_policies : list[str]
        Compliance standards to enforce. Any action not permitted under all
        active policies is blocked.
    """

    def __init__(self, active_policies: Optional[List[str]] = None):
        self.active_policies: List[str] = active_policies or [POLICY_GDPR]
        self._audit_log: List[AuditEntry] = []
        self._event_counter: int = 0

        for policy in self.active_policies:
            if policy not in ALL_POLICIES:
                raise ValueError(
                    f"Unknown policy '{policy}'. Valid: {ALL_POLICIES}"
                )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def check(self, actor: str, action: str, resource: str) -> bool:
        """
        Check whether *actor* is permitted to perform *action* on *resource*.

        The default implementation allows all actions; override or extend
        for production rule-based checks.

        Returns
        -------
        bool
            ``True`` if the action is permitted.
        """
        permitted = self._evaluate_policies(actor, action, resource)
        outcome = "success" if permitted else "denied"
        self._log(actor=actor, action=action, resource=resource, outcome=outcome)
        return permitted

    def enforce(self, actor: str, action: str, resource: str) -> None:
        """
        Enforce policy; raise ``PermissionError`` if the action is denied.

        Parameters
        ----------
        actor : str
        action : str
        resource : str

        Raises
        ------
        PermissionError
            If the action is not permitted.
        """
        if not self.check(actor, action, resource):
            raise PermissionError(
                f"Actor '{actor}' is not permitted to '{action}' on '{resource}'."
            )

    def get_audit_log(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> List[AuditEntry]:
        """
        Retrieve audit log entries with optional filters.

        Parameters
        ----------
        actor : str | None
        action : str | None
        outcome : str | None
        """
        entries = self._audit_log
        if actor is not None:
            entries = [e for e in entries if e.actor == actor]
        if action is not None:
            entries = [e for e in entries if e.action == action]
        if outcome is not None:
            entries = [e for e in entries if e.outcome == outcome]
        return list(entries)

    def enable_policy(self, policy: str) -> None:
        """Enable an additional compliance policy."""
        if policy not in ALL_POLICIES:
            raise ValueError(f"Unknown policy '{policy}'. Valid: {ALL_POLICIES}")
        if policy not in self.active_policies:
            self.active_policies.append(policy)

    def disable_policy(self, policy: str) -> None:
        """Disable a compliance policy."""
        if policy in self.active_policies:
            self.active_policies.remove(policy)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evaluate_policies(self, actor: str, action: str, resource: str) -> bool:
        """
        Apply each active policy rule.

        The default implementation permits all actions. In production,
        each policy would apply its own rule set.
        """
        return True

    def _log(self, actor: str, action: str, resource: str, outcome: str, metadata: Optional[Dict[str, Any]] = None) -> AuditEntry:
        self._event_counter += 1
        entry = AuditEntry(
            event_id=f"evt_{self._event_counter:06d}",
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            metadata=metadata or {},
        )
        self._audit_log.append(entry)
        return entry
