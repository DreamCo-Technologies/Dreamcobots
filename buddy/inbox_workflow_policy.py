"""Buddy-owned inbox and workflow authorization policy (stdlib only).

This is an enforceable local policy boundary, not an email provider, mailbox
provisioning tool, or remote workflow executor. External adapters must validate
OAuth scopes and use this gate before performing actions.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

READ_ACTIONS = frozenset({"inbox.list", "inbox.read", "workflow.inspect", "workflow.status"})
REVIEW_ACTIONS = frozenset({"inbox.draft", "workflow.plan", "workflow.test"})
CONFIRM_ACTIONS = frozenset({"inbox.send", "inbox.delete", "workflow.dispatch", "workflow.cancel"})
BLOCKED_ACTIONS = frozenset({"workflow.deploy_production", "workflow.merge_main",
                             "account.change_security", "billing.charge"})


@dataclass(frozen=True)
class Authorization:
    user_id: str
    connected_account_id: str
    allowed_actions: frozenset[str]
    expires_at: datetime
    revoked: bool = False


def authorize(action: str, auth: Authorization, *, user_id: str,
              connected_account_id: str, confirmed: bool = False,
              now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or auth.expires_at.tzinfo is None:
        raise ValueError("Timezone-aware timestamps required")
    if action in BLOCKED_ACTIONS:
        return {"allowed": False, "reason": "separate_high_impact_approval_required"}
    if action not in READ_ACTIONS | REVIEW_ACTIONS | CONFIRM_ACTIONS:
        return {"allowed": False, "reason": "unknown_action"}
    if auth.revoked or now >= auth.expires_at:
        return {"allowed": False, "reason": "revoked_or_expired"}
    if user_id != auth.user_id or connected_account_id != auth.connected_account_id:
        return {"allowed": False, "reason": "account_owner_mismatch"}
    if action not in auth.allowed_actions:
        return {"allowed": False, "reason": "missing_scope"}
    if action in CONFIRM_ACTIONS and confirmed is not True:
        return {"allowed": False, "reason": "per_action_confirmation_required"}
    return {"allowed": True, "reason": "authorized", "action": action}


def workflow_plan(steps: list[dict], auth: Authorization, *, user_id: str,
                  connected_account_id: str) -> dict:
    """Dry-run a proposed workflow; does not execute or schedule any step."""
    if not isinstance(steps, list) or len(steps) > 100:
        raise ValueError("Invalid workflow step count")
    decisions = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict) or not isinstance(step.get("action"), str):
            raise ValueError("Malformed step")
        decision = authorize(step["action"], auth, user_id=user_id,
                             connected_account_id=connected_account_id)
        decisions.append({"index": index, "action": step["action"], **decision})
    return {"status": "dry_run_only", "steps": decisions,
            "ready_for_automatic_execution": all(x["allowed"] for x in decisions)}
