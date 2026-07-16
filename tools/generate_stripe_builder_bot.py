#!/usr/bin/env python3
"""Generate the Buddy Stripe Builder bot contract."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "reports" / "stripe_builder_bot.json"
OUTPUT_MD = ROOT / "reports" / "STRIPE_BUILDER_BOT.md"

BUILD_MODULES = [
    {
        "id": "offer_catalog_builder",
        "label": "Offer Catalog Builder",
        "builds": ["products", "prices", "tiers", "trial rules", "refund policy notes"],
    },
    {
        "id": "checkout_builder",
        "label": "Checkout Builder",
        "builds": ["payment link drafts", "checkout session config", "success URL", "cancel URL"],
    },
    {
        "id": "subscription_builder",
        "label": "Subscription Builder",
        "builds": ["monthly plans", "annual plans", "upgrade paths", "dunning notes"],
    },
    {
        "id": "webhook_builder",
        "label": "Webhook Builder",
        "builds": ["event allowlist", "signature verification checklist", "retry plan", "event ledger schema"],
    },
    {
        "id": "payment_notification_builder",
        "label": "Payment Notification Builder",
        "builds": ["owner email alerts", "GitHub issue alerts", "dashboard payment feed", "failure notices"],
    },
    {
        "id": "test_mode_builder",
        "label": "Test Mode Builder",
        "builds": ["test cards checklist", "webhook fixture plan", "refund test", "subscription lifecycle test"],
    },
    {
        "id": "secret_setup_builder",
        "label": "Secret Setup Builder",
        "builds": ["required env var list", "Secret Manager map", "GitHub Secret map", "rotation checklist"],
    },
    {
        "id": "stripe_profile_manager",
        "label": "Stripe Profile Manager",
        "builds": ["default Stripe profile", "future account profiles", "secret aliases", "profile switch checklist"],
    },
    {
        "id": "secret_rotation_builder",
        "label": "Secret Rotation Builder",
        "builds": ["new secret plan", "old secret retirement plan", "dry-run validation", "rollback checklist"],
    },
]

APPROVAL_GATES = [
    "create_live_product_or_price",
    "publish_payment_link",
    "send_invoice",
    "accept_live_payment",
    "issue_refund",
    "change_payout_or_bank_settings",
    "email_customer",
    "create_github_payment_issue",
    "add_or_rotate_stripe_secret",
    "switch_active_stripe_profile",
]

REQUIRED_ENV = [
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PUBLISHABLE_KEY",
    "PAYMENT_ALERT_EMAILS",
    "PAYMENT_EMAIL_PROVIDER",
    "PAYMENT_EMAIL_FROM",
    "PAYMENT_GITHUB_NOTIFICATIONS",
    "PAYMENT_GITHUB_REPOSITORY",
]

SECRET_ALIASES = {
    "stripe_secret_key": ["STRIPE_SECRET_KEY", "STRIPE_API_KEY"],
    "stripe_publishable_key": ["STRIPE_PUBLISHABLE_KEY"],
    "stripe_webhook_secret": ["STRIPE_WEBHOOK_SECRET"],
}

PROFILE_SECRET_TEMPLATE = {
    "default": {
        "secret_key": ["STRIPE_SECRET_KEY", "STRIPE_API_KEY"],
        "publishable_key": ["STRIPE_PUBLISHABLE_KEY"],
        "webhook_secret": ["STRIPE_WEBHOOK_SECRET"],
    },
    "additional_account": {
        "secret_key": "STRIPE_SECRET_KEY_{PROFILE}",
        "publishable_key": "STRIPE_PUBLISHABLE_KEY_{PROFILE}",
        "webhook_secret": "STRIPE_WEBHOOK_SECRET_{PROFILE}",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report() -> dict:
    return {
        "schema": "dreamco.stripe_builder_bot.v1",
        "generated_at": utc_now(),
        "bot": {
            "slug": "stripe-builder-bot",
            "name": "Stripe Builder Bot",
            "division": "DreamPayments",
            "status": "sandbox_builder_ready",
            "buddy_connected": True,
            "safe_mode": True,
            "mission": "Help Buddy build, test, and prepare Stripe revenue systems without exposing secrets or taking live payment actions without approval.",
        },
        "summary": {
            "build_modules": len(BUILD_MODULES),
            "required_env_vars": len(REQUIRED_ENV),
            "approval_gates": len(APPROVAL_GATES),
            "live_money_blocked_without_approval": True,
            "secret_values_stored_in_repo": False,
            "github_notifications_supported": True,
            "email_notifications_supported": True,
            "future_stripe_profiles_supported": True,
            "secret_rotation_supported": True,
            "secret_aliases_supported": len(SECRET_ALIASES),
        },
        "build_modules": BUILD_MODULES,
        "required_environment": REQUIRED_ENV,
        "secret_aliases": SECRET_ALIASES,
        "profile_secret_template": PROFILE_SECRET_TEMPLATE,
        "approval_gates": APPROVAL_GATES,
        "future_stripe_account_workflow": [
            "Create a new Stripe account or project in Stripe.",
            "Add profile-specific GitHub Secrets or Google Secret Manager entries.",
            "Run Stripe Secret Readiness in DRY_RUN mode.",
            "Run Stripe price audit to confirm every repository price still maps to a draft offer.",
            "Run Stripe revenue rescue to confirm webhook, email, and GitHub notification readiness.",
            "Approve profile switch only after a test checkout and webhook replay pass.",
            "Keep the old profile available until subscriptions, refunds, disputes, and reports are reconciled.",
        ],
        "sandbox_test_plan": [
            "Create two draft offers with product, price, and checkout metadata.",
            "Verify no live key values are printed or stored.",
            "Run checkout session generation in test mode.",
            "Replay signed webhook fixtures for checkout, payment, invoice, subscription, refund, and payout events.",
            "Queue owner email notices without sending until provider secrets exist.",
            "Queue GitHub payment issues only when PAYMENT_GITHUB_NOTIFICATIONS is enabled.",
            "Run Stripe revenue rescue after every config change.",
            "Build a fake second Stripe profile packet and confirm no secret values are printed.",
            "Build a rotation packet and confirm live profile switching remains approval-gated.",
        ],
        "production_readiness": [
            "Stripe live keys are stored only in host secrets or Google Secret Manager.",
            "Webhook endpoint is HTTPS and verifies Stripe signatures.",
            "Payment links map directly to approved DreamCo offers.",
            "Owner receives email or GitHub notification for every successful, failed, refunded, or disputed payment.",
            "Refund, dispute, tax, and customer support paths are documented.",
            "A $1 live checkout test is approved and recorded before public launch.",
            "New Stripe account/profile secrets can be added without changing application code.",
        ],
    }


def write_markdown(report: dict) -> None:
    lines = [
        "# Stripe Builder Bot",
        "",
        report["bot"]["mission"],
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Build Modules", ""])
    for module in report["build_modules"]:
        lines.append(f"- **{module['label']}**: {', '.join(module['builds'])}")
    lines.extend(["", "## Secret Aliases", ""])
    for key, aliases in report["secret_aliases"].items():
        lines.append(f"- {key}: {', '.join(aliases)}")
    lines.extend(["", "## Future Stripe Account Workflow", ""])
    lines.extend(f"- {step}" for step in report["future_stripe_account_workflow"])
    lines.extend(["", "## Approval Gates", ""])
    lines.extend(f"- {gate}" for gate in report["approval_gates"])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Stripe Builder bot report missing; run the generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        if json.dumps(existing, indent=2, sort_keys=True) + "\n" != rendered:
            raise SystemExit("Stripe Builder bot report stale; run the generator")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        "stripe_builder_ready=True modules={modules} gates={gates}".format(
            modules=report["summary"]["build_modules"],
            gates=report["summary"]["approval_gates"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
