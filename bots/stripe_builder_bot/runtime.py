"""Sandbox-first Stripe Builder Bot.

This bot prepares Stripe configuration packets and test plans. It never stores
secret values and never performs live payment actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


APPROVAL_GATES = {
    "create_live_product_or_price",
    "publish_payment_link",
    "send_invoice",
    "accept_live_payment",
    "issue_refund",
    "change_payout_or_bank_settings",
    "email_customer",
    "create_github_payment_issue",
}


@dataclass
class StripeBuilderBot:
    """Builds safe Stripe setup packets for Buddy and DreamCo."""

    safe_mode: bool = True
    prepared_packets: list[dict[str, Any]] = field(default_factory=list)

    def build_offer_packet(self, offer_id: str, name: str, price_cents: int, billing_mode: str) -> dict[str, Any]:
        if price_cents <= 0:
            raise ValueError("price_cents must be positive")
        if billing_mode not in {"one_time", "subscription"}:
            raise ValueError("billing_mode must be one_time or subscription")
        packet = {
            "offer_id": offer_id,
            "name": name,
            "price_cents": price_cents,
            "billing_mode": billing_mode,
            "status": "draft_ready_for_stripe_test_mode",
            "live_action": False,
            "approval_required_before": sorted(APPROVAL_GATES),
            "builds": [
                "product draft",
                "price draft",
                "checkout settings",
                "webhook event plan",
                "payment notification plan",
                "test-mode validation checklist",
            ],
        }
        self.prepared_packets.append(packet)
        return packet

    def build_webhook_packet(self, endpoint_url: str) -> dict[str, Any]:
        if not endpoint_url.startswith("https://"):
            raise ValueError("Stripe webhook endpoint must be HTTPS before production")
        return {
            "endpoint_url": endpoint_url,
            "status": "webhook_plan_ready",
            "live_action": False,
            "events": [
                "checkout.session.completed",
                "payment_intent.succeeded",
                "payment_intent.payment_failed",
                "invoice.paid",
                "invoice.payment_failed",
                "customer.subscription.updated",
                "charge.refunded",
                "payout.paid",
            ],
            "requirements": [
                "verify Stripe signature",
                "store event idempotently",
                "queue owner notification",
                "never print webhook secret",
                "retry failed processing safely",
            ],
            "approval_required_before": sorted(APPROVAL_GATES),
        }

    def readiness(self) -> dict[str, Any]:
        return {
            "bot": "Stripe Builder Bot",
            "safe_mode": self.safe_mode,
            "prepared_packets": len(self.prepared_packets),
            "live_money_blocked_without_approval": True,
            "secret_values_stored": False,
            "approval_gates": sorted(APPROVAL_GATES),
        }
