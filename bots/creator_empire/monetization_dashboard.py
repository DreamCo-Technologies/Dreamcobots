"""
Monetization Dashboard for CreatorEmpire.

Tracks revenue streams, service fees, subscriptions, and payment
integration for talent managed through the DreamCo platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class MonetizationError(Exception):
    """Raised when a monetization operation fails."""


# ---------------------------------------------------------------------------
# Subscription / service fee tiers
# ---------------------------------------------------------------------------

@dataclass
class ServicePlan:
    """A monetization service plan offered to talent."""
    plan_id: str
    name: str
    monthly_fee_usd: float
    transaction_fee_pct: float   # % taken from each transaction
    features: list[str] = field(default_factory=list)
    max_active_streams: Optional[int] = None   # None = unlimited

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "monthly_fee_usd": self.monthly_fee_usd,
            "transaction_fee_pct": self.transaction_fee_pct,
            "features": self.features,
            "max_active_streams": self.max_active_streams if self.max_active_streams else "unlimited",
        }


SERVICE_PLANS: dict[str, ServicePlan] = {
    "starter": ServicePlan(
        plan_id="starter",
        name="Starter",
        monthly_fee_usd=0.0,
        transaction_fee_pct=10.0,
        features=["Basic revenue tracking", "Up to 1 payment processor"],
        max_active_streams=1,
    ),
    "creator": ServicePlan(
        plan_id="creator",
        name="Creator",
        monthly_fee_usd=29.0,
        transaction_fee_pct=5.0,
        features=[
            "Revenue tracking & analytics",
            "Up to 3 payment processors",
            "Auto royalty distribution",
            "Monthly payout reports",
        ],
        max_active_streams=5,
    ),
    "pro": ServicePlan(
        plan_id="pro",
        name="Pro",
        monthly_fee_usd=79.0,
        transaction_fee_pct=2.5,
        features=[
            "Advanced revenue tracking & analytics",
            "Unlimited payment processors",
            "Auto royalty distribution",
            "Weekly payout reports",
            "Stripe & PayPal integration",
            "Priority support",
        ],
        max_active_streams=None,
    ),
    "enterprise": ServicePlan(
        plan_id="enterprise",
        name="Enterprise",
        monthly_fee_usd=299.0,
        transaction_fee_pct=1.0,
        features=[
            "White-glove revenue management",
            "Custom payout schedules",
            "Dedicated account manager",
            "Custom integrations",
            "White-label dashboard",
            "SLA guarantee",
        ],
        max_active_streams=None,
    ),
}

PAYMENT_PROVIDERS = ["stripe", "paypal", "venmo_business", "cashapp_business"]


@dataclass
class RevenueEntry:
    """A single revenue transaction."""
    entry_id: str
    talent_id: str
    source: str          # e.g. "streaming_royalties", "sponsorship", "event", "merchandise"
    gross_amount_usd: float
    platform_fee_pct: float
    description: str = ""

    def net_amount(self) -> float:
        return round(self.gross_amount_usd * (1 - self.platform_fee_pct / 100), 4)

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "talent_id": self.talent_id,
            "source": self.source,
            "gross_amount_usd": self.gross_amount_usd,
            "platform_fee_pct": self.platform_fee_pct,
            "net_amount_usd": self.net_amount(),
            "description": self.description,
        }


@dataclass
class TalentMonetizationAccount:
    """Tracks the monetization state for a single talent."""
    talent_id: str
    service_plan_id: str = "starter"
    connected_processors: list[str] = field(default_factory=list)
    revenue_entries: list[RevenueEntry] = field(default_factory=list)

    def total_gross(self) -> float:
        return round(sum(e.gross_amount_usd for e in self.revenue_entries), 4)

    def total_net(self) -> float:
        return round(sum(e.net_amount() for e in self.revenue_entries), 4)

    def to_dict(self) -> dict:
        return {
            "talent_id": self.talent_id,
            "service_plan_id": self.service_plan_id,
            "connected_processors": self.connected_processors,
            "total_gross_usd": self.total_gross(),
            "total_net_usd": self.total_net(),
            "entry_count": len(self.revenue_entries),
        }


class MonetizationDashboard:
    """
    Tracks revenue, manages service plans, and handles payment processor
    connections for talent on the CreatorEmpire platform.

    Parameters
    ----------
    tier : Tier
        Controls which service plans and payment features are accessible.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._accounts: dict[str, TalentMonetizationAccount] = {}

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def register_talent(self, talent_id: str, service_plan_id: str = "starter") -> TalentMonetizationAccount:
        """Register a talent with a service plan."""
        if talent_id in self._accounts:
            raise MonetizationError(f"Talent '{talent_id}' is already registered.")
        if service_plan_id not in SERVICE_PLANS:
            raise MonetizationError(
                f"Service plan '{service_plan_id}' not found. "
                f"Available: {', '.join(SERVICE_PLANS)}."
            )
        self._require_tier_for_plan(service_plan_id)
        account = TalentMonetizationAccount(
            talent_id=talent_id,
            service_plan_id=service_plan_id,
        )
        self._accounts[talent_id] = account
        return account

    def upgrade_plan(self, talent_id: str, new_plan_id: str) -> TalentMonetizationAccount:
        """Upgrade a talent's service plan."""
        account = self._get_account(talent_id)
        if new_plan_id not in SERVICE_PLANS:
            raise MonetizationError(f"Service plan '{new_plan_id}' not found.")
        self._require_tier_for_plan(new_plan_id)
        account.service_plan_id = new_plan_id
        return account

    # ------------------------------------------------------------------
    # Payment processors
    # ------------------------------------------------------------------

    def connect_payment_processor(self, talent_id: str, processor: str) -> dict:
        """
        Connect a payment processor to a talent account.

        PRO/ENTERPRISE plans allow unlimited processors;
        Starter allows 1, Creator allows 3.
        """
        account = self._get_account(talent_id)
        plan = SERVICE_PLANS[account.service_plan_id]

        if processor.lower() not in PAYMENT_PROVIDERS:
            raise MonetizationError(
                f"Payment provider '{processor}' not supported. "
                f"Supported: {', '.join(PAYMENT_PROVIDERS)}."
            )

        max_proc = plan.max_active_streams  # re-used field for processor limit
        if max_proc is not None and len(account.connected_processors) >= max_proc:
            raise MonetizationError(
                f"Your '{plan.name}' plan allows a maximum of {max_proc} "
                "connected payment processor(s). Upgrade to add more."
            )

        if processor.lower() in account.connected_processors:
            raise MonetizationError(f"'{processor}' is already connected.")

        account.connected_processors.append(processor.lower())
        return {"talent_id": talent_id, "processor": processor.lower(), "status": "connected"}

    # ------------------------------------------------------------------
    # Revenue tracking
    # ------------------------------------------------------------------

    def log_revenue(
        self,
        talent_id: str,
        entry_id: str,
        source: str,
        gross_amount_usd: float,
        description: str = "",
    ) -> RevenueEntry:
        """Log a revenue transaction for a talent."""
        account = self._get_account(talent_id)
        plan = SERVICE_PLANS[account.service_plan_id]

        if any(e.entry_id == entry_id for e in account.revenue_entries):
            raise MonetizationError(f"Entry ID '{entry_id}' already exists for talent '{talent_id}'.")

        entry = RevenueEntry(
            entry_id=entry_id,
            talent_id=talent_id,
            source=source,
            gross_amount_usd=gross_amount_usd,
            platform_fee_pct=plan.transaction_fee_pct,
            description=description,
        )
        account.revenue_entries.append(entry)
        return entry

    def get_revenue_report(self, talent_id: str) -> dict:
        """Return a revenue report for a talent."""
        account = self._get_account(talent_id)
        by_source: dict[str, float] = {}
        for e in account.revenue_entries:
            by_source[e.source] = round(by_source.get(e.source, 0) + e.net_amount(), 4)
        return {
            "talent_id": talent_id,
            "service_plan": account.service_plan_id,
            "total_gross_usd": account.total_gross(),
            "total_net_usd": account.total_net(),
            "breakdown_by_source": by_source,
            "entry_count": len(account.revenue_entries),
        }

    def get_account(self, talent_id: str) -> dict:
        return self._get_account(talent_id).to_dict()

    # ------------------------------------------------------------------
    # Plan catalogue
    # ------------------------------------------------------------------

    @staticmethod
    def list_service_plans() -> list[dict]:
        """Return all available service plans."""
        return [plan.to_dict() for plan in SERVICE_PLANS.values()]

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        total_gross = sum(a.total_gross() for a in self._accounts.values())
        total_net = sum(a.total_net() for a in self._accounts.values())
        return {
            "tier": self.tier.value,
            "registered_talents": len(self._accounts),
            "total_gross_revenue_usd": round(total_gross, 4),
            "total_net_revenue_usd": round(total_net, 4),
            "available_payment_providers": PAYMENT_PROVIDERS,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_account(self, talent_id: str) -> TalentMonetizationAccount:
        if talent_id not in self._accounts:
            raise MonetizationError(f"Talent '{talent_id}' is not registered.")
        return self._accounts[talent_id]

    def _require_tier_for_plan(self, plan_id: str) -> None:
        """Enforce that advanced plans require higher platform tiers."""
        if plan_id in ("pro", "enterprise") and self.tier == Tier.FREE:
            raise MonetizationError(
                f"The '{plan_id}' service plan requires the Pro platform tier or higher."
            )
        if plan_id == "enterprise" and self.tier == Tier.PRO:
            raise MonetizationError(
                "The 'enterprise' service plan requires the Enterprise platform tier."
            )
