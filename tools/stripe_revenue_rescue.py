#!/usr/bin/env python3
"""Diagnose why connected Stripe setup is not producing tracked revenue."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFERS_FILE = ROOT / "data/stripe/offers.template.json"
EVENTS_FILE = ROOT / "data/stripe/events.json"
SUMMARY_FILE = ROOT / "data/stripe/summary.json"
PAYMENT_EMAIL_OUTBOX_FILE = ROOT / "data/stripe/payment-email-outbox.json"
MONETIZATION_LINKS_FILE = ROOT / "src/components/MonetizationLinks.jsx"
REPORT_JSON = ROOT / "reports/stripe_revenue_rescue_report.json"
REPORT_MD = ROOT / "reports/STRIPE_REVENUE_RESCUE_REPORT.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def secret_state(name: str) -> dict[str, Any]:
    value = os.environ.get(name, "")
    state = {
        "name": name,
        "configured": bool(value),
        "mode": "missing",
    }
    if value.startswith(("sk_live_", "pk_live_", "whsec_")):
        state["mode"] = "live_or_webhook_secret"
    elif value.startswith(("sk_test_", "pk_test_")):
        state["mode"] = "test"
    elif value:
        state["mode"] = "present_unknown_prefix"
    return state


def check_offers() -> tuple[list[dict[str, Any]], list[str]]:
    data = read_json(OFFERS_FILE, {"offers": []})
    offers = data.get("offers", [])
    issues: list[str] = []
    normalized: list[dict[str, Any]] = []

    for offer in offers:
        has_price = bool(offer.get("stripePriceId"))
        has_payment_link = bool(offer.get("stripePaymentLinkId"))
        is_live = str(offer.get("status", "")).lower() in {"live", "active", "published"}
        ready = has_price and has_payment_link and is_live
        normalized.append(
            {
                "offerId": offer.get("offerId"),
                "name": offer.get("name"),
                "status": offer.get("status"),
                "priceCents": offer.get("priceCents"),
                "hasStripePriceId": has_price,
                "hasStripePaymentLinkId": has_payment_link,
                "checkoutReady": ready,
            }
        )
        if not is_live:
            issues.append(f"{offer.get('offerId')} is not live/published")
        if not has_price:
            issues.append(f"{offer.get('offerId')} is missing stripePriceId")
        if not has_payment_link:
            issues.append(f"{offer.get('offerId')} is missing stripePaymentLinkId")

    if not offers:
        issues.append("No Stripe offers found in data/stripe/offers.template.json")

    return normalized, issues


def check_events() -> dict[str, Any]:
    events = read_json(EVENTS_FILE, [])
    summary = read_json(SUMMARY_FILE, {})
    return {
        "eventsFileExists": EVENTS_FILE.exists(),
        "summaryFileExists": SUMMARY_FILE.exists(),
        "trackedEvents": len(events) if isinstance(events, list) else 0,
        "grossRevenueCents": summary.get("grossRevenueCents", 0),
        "checkoutCompleted": summary.get("checkoutCompleted", 0),
        "paymentSucceeded": summary.get("paymentSucceeded", 0),
        "invoicePaid": summary.get("invoicePaid", 0),
        "paymentFailed": summary.get("paymentFailed", 0),
        "invoiceFailed": summary.get("invoiceFailed", 0),
    }


def check_payment_email_notifications() -> dict[str, Any]:
    outbox = read_json(PAYMENT_EMAIL_OUTBOX_FILE, [])
    if not isinstance(outbox, list):
        outbox = []
    recipients = os.environ.get("STRIPE_PAYMENT_ALERT_EMAILS") or os.environ.get("PAYMENT_ALERT_EMAILS") or ""
    recipient_count = len([item.strip() for item in recipients.split(",") if item.strip()])
    provider = os.environ.get("PAYMENT_EMAIL_PROVIDER") or ("resend" if os.environ.get("RESEND_API_KEY") else "missing")
    sent = sum(1 for item in outbox if item.get("status") == "sent")
    blocked = sum(1 for item in outbox if str(item.get("status", "")).startswith("blocked"))
    queued = sum(1 for item in outbox if str(item.get("status", "")).startswith("queued"))
    github_created = sum(1 for item in outbox if item.get("githubStatus") == "github_issue_created")
    github_enabled = str(os.environ.get("PAYMENT_GITHUB_NOTIFICATIONS", "")).lower() in {"1", "true", "yes"}
    github_repo = os.environ.get("PAYMENT_GITHUB_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY") or ""
    github_token_configured = bool(os.environ.get("PAYMENT_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    return {
        "outboxFileExists": PAYMENT_EMAIL_OUTBOX_FILE.exists(),
        "outboxNotices": len(outbox),
        "sentNotices": sent,
        "queuedNotices": queued,
        "blockedNotices": blocked,
        "recipientCount": recipient_count,
        "provider": provider,
        "resendConfigured": bool(os.environ.get("RESEND_API_KEY")),
        "fromConfigured": bool(os.environ.get("PAYMENT_EMAIL_FROM")),
        "githubNotificationsEnabled": github_enabled,
        "githubRepositoryConfigured": bool(github_repo),
        "githubTokenConfigured": github_token_configured,
        "githubIssuesCreated": github_created,
    }


def check_customer_links() -> dict[str, Any]:
    content = MONETIZATION_LINKS_FILE.read_text(encoding="utf-8") if MONETIZATION_LINKS_FILE.exists() else ""
    default_match = re.search(r"https://[^'\"`]+", content)
    uses_template_checkout = "/checkout?" in content
    return {
        "file": str(MONETIZATION_LINKS_FILE.relative_to(ROOT)),
        "exists": MONETIZATION_LINKS_FILE.exists(),
        "defaultPaymentBase": default_match.group(0) if default_match else None,
        "usesTemplateCheckoutRoute": uses_template_checkout,
        "hasDirectPaymentLinkMapping": "stripePaymentLink" in content or "payment_links" in content,
        "risk": "high" if uses_template_checkout else "unknown",
        "message": "Customer buttons appear to build a generic checkout URL, not verified live Stripe Payment Links.",
    }


def build_report() -> dict[str, Any]:
    offers, offer_issues = check_offers()
    events = check_events()
    email_notifications = check_payment_email_notifications()
    link_check = check_customer_links()
    secrets = [
        secret_state("STRIPE_SECRET_KEY"),
        secret_state("STRIPE_WEBHOOK_SECRET"),
        secret_state("STRIPE_PUBLISHABLE_KEY"),
        secret_state("REACT_APP_DREAMCO_PAYMENT_URL"),
        secret_state("VITE_DREAMCO_PAYMENT_URL"),
    ]

    checkout_ready_offers = sum(1 for offer in offers if offer["checkoutReady"])
    tracked_revenue = events["grossRevenueCents"]
    revenue_blockers = []
    if checkout_ready_offers == 0:
        revenue_blockers.append("No checkout-ready live Stripe offers with price and payment link IDs.")
    if events["trackedEvents"] == 0:
        revenue_blockers.append("No Stripe webhook events are recorded locally.")
    if tracked_revenue == 0:
        revenue_blockers.append("No successful payment or paid invoice revenue is tracked.")
    if link_check["usesTemplateCheckoutRoute"] and not link_check["hasDirectPaymentLinkMapping"]:
        revenue_blockers.append("Customer CTA buttons are not mapped to verified live Stripe Payment Links.")
    if not any(item["name"] == "STRIPE_SECRET_KEY" and item["configured"] for item in secrets):
        revenue_blockers.append("STRIPE_SECRET_KEY is not configured in this runtime.")
    if not any(item["name"] == "STRIPE_WEBHOOK_SECRET" and item["configured"] for item in secrets):
        revenue_blockers.append("STRIPE_WEBHOOK_SECRET is not configured in this runtime.")
    if email_notifications["recipientCount"] == 0:
        revenue_blockers.append("Payment alert email recipients are not configured.")
    if email_notifications["provider"] == "missing":
        revenue_blockers.append("Payment email provider is not configured.")
    if not email_notifications["githubNotificationsEnabled"]:
        revenue_blockers.append("GitHub payment notifications are not enabled.")
    elif not email_notifications["githubRepositoryConfigured"]:
        revenue_blockers.append("GitHub payment notification repository is not configured.")
    elif not email_notifications["githubTokenConfigured"]:
        revenue_blockers.append("GitHub payment notification token is not configured.")

    priority_fixes = [
        "Set STRIPE_PAYMENT_ALERT_EMAILS or PAYMENT_ALERT_EMAILS to the owner email list that should receive every payment notice.",
        "Configure PAYMENT_EMAIL_PROVIDER=resend plus RESEND_API_KEY and PAYMENT_EMAIL_FROM, or connect another production email provider.",
        "For GitHub payment alerts, set PAYMENT_GITHUB_NOTIFICATIONS=true, PAYMENT_GITHUB_REPOSITORY=DreamCo-Technologies/Dreamcobots, and PAYMENT_GITHUB_TOKEN or GITHUB_TOKEN with issue-write access.",
        "Create or confirm two live Stripe Payment Links for the starter audit and monthly command center offers.",
        "Put the live Stripe price/payment link IDs in a private production offer catalog or environment-backed config.",
        "Update customer-facing CTA buttons to use verified live Stripe Payment Links, not generic placeholder checkout routes.",
        "Deploy the webhook endpoint over HTTPS and subscribe it to checkout, payment, invoice, subscription, and payout events.",
        "Send one $1 live-mode internal checkout test, then confirm the rescue report shows checkoutCompleted > 0 and grossRevenueCents > 0.",
        "Review the Stripe Dashboard for failed payments, disabled payouts, test-mode products, and broken success/cancel URLs.",
    ]

    return {
        "schema": "dreamco.stripe_revenue_rescue.v1",
        "generated_at": utc_now(),
        "summary": {
            "revenue_rescue_ready": len(revenue_blockers) == 0,
            "checkout_ready_offers": checkout_ready_offers,
            "offers_checked": len(offers),
            "tracked_events": events["trackedEvents"],
            "gross_revenue_cents": tracked_revenue,
            "checkout_completed": events["checkoutCompleted"],
            "payment_succeeded": events["paymentSucceeded"],
            "invoice_paid": events["invoicePaid"],
            "payment_email_recipients": email_notifications["recipientCount"],
            "payment_email_notices": email_notifications["outboxNotices"],
            "payment_email_sent": email_notifications["sentNotices"],
            "github_payment_notifications_enabled": email_notifications["githubNotificationsEnabled"],
            "github_payment_issues_created": email_notifications["githubIssuesCreated"],
            "blocker_count": len(revenue_blockers),
        },
        "revenue_blockers": revenue_blockers,
        "priority_fixes": priority_fixes,
        "offers": offers,
        "offer_issues": offer_issues,
        "events": events,
        "payment_email_notifications": email_notifications,
        "customer_links": link_check,
        "runtime_secret_state": secrets,
        "safety_note": "This report never prints secret values. Configure Stripe keys only in environment variables or a secure host secret store.",
    }


def write_reports(report: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Stripe Revenue Rescue Report",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Rescue ready: {report['summary']['revenue_rescue_ready']}",
        f"- Checkout-ready offers: {report['summary']['checkout_ready_offers']}/{report['summary']['offers_checked']}",
        f"- Tracked Stripe events: {report['summary']['tracked_events']}",
        f"- Gross tracked revenue: ${report['summary']['gross_revenue_cents'] / 100:.2f}",
            f"- Payment email recipients configured: {report['summary']['payment_email_recipients']}",
            f"- Payment email notices tracked: {report['summary']['payment_email_notices']}",
            f"- GitHub payment notifications enabled: {report['summary']['github_payment_notifications_enabled']}",
            f"- GitHub payment issues created: {report['summary']['github_payment_issues_created']}",
            f"- Blockers: {report['summary']['blocker_count']}",
        "",
        "## Revenue Blockers",
        "",
    ]
    if report["revenue_blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["revenue_blockers"])
    else:
        lines.append("- No blockers found by the local rescue scan.")
    lines.extend(["", "## Priority Fixes", ""])
    lines.extend(f"{index}. {fix}" for index, fix in enumerate(report["priority_fixes"], start=1))
    lines.extend(["", "## Offer Readiness", ""])
    for offer in report["offers"]:
        lines.append(
            "- `{offerId}`: status={status}, price_id={price}, payment_link={link}, ready={ready}".format(
                offerId=offer["offerId"],
                status=offer["status"],
                price=offer["hasStripePriceId"],
                link=offer["hasStripePaymentLinkId"],
                ready=offer["checkoutReady"],
            )
        )
    lines.extend(["", "## Payment Email Notifications", ""])
    email = report["payment_email_notifications"]
    lines.extend(
        [
            f"- Provider: {email['provider']}",
            f"- Recipients configured: {email['recipientCount']}",
            f"- Outbox notices: {email['outboxNotices']}",
            f"- Sent notices: {email['sentNotices']}",
            f"- Queued notices: {email['queuedNotices']}",
            f"- Blocked notices: {email['blockedNotices']}",
            f"- GitHub notifications enabled: {email['githubNotificationsEnabled']}",
            f"- GitHub repository configured: {email['githubRepositoryConfigured']}",
            f"- GitHub token configured: {email['githubTokenConfigured']}",
            f"- GitHub issues created: {email['githubIssuesCreated']}",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_reports(report)
    print(
        "revenue_rescue_ready={ready} blockers={blockers} checkout_ready_offers={offers} tracked_events={events} payment_email_recipients={recipients} github_notifications={github} gross=${gross:.2f}".format(
            ready=report["summary"]["revenue_rescue_ready"],
            blockers=report["summary"]["blocker_count"],
            offers=report["summary"]["checkout_ready_offers"],
            events=report["summary"]["tracked_events"],
            recipients=report["summary"]["payment_email_recipients"],
            github=report["summary"]["github_payment_notifications_enabled"],
            gross=report["summary"]["gross_revenue_cents"] / 100,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
