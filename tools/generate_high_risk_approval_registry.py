#!/usr/bin/env python3
"""Generate the Buddy money-help approval registry for high-risk bots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = ROOT / "reports" / "buddy_capability_inventory.json"
APPROVAL_DIR = ROOT / "config" / "production_approvals"
APPROVAL_FILE = APPROVAL_DIR / "high_risk_bot_approvals.json"
REQUIRED_BUDDY_MONEY_REQUEST = (
    "Buddy, help me make money with this bot. "
    "I approve the listed live actions and understand the risks."
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def high_risk_reason(bot: dict) -> list[str]:
    text = " ".join(
        str(bot.get(key, ""))
        for key in ("slug", "name", "division", "category", "description")
    ).lower()
    reasons = []
    terms = {
        "money_movement": ("payment", "billing", "ach", "stripe", "wallet"),
        "financial_or_trading": ("trading", "crypto", "staking", "forex", "stock"),
        "credit_or_loans": ("loan", "credit"),
        "legal_or_tax": ("legal", "tax"),
        "health_or_medical": ("health", "medical", "biomedical", "telehealth"),
        "security_or_defense": ("security", "cyber", "defense"),
        "fraud_or_compliance": ("fraud", "compliance"),
    }
    for reason, matches in terms.items():
        if any(match in text for match in matches):
            reasons.append(reason)
    return reasons or ["high_risk_domain"]


def default_entry(bot: dict, existing: dict | None = None) -> dict:
    existing = existing or {}
    return {
        "slug": bot["slug"],
        "name": bot["name"],
        "division": bot.get("division"),
        "category": bot.get("category"),
        "risk_reasons": high_risk_reason(bot),
        "required_buddy_money_request": REQUIRED_BUDDY_MONEY_REQUEST,
        "user_asked_buddy_to_help_make_money": existing.get(
            "user_asked_buddy_to_help_make_money", False
        ),
        "risk_acknowledged": existing.get("risk_acknowledged", False),
        "approved": existing.get("approved", False),
        "approved_by": existing.get("approved_by"),
        "approved_at": existing.get("approved_at"),
        "allowed_live_actions": existing.get("allowed_live_actions", []),
        "disallowed_live_actions": existing.get(
            "disallowed_live_actions",
            [
                "move_money_without_final_user_confirmation",
                "place_trades_without_final_user_confirmation",
                "send_legal_or_medical_advice_as_final_advice",
                "run_security_actions_against third-party systems without authorization",
            ],
        ),
        "checklist": {
            "sandbox_smoke_test_passed": existing.get("checklist", {}).get(
                "sandbox_smoke_test_passed", False
            ),
            "no_unapproved_live_money_movement": existing.get("checklist", {}).get(
                "no_unapproved_live_money_movement", False
            ),
            "secrets_are_environment_only": existing.get("checklist", {}).get(
                "secrets_are_environment_only", False
            ),
            "audit_logging_enabled": existing.get("checklist", {}).get(
                "audit_logging_enabled", False
            ),
            "human_review_before_external_action": existing.get("checklist", {}).get(
                "human_review_before_external_action", False
            ),
        },
        "notes": existing.get(
            "notes",
            "Approval is intentionally false until the user asks Buddy for money help and approves live actions.",
        ),
    }


def main() -> None:
    inventory = load_json(INVENTORY_FILE)
    existing = load_json(APPROVAL_FILE)
    existing_by_slug = {
        entry.get("slug"): entry for entry in existing.get("approvals", []) if entry.get("slug")
    }
    high_risk_bots = [
        bot
        for bot in inventory.get("bots", [])
        if bot.get("risk_hint") == "high"
        or bot.get("production_readiness_status") == "production_candidate_approval_required"
    ]
    approvals = [
        default_entry(bot, existing_by_slug.get(bot["slug"]))
        for bot in sorted(high_risk_bots, key=lambda item: str(item["slug"]))
    ]
    report = {
        "schema": "dreamco.high_risk_bot_buddy_money_approvals.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "required_buddy_money_request": REQUIRED_BUDDY_MONEY_REQUEST,
        "approval_rule": (
            "A high-risk bot becomes production-approved only after the user asks Buddy "
            "to help make money, acknowledges risk, and approves specific live actions."
        ),
        "approvals_required": len(approvals),
        "approvals_granted": sum(1 for entry in approvals if entry.get("approved") is True),
        "approvals": approvals,
    }
    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    APPROVAL_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "approval_file": str(APPROVAL_FILE.relative_to(ROOT)),
                "approvals_required": report["approvals_required"],
                "approvals_granted": report["approvals_granted"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
