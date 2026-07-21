"""
Home Buyer Bot — tier-aware real-estate lead generation and payment bot for Chicago.

Focuses on Buy / Rent / Off-Market deals in the Chicago metro area.
Integrates with Stripe/PayPal mock gateways, logs every interaction and purchase,
and serves as DreamCo's first revenue-generating proof-of-concept bot.
"""

from __future__ import annotations

import os
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: E402
from bots.home_buyer_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: E402
from framework import GlobalAISourcesFlow  # noqa: F401, E402


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("home_buyer_bot")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Enums and constants
# ---------------------------------------------------------------------------


class DealType(Enum):
    BUY = "buy"
    RENT = "rent"
    OFF_MARKET = "off_market"


class PaymentProvider(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"


class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class HomeBuyerBotError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Mock property database for Chicago
# ---------------------------------------------------------------------------

CHICAGO_LISTINGS: Dict[str, List[dict]] = {
    "buy": [
        {
            "id": "chi-buy-001",
            "address": "2401 N Lincoln Ave, Chicago IL",
            "price": 425000,
            "beds": 3,
            "baths": 2,
            "sqft": 1750,
            "type": "single_family",
            "neighborhood": "Lincoln Park",
        },
        {
            "id": "chi-buy-002",
            "address": "1122 W Belmont Ave #5B, Chicago IL",
            "price": 285000,
            "beds": 2,
            "baths": 1,
            "sqft": 980,
            "type": "condo",
            "neighborhood": "Lakeview",
        },
        {
            "id": "chi-buy-003",
            "address": "3544 S King Dr, Chicago IL",
            "price": 195000,
            "beds": 3,
            "baths": 1,
            "sqft": 1300,
            "type": "single_family",
            "neighborhood": "Bronzeville",
        },
        {
            "id": "chi-buy-004",
            "address": "5020 N Sheridan Rd #12A, Chicago IL",
            "price": 220000,
            "beds": 1,
            "baths": 1,
            "sqft": 750,
            "type": "condo",
            "neighborhood": "Edgewater",
        },
        {
            "id": "chi-buy-005",
            "address": "1801 W Division St, Chicago IL",
            "price": 550000,
            "beds": 4,
            "baths": 3,
            "sqft": 2200,
            "type": "townhouse",
            "neighborhood": "Wicker Park",
        },
    ],
    "rent": [
        {
            "id": "chi-rent-001",
            "address": "800 N Michigan Ave #2203, Chicago IL",
            "monthly_rent": 3200,
            "beds": 2,
            "baths": 2,
            "sqft": 1100,
            "type": "condo",
            "neighborhood": "Magnificent Mile",
        },
        {
            "id": "chi-rent-002",
            "address": "2200 W Chicago Ave #3F, Chicago IL",
            "monthly_rent": 1600,
            "beds": 1,
            "baths": 1,
            "sqft": 700,
            "type": "apartment",
            "neighborhood": "Ukrainian Village",
        },
        {
            "id": "chi-rent-003",
            "address": "4501 N Racine Ave, Chicago IL",
            "monthly_rent": 2100,
            "beds": 3,
            "baths": 2,
            "sqft": 1400,
            "type": "single_family",
            "neighborhood": "Uptown",
        },
    ],
    "off_market": [
        {
            "id": "chi-off-001",
            "address": "6120 S Cottage Grove, Chicago IL",
            "asking_price": 155000,
            "arv": 240000,
            "beds": 3,
            "baths": 1,
            "sqft": 1250,
            "type": "single_family",
            "neighborhood": "Woodlawn",
            "discount_pct": 35,
        },
        {
            "id": "chi-off-002",
            "address": "1444 W 69th St, Chicago IL",
            "asking_price": 98000,
            "arv": 180000,
            "beds": 3,
            "baths": 2,
            "sqft": 1150,
            "type": "single_family",
            "neighborhood": "Englewood",
            "discount_pct": 45,
        },
    ],
}

# Service fee schedule
SERVICE_FEES: Dict[str, float] = {
    Tier.FREE.value: 199.0,
    Tier.PRO.value: 99.0,
    Tier.ENTERPRISE.value: 49.0,
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Lead:
    lead_id: str
    name: str
    email: str
    phone: str
    deal_type: DealType
    budget: float
    neighborhoods: List[str]
    status: LeadStatus = LeadStatus.NEW
    notes: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "lead_id": self.lead_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "deal_type": self.deal_type.value,
            "budget": self.budget,
            "neighborhoods": self.neighborhoods,
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at,
        }


@dataclass
class Payment:
    payment_id: str
    lead_id: str
    amount: float
    provider: PaymentProvider
    status: str  # "pending", "completed", "failed", "refunded"
    description: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "lead_id": self.lead_id,
            "amount": self.amount,
            "provider": self.provider.value,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# HomeBuyerBot
# ---------------------------------------------------------------------------


class HomeBuyerBot:
    """Chicago-focused lead generation + payment bot for Buy/Rent/Off-Market deals."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._leads: Dict[str, Lead] = {}
        self._payments: Dict[str, Payment] = {}
        self._interaction_log: List[dict] = []
        logger.info("HomeBuyerBot initialized [tier=%s]", tier.value)

    # ------------------------------------------------------------------
    # Feature gating
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        features = BOT_FEATURES.get(self.tier.value, [])
        if feature not in features:
            upgrade = get_upgrade_path(self.tier)
            raise HomeBuyerBotError(
                f"Feature '{feature}' requires a higher tier. "
                f"Upgrade to {upgrade} to unlock it."
            )

    # ------------------------------------------------------------------
    # Lead management
    # ------------------------------------------------------------------

    def submit_lead(
        self,
        name: str,
        email: str,
        phone: str,
        deal_type: DealType,
        budget: float,
        neighborhoods: Optional[List[str]] = None,
    ) -> dict:
        """Capture a new buyer/renter lead."""
        lead = Lead(
            lead_id=f"lead-{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            phone=phone,
            deal_type=deal_type,
            budget=budget,
            neighborhoods=neighborhoods or ["Chicago"],
        )
        self._leads[lead.lead_id] = lead
        self._log("lead_submitted", lead.to_dict())
        logger.info("Lead submitted: %s (%s)", lead.lead_id, deal_type.value)
        return lead.to_dict()

    def get_lead(self, lead_id: str) -> dict:
        lead = self._leads.get(lead_id)
        if lead is None:
            raise HomeBuyerBotError(f"Lead '{lead_id}' not found.")
        return lead.to_dict()

    def update_lead_status(self, lead_id: str, status: LeadStatus, notes: str = "") -> dict:
        lead = self._leads.get(lead_id)
        if lead is None:
            raise HomeBuyerBotError(f"Lead '{lead_id}' not found.")
        lead.status = status
        if notes:
            lead.notes = notes
        self._log("lead_status_updated", {"lead_id": lead_id, "status": status.value})
        return lead.to_dict()

    def list_leads(self, status: Optional[LeadStatus] = None) -> List[dict]:
        leads = list(self._leads.values())
        if status:
            leads = [l for l in leads if l.status == status]
        return [l.to_dict() for l in leads]

    # ------------------------------------------------------------------
    # Property search
    # ------------------------------------------------------------------

    def search_listings(
        self,
        deal_type: DealType,
        max_price: Optional[float] = None,
        neighborhood: Optional[str] = None,
    ) -> List[dict]:
        """Return matching Chicago listings for the requested deal type."""
        listings = list(CHICAGO_LISTINGS.get(deal_type.value, []))

        if deal_type == DealType.BUY and max_price is not None:
            listings = [p for p in listings if p.get("price", 0) <= max_price]
        elif deal_type == DealType.RENT and max_price is not None:
            listings = [p for p in listings if p.get("monthly_rent", 0) <= max_price]
        elif deal_type == DealType.OFF_MARKET and max_price is not None:
            listings = [p for p in listings if p.get("asking_price", 0) <= max_price]

        if neighborhood:
            neighborhood_lower = neighborhood.lower()
            listings = [
                p
                for p in listings
                if neighborhood_lower in p.get("neighborhood", "").lower()
            ]

        self._log(
            "listings_searched",
            {"deal_type": deal_type.value, "results": len(listings)},
        )
        return listings

    def get_off_market_deals(self) -> List[dict]:
        """Return off-market deals (PRO/ENTERPRISE only)."""
        self._require("off_market_deals")
        return self.search_listings(DealType.OFF_MARKET)

    # ------------------------------------------------------------------
    # Payment processing
    # ------------------------------------------------------------------

    def process_payment(
        self,
        lead_id: str,
        provider: PaymentProvider = PaymentProvider.STRIPE,
        description: str = "Buyer consultation fee",
    ) -> dict:
        """Process a service-fee payment for the given lead (mock gateway)."""
        if lead_id not in self._leads:
            raise HomeBuyerBotError(f"Lead '{lead_id}' not found.")
        amount = SERVICE_FEES[self.tier.value]
        payment = Payment(
            payment_id=f"pay-{uuid.uuid4().hex[:8]}",
            lead_id=lead_id,
            amount=amount,
            provider=provider,
            status="completed",  # mock: always succeeds
            description=description,
        )
        self._payments[payment.payment_id] = payment
        self._log("payment_processed", payment.to_dict())
        logger.info(
            "Payment processed: %s | $%.2f via %s",
            payment.payment_id,
            amount,
            provider.value,
        )
        return payment.to_dict()

    def refund_payment(self, payment_id: str) -> dict:
        """Issue a refund for a completed payment."""
        payment = self._payments.get(payment_id)
        if payment is None:
            raise HomeBuyerBotError(f"Payment '{payment_id}' not found.")
        if payment.status != "completed":
            raise HomeBuyerBotError(
                f"Cannot refund payment with status '{payment.status}'."
            )
        payment.status = "refunded"
        self._log("payment_refunded", {"payment_id": payment_id})
        return payment.to_dict()

    def get_payment(self, payment_id: str) -> dict:
        payment = self._payments.get(payment_id)
        if payment is None:
            raise HomeBuyerBotError(f"Payment '{payment_id}' not found.")
        return payment.to_dict()

    # ------------------------------------------------------------------
    # Revenue summary
    # ------------------------------------------------------------------

    def revenue_summary(self) -> dict:
        """Return total revenue collected via completed payments."""
        completed = [
            p for p in self._payments.values() if p.status == "completed"
        ]
        total = sum(p.amount for p in completed)
        return {
            "total_payments": len(self._payments),
            "completed_payments": len(completed),
            "total_revenue_usd": round(total, 2),
            "service_fee_usd": SERVICE_FEES[self.tier.value],
        }

    # ------------------------------------------------------------------
    # Interaction log / analytics
    # ------------------------------------------------------------------

    def _log(self, event: str, data: dict) -> None:
        entry = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self._interaction_log.append(entry)

    def get_interaction_log(self) -> List[dict]:
        return list(self._interaction_log)

    def get_tier_info(self) -> dict:
        return get_bot_tier_info(self.tier)

    def upgrade_path(self) -> Optional[str]:
        path = get_upgrade_path(self.tier)
        if path is None:
            return None
        tier_attr = getattr(path, "tier", None)
        if tier_attr is None:
            return None
        return tier_attr.value

    def run(self) -> dict:
        """Return a status snapshot of the bot."""
        return {
            "bot": "HomeBuyerBot",
            "tier": self.tier.value,
            "leads": len(self._leads),
            "payments": len(self._payments),
            **self.revenue_summary(),
        }
