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
    "add_or_rotate_stripe_secret",
    "switch_active_stripe_profile",
}

SECRET_ALIASES = {
    "secret_key": ["STRIPE_SECRET_KEY", "STRIPE_API_KEY"],
    "publishable_key": ["STRIPE_PUBLISHABLE_KEY"],
    "webhook_secret": ["STRIPE_WEBHOOK_SECRET"],
}

PROFILE_SUFFIX_FIELDS = {
    "secret_key": "STRIPE_SECRET_KEY_{suffix}",
    "publishable_key": "STRIPE_PUBLISHABLE_KEY_{suffix}",
    "webhook_secret": "STRIPE_WEBHOOK_SECRET_{suffix}",
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

    @staticmethod
    def _profile_suffix(profile_name: str) -> str:
        suffix = "".join(ch if ch.isalnum() else "_" for ch in profile_name.upper()).strip("_")
        return suffix or "DEFAULT"

    def build_secret_profile_packet(self, profile_name: str = "default") -> dict[str, Any]:
        suffix = self._profile_suffix(profile_name)
        profile_secrets = {
            key: template.format(suffix=suffix)
            for key, template in PROFILE_SUFFIX_FIELDS.items()
        }
        packet = {
            "profile": profile_name,
            "suffix": suffix,
            "status": "secret_profile_ready",
            "live_action": False,
            "secret_values_included": False,
            "default_secret_aliases": SECRET_ALIASES,
            "profile_secret_names": profile_secrets,
            "github_actions_behavior": [
                "Use STRIPE_SECRET_KEY or STRIPE_API_KEY for the default account.",
                "Use profile-specific names when a second Stripe account is added.",
                "Never print secret values; report configured/missing only.",
            ],
            "approval_required_before": sorted(APPROVAL_GATES),
        }
        self.prepared_packets.append(packet)
        return packet

    def build_secret_rotation_plan(self, old_profile: str, new_profile: str) -> dict[str, Any]:
        old_packet = self.build_secret_profile_packet(old_profile)
        new_packet = self.build_secret_profile_packet(new_profile)
        return {
            "status": "stripe_secret_rotation_plan_ready",
            "live_action": False,
            "secret_values_included": False,
            "old_profile": old_packet["profile_secret_names"],
            "new_profile": new_packet["profile_secret_names"],
            "steps": [
                "Add the new Stripe secret names in GitHub Secrets or Google Secret Manager.",
                "Run Stripe Secret Readiness in DRY_RUN mode.",
                "Run Stripe price audit and revenue rescue reports.",
                "Create test-mode product, price, payment link, and webhook checks.",
                "Approve profile switch only after test checkout and webhook verification pass.",
                "Keep old Stripe secrets until refunds, disputes, subscriptions, and reporting are reconciled.",
                "Remove old secrets only after owner approval and a final revenue export.",
            ],
            "approval_required_before": sorted(APPROVAL_GATES),
        }

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
            "secret_aliases": SECRET_ALIASES,
            "approval_gates": sorted(APPROVAL_GATES),
        }
