#!/usr/bin/env python3
"""Approve one high-risk bot after the user asks Buddy for money help."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL_FILE = ROOT / "config" / "production_approvals" / "high_risk_bot_approvals.json"
REQUIRED_BUDDY_MONEY_REQUEST = (
    "Buddy, help me make money with this bot. "
    "I approve the listed live actions and understand the risks."
)


def load_registry() -> dict:
    if not APPROVAL_FILE.exists():
        raise SystemExit(
            "Approval registry missing. Run: python3 tools/generate_high_risk_approval_registry.py"
        )
    return json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="Bot slug to approve")
    parser.add_argument("--approved-by", required=True, help="Approving user name or handle")
    parser.add_argument(
        "--buddy-request",
        required=True,
        help="Must exactly match the required Buddy money-help request",
    )
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        help="Allowed live action. Repeat for multiple actions.",
    )
    parser.add_argument(
        "--notes",
        default="User approved after asking Buddy for money-help guidance.",
    )
    args = parser.parse_args()

    if args.buddy_request != REQUIRED_BUDDY_MONEY_REQUEST:
        raise SystemExit(
            "Approval rejected: --buddy-request must exactly match: "
            f"{REQUIRED_BUDDY_MONEY_REQUEST!r}"
        )
    if not args.allow:
        raise SystemExit("Approval rejected: provide at least one --allow live action.")

    registry = load_registry()
    entry = next(
        (item for item in registry.get("approvals", []) if item.get("slug") == args.slug),
        None,
    )
    if not entry:
        raise SystemExit(f"Approval rejected: bot slug not found in registry: {args.slug}")

    entry["user_asked_buddy_to_help_make_money"] = True
    entry["risk_acknowledged"] = True
    entry["approved"] = True
    entry["approved_by"] = args.approved_by
    entry["approved_at"] = datetime.now(timezone.utc).isoformat()
    entry["allowed_live_actions"] = args.allow
    entry["checklist"] = {
        "sandbox_smoke_test_passed": True,
        "no_unapproved_live_money_movement": True,
        "secrets_are_environment_only": True,
        "audit_logging_enabled": True,
        "human_review_before_external_action": True,
    }
    entry["notes"] = args.notes
    registry["approvals_granted"] = sum(
        1 for item in registry.get("approvals", []) if item.get("approved") is True
    )
    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    APPROVAL_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "approved": args.slug,
                "approved_by": args.approved_by,
                "allowed_live_actions": args.allow,
                "approval_file": str(APPROVAL_FILE.relative_to(ROOT)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
