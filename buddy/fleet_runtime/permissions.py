"""Permission policy for fleet runs, derived from Buddy's approval policy.

Source of truth: buddy_os/governance/approval_policy.yaml. Levels whose
``approval`` is ``none`` may run unattended; every other level returns
``approval_required`` without acting. This runtime never self-approves.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .contract import ROOT

POLICY_PATH = ROOT / "buddy_os" / "governance" / "approval_policy.yaml"

# Used only when PyYAML is unavailable; tests assert it matches the YAML file.
FALLBACK_LEVELS: dict[str, dict[str, Any]] = {
    "read_only": {"allowed": True, "approval": "none"},
    "sandbox": {"allowed": True, "approval": "none"},
    "repository_write": {"allowed": "governed", "approval": "user_or_repository_policy"},
    "external_side_effect": {"allowed": "governed", "approval": "explicit"},
    "destructive": {"allowed": "governed", "approval": "explicit_and_secondary_guard"},
    "production_deploy": {"allowed": "governed", "approval": "explicit_and_release_gate"},
}

# Words that mean a step would touch the outside world. Used to flag
# workflow steps and to cap a bot's ceiling at plan_only.
LIVE_ACTION_RE = re.compile(
    r"\b(send|sends|sending|cold email|mass email|email blast|sms|text message|publish|post to|posting|pay|payment|payout|"
    r"wire|transfer funds|trade|trading|order execution|purchase|checkout|deploy|delete|outreach|"
    r"cold call|dial|submit|file with|charge|invoice send|broadcast|mint|withdraw)\b",
    re.I,
)

CEILING_LEVELS = {
    "read_only": {"read_only"},
    "sandbox": {"read_only", "sandbox"},
    # plan_only bots may run sandbox computations but every live step is
    # emitted as a plan item that needs explicit approval.
    "plan_only": {"read_only", "sandbox"},
}


@lru_cache(maxsize=1)
def load_levels(path: str = str(POLICY_PATH)) -> dict[str, dict[str, Any]]:
    try:
        import yaml  # type: ignore
    except Exception:  # pragma: no cover - exercised only without PyYAML
        return dict(FALLBACK_LEVELS)
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(data.get("levels", {}))


def unattended_levels() -> set[str]:
    return {name for name, rule in load_levels().items() if rule.get("approval") == "none"}


def decide(ceiling: str, requested_level: str) -> dict[str, Any]:
    """Return the permission decision for a run.

    ``allowed`` is True only when the requested level needs no approval under
    the policy AND is inside the bot's ceiling.
    """
    levels = load_levels()
    if requested_level not in levels:
        return {"allowed": False, "decision": "unknown_level", "requested_level": requested_level,
                "approval": "explicit", "policy": "buddy_os/governance/approval_policy.yaml"}
    rule = levels[requested_level]
    within_ceiling = requested_level in CEILING_LEVELS.get(ceiling, set())
    unattended = rule.get("approval") == "none"
    allowed = within_ceiling and unattended
    return {
        "allowed": allowed,
        "decision": "allowed" if allowed else "approval_required",
        "requested_level": requested_level,
        "ceiling": ceiling,
        "approval": rule.get("approval"),
        "policy": "buddy_os/governance/approval_policy.yaml",
    }


def text_declares_live_action(text: str) -> bool:
    return bool(LIVE_ACTION_RE.search(text or ""))
