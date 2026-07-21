"""
Wealth System Bot — Main Module

Manages global Wealth Hubs — community investment vehicles that let members
pool capital, allocate assets, run automated bots, and distribute dividends.
Supports worldwide operation with multi-language, multi-currency, and
region-specific KYC/AML compliance.

Tier-aware: FREE gets basic hub creation and treasury management;
PRO adds governance, dividend engine, compliance, DreamCoin, and income/asset bots;
ENTERPRISE unlocks trading bots, full analytics, and white-label.

Adheres to the DreamCo bots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
import uuid
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.wealth_system_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_WEALTH_HUBS,
    FEATURE_TREASURY_MANAGEMENT,
    FEATURE_GOVERNANCE_VOTING,
    FEATURE_DIVIDEND_ENGINE,
    FEATURE_ASSET_ALLOCATION,
    FEATURE_DREAMCOIN,
    FEATURE_KYC_COMPLIANCE,
    FEATURE_AML_COMPLIANCE,
    FEATURE_GLOBAL_REGISTRY,
    FEATURE_MULTI_LANGUAGE,
    FEATURE_MULTI_CURRENCY,
    FEATURE_INCOME_BOTS,
    FEATURE_ASSET_BOTS,
    FEATURE_TRADING_BOTS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
    FEATURE_REFERRAL_SYSTEM,
    FEATURE_MARKETPLACE,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class WealthSystemBotError(Exception):
    """Base exception for Wealth System Bot errors."""


class WealthSystemBotTierError(WealthSystemBotError):
    """Raised when a feature is not available on the current tier."""


class WealthSystemBotNotFoundError(WealthSystemBotError):
    """Raised when a requested resource is not found."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AssetTier(Enum):
    STABILITY = "stability"      # 40 % target
    GROWTH = "growth"            # 40 % target
    HIGH_GROWTH = "high_growth"  # 20 % target


class PayoutSchedule(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    COMPOUND = "compound"


class BotType(Enum):
    INCOME = "income"
    ASSET = "asset"
    COMMERCE = "commerce"
    FINANCE = "finance"


class ComplianceStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HubStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"


class Language(Enum):
    EN = "en"   # English
    ES = "es"   # Spanish
    FR = "fr"   # French
    PT = "pt"   # Portuguese
    ZH = "zh"   # Chinese
    AR = "ar"   # Arabic
    HI = "hi"   # Hindi
    SW = "sw"   # Swahili


class Region(Enum):
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    AFRICA = "africa"
    ASIA = "asia"
    OCEANIA = "oceania"
    MIDDLE_EAST = "middle_east"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RegionConfig:
    region: Region
    supported_languages: list
    default_currency: str
    kyc_requirements: list
    aml_threshold_usd: float
    compliance_agencies: list
    tax_jurisdiction: str


@dataclass
class WealthHub:
    hub_id: str
    name: str
    owner_id: str
    city: str
    state: str
    country: str
    region: Region
    status: HubStatus
    treasury_balance: float
    members: list
    ownership_ledger: dict
    governance_votes: list
    language: Language
    currency: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Member:
    member_id: str
    user_id: str
    hub_id: str
    contribution_total: float
    ownership_pct: float
    dreamcoin_balance: float
    kyc_status: ComplianceStatus
    aml_status: ComplianceStatus
    joined_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class GovernanceProposal:
    proposal_id: str
    hub_id: str
    proposer_id: str
    title: str
    description: str
    votes_for: int
    votes_against: int
    status: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class DividendRecord:
    dividend_id: str
    hub_id: str
    amount: float
    payout_schedule: PayoutSchedule
    distributed_at: str
    member_payouts: dict


@dataclass
class AssetAllocation:
    allocation_id: str
    hub_id: str
    stability_pct: float
    growth_pct: float
    high_growth_pct: float
    assets: dict
    last_rebalanced: str


@dataclass
class ComplianceRecord:
    record_id: str
    user_id: str
    hub_id: str
    compliance_type: str
    status: ComplianceStatus
    notes: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class BotTask:
    task_id: str
    hub_id: str
    bot_type: BotType
    description: str
    earnings_usd: float
    status: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Region catalogue
# ---------------------------------------------------------------------------

REGION_CONFIG_CATALOGUE: dict[Region, RegionConfig] = {
    Region.NORTH_AMERICA: RegionConfig(
        region=Region.NORTH_AMERICA,
        supported_languages=[Language.EN, Language.ES, Language.FR],
        default_currency="USD",
        kyc_requirements=["government_id", "proof_of_address", "ssn_or_itin"],
        aml_threshold_usd=10_000.0,
        compliance_agencies=["FinCEN", "OFAC", "FINTRAC"],
        tax_jurisdiction="IRS / CRA",
    ),
    Region.SOUTH_AMERICA: RegionConfig(
        region=Region.SOUTH_AMERICA,
        supported_languages=[Language.ES, Language.PT],
        default_currency="BRL",
        kyc_requirements=["government_id", "proof_of_address", "cpf_or_rut"],
        aml_threshold_usd=5_000.0,
        compliance_agencies=["COAF", "UIF", "UAF"],
        tax_jurisdiction="Receita Federal / SUNAT",
    ),
    Region.EUROPE: RegionConfig(
        region=Region.EUROPE,
        supported_languages=[Language.EN, Language.FR, Language.ES, Language.PT],
        default_currency="EUR",
        kyc_requirements=["passport_or_national_id", "proof_of_address", "tax_id"],
        aml_threshold_usd=15_000.0,
        compliance_agencies=["EBA", "FCA", "BaFin", "AMF"],
        tax_jurisdiction="EU Tax Authority",
    ),
    Region.AFRICA: RegionConfig(
        region=Region.AFRICA,
        supported_languages=[Language.EN, Language.FR, Language.SW, Language.AR],
        default_currency="USD",
        kyc_requirements=["national_id", "proof_of_address"],
        aml_threshold_usd=3_000.0,
        compliance_agencies=["FATF", "ESAAMLG", "GIABA"],
        tax_jurisdiction="Regional Revenue Authority",
    ),
    Region.ASIA: RegionConfig(
        region=Region.ASIA,
        supported_languages=[Language.EN, Language.ZH, Language.HI],
        default_currency="USD",
        kyc_requirements=["passport", "proof_of_address", "national_id"],
        aml_threshold_usd=8_000.0,
        compliance_agencies=["MAS", "SEBI", "CSRC", "FSC"],
        tax_jurisdiction="National Tax Authority",
    ),
    Region.OCEANIA: RegionConfig(
        region=Region.OCEANIA,
        supported_languages=[Language.EN],
        default_currency="AUD",
        kyc_requirements=["driver_license_or_passport", "proof_of_address"],
        aml_threshold_usd=10_000.0,
        compliance_agencies=["AUSTRAC", "FMA"],
        tax_jurisdiction="ATO / IRD",
    ),
    Region.MIDDLE_EAST: RegionConfig(
        region=Region.MIDDLE_EAST,
        supported_languages=[Language.AR, Language.EN],
        default_currency="AED",
        kyc_requirements=["passport", "residence_visa", "proof_of_address"],
        aml_threshold_usd=7_000.0,
        compliance_agencies=["CBUAE", "CMA", "SAMA"],
        tax_jurisdiction="Regional Tax Authority",
    ),
}

# ---------------------------------------------------------------------------
# Language display labels
# ---------------------------------------------------------------------------

LANGUAGE_LABELS: dict[Language, str] = {
    Language.EN: "English",
    Language.ES: "Spanish",
    Language.FR: "French",
    Language.PT: "Portuguese",
    Language.ZH: "Chinese",
    Language.AR: "Arabic",
    Language.HI: "Hindi",
    Language.SW: "Swahili",
}

_LANGUAGE_GREETINGS: dict[Language, str] = {
    Language.EN: "Welcome to your Wealth Hub!",
    Language.ES: "¡Bienvenido a tu Centro de Riqueza!",
    Language.FR: "Bienvenue dans votre Hub de Richesse!",
    Language.PT: "Bem-vindo ao seu Hub de Riqueza!",
    Language.ZH: "欢迎来到您的财富中心！",
    Language.AR: "مرحباً بكم في مركز الثروة الخاص بكم!",
    Language.HI: "आपके वेल्थ हब में आपका स्वागत है!",
    Language.SW: "Karibu kwenye Kituo chako cha Utajiri!",
}


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class WealthSystemBot:
    """
    DreamCo Wealth System Bot.

    Manages global Wealth Hubs with treasury management, governance, asset
    allocation, dividend distribution, KYC/AML compliance, DreamCoin, and
    automated income/asset/trading bots.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._tier_config: TierConfig = get_tier_config(tier)

        # In-memory stores
        self._hubs: dict[str, WealthHub] = {}
        self._members: dict[str, Member] = {}
        self._proposals: dict[str, GovernanceProposal] = {}
        self._dividends: dict[str, DividendRecord] = {}
        self._allocations: dict[str, AssetAllocation] = {}
        self._compliance_records: dict[str, ComplianceRecord] = {}
        self._bot_tasks: dict[str, BotTask] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self._tier_config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade
                else ""
            )
            raise WealthSystemBotTierError(
                f"Feature '{feature}' is not available on the {self.tier.value} tier.{hint}"
            )

    def _recalculate_ownership(self, hub_id: str) -> None:
        """Recalculate ownership percentages for all hub members."""
        hub_members = [m for m in self._members.values() if m.hub_id == hub_id]
        total = sum(m.contribution_total for m in hub_members)
        for m in hub_members:
            m.ownership_pct = (m.contribution_total / total * 100.0) if total > 0 else 0.0
            self._hubs[hub_id].ownership_ledger[m.member_id] = m.ownership_pct

    # ------------------------------------------------------------------
    # Global Registry
    # ------------------------------------------------------------------

    def register_hub(
        self,
        owner_id: str,
        name: str,
        city: str,
        state: str,
        country: str,
        region: Region,
        language: Language = Language.EN,
        currency: str = "USD",
    ) -> WealthHub:
        """Create a new Wealth Hub. FREE tier limited to 3 hubs."""
        self._require_feature(FEATURE_WEALTH_HUBS)
        max_hubs = self._tier_config.max_hubs
        if max_hubs is not None and len(self._hubs) >= max_hubs:
            raise WealthSystemBotTierError(
                f"FREE tier allows a maximum of {max_hubs} hubs. "
                "Upgrade to Pro for unlimited hubs."
            )
        hub_id = f"hub_{uuid.uuid4().hex[:8]}"
        hub = WealthHub(
            hub_id=hub_id,
            name=name,
            owner_id=owner_id,
            city=city,
            state=state,
            country=country,
            region=region,
            status=HubStatus.ACTIVE,
            treasury_balance=0.0,
            members=[],
            ownership_ledger={},
            governance_votes=[],
            language=language,
            currency=currency,
        )
        self._hubs[hub_id] = hub
        return hub

    def get_hub(self, hub_id: str) -> WealthHub:
        """Return a hub by ID or raise NotFoundError."""
        hub = self._hubs.get(hub_id)
        if hub is None:
            raise WealthSystemBotNotFoundError(f"Hub '{hub_id}' not found.")
        return hub

    def list_hubs(
        self,
        region: Optional[Region] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
    ) -> list:
        """Return hubs, optionally filtered by region, country, or city."""
        hubs = list(self._hubs.values())
        if region is not None:
            hubs = [h for h in hubs if h.region == region]
        if country is not None:
            hubs = [h for h in hubs if h.country.lower() == country.lower()]
        if city is not None:
            hubs = [h for h in hubs if h.city.lower() == city.lower()]
        return hubs

    def get_region_config(self, region: Region) -> RegionConfig:
        """Return configuration for a region."""
        return REGION_CONFIG_CATALOGUE[region]

    def list_supported_regions(self) -> list:
        """Return all supported regions."""
        return list(Region)

    # ------------------------------------------------------------------
    # Localization
    # ------------------------------------------------------------------

    def get_language_label(self, language: Language) -> str:
        """Return the display name for a language."""
        return LANGUAGE_LABELS[language]

    def translate_hub_summary(self, hub_id: str, language: Language) -> dict:
        """Return a hub summary with a localized greeting message."""
        self._require_feature(FEATURE_MULTI_LANGUAGE)
        hub = self.get_hub(hub_id)
        greeting = _LANGUAGE_GREETINGS.get(language, _LANGUAGE_GREETINGS[Language.EN])
        return {
            "hub_id": hub.hub_id,
            "name": hub.name,
            "city": hub.city,
            "country": hub.country,
            "region": hub.region.value,
            "language": language.value,
            "currency": hub.currency,
            "treasury_balance": hub.treasury_balance,
            "member_count": len(hub.members),
            "greeting": greeting,
        }

    # ------------------------------------------------------------------
    # Member Management
    # ------------------------------------------------------------------

    def add_member(self, hub_id: str, user_id: str) -> Member:
        """Add a user to a hub. Capacity limits apply per tier."""
        hub = self.get_hub(hub_id)
        max_members = self._tier_config.max_members_per_hub
        if max_members is not None and len(hub.members) >= max_members:
            raise WealthSystemBotTierError(
                f"Hub has reached the member capacity of {max_members} for "
                f"the {self.tier.value} tier."
            )
        member_id = f"mbr_{uuid.uuid4().hex[:8]}"
        member = Member(
            member_id=member_id,
            user_id=user_id,
            hub_id=hub_id,
            contribution_total=0.0,
            ownership_pct=0.0,
            dreamcoin_balance=0.0,
            kyc_status=ComplianceStatus.PENDING,
            aml_status=ComplianceStatus.PENDING,
        )
        self._members[member_id] = member
        hub.members.append(member_id)
        return member

    def get_member(self, member_id: str) -> Member:
        """Return a member by ID or raise NotFoundError."""
        member = self._members.get(member_id)
        if member is None:
            raise WealthSystemBotNotFoundError(f"Member '{member_id}' not found.")
        return member

    def get_hub_members(self, hub_id: str) -> list:
        """Return all members belonging to a hub."""
        self.get_hub(hub_id)  # validate hub exists
        return [m for m in self._members.values() if m.hub_id == hub_id]

    def contribute(self, member_id: str, amount_usd: float) -> Member:
        """Add a USD contribution for a member and recalculate ownership."""
        member = self.get_member(member_id)
        hub = self.get_hub(member.hub_id)
        member.contribution_total += amount_usd
        hub.treasury_balance += amount_usd
        self._recalculate_ownership(member.hub_id)
        return member

    # ------------------------------------------------------------------
    # KYC / AML Compliance
    # ------------------------------------------------------------------

    def submit_kyc(self, user_id: str, hub_id: str, documents: list) -> ComplianceRecord:
        """Submit KYC documents for a user. Requires KYC feature."""
        self._require_feature(FEATURE_KYC_COMPLIANCE)
        self.get_hub(hub_id)
        record_id = f"kyc_{uuid.uuid4().hex[:8]}"
        record = ComplianceRecord(
            record_id=record_id,
            user_id=user_id,
            hub_id=hub_id,
            compliance_type="kyc",
            status=ComplianceStatus.PENDING,
            notes=f"Documents submitted: {', '.join(documents)}",
        )
        self._compliance_records[record_id] = record
        return record

    def approve_kyc(self, record_id: str) -> ComplianceRecord:
        """Approve a KYC compliance record."""
        record = self._compliance_records.get(record_id)
        if record is None:
            raise WealthSystemBotNotFoundError(f"Compliance record '{record_id}' not found.")
        record.status = ComplianceStatus.APPROVED
        return record

    def reject_kyc(self, record_id: str, reason: str) -> ComplianceRecord:
        """Reject a KYC compliance record with a reason."""
        record = self._compliance_records.get(record_id)
        if record is None:
            raise WealthSystemBotNotFoundError(f"Compliance record '{record_id}' not found.")
        record.status = ComplianceStatus.REJECTED
        record.notes = reason
        return record

    def submit_aml_check(
        self, user_id: str, hub_id: str, transaction_amount: float
    ) -> ComplianceRecord:
        """Submit an AML check. Auto-approves if below region threshold."""
        self._require_feature(FEATURE_AML_COMPLIANCE)
        hub = self.get_hub(hub_id)
        region_cfg = REGION_CONFIG_CATALOGUE[hub.region]
        record_id = f"aml_{uuid.uuid4().hex[:8]}"
        status = (
            ComplianceStatus.PENDING
            if transaction_amount > region_cfg.aml_threshold_usd
            else ComplianceStatus.APPROVED
        )
        record = ComplianceRecord(
            record_id=record_id,
            user_id=user_id,
            hub_id=hub_id,
            compliance_type="aml",
            status=status,
            notes=f"Transaction amount: ${transaction_amount:,.2f}",
        )
        self._compliance_records[record_id] = record
        return record

    def get_compliance_records(self, hub_id: str) -> list:
        """Return all compliance records for a hub."""
        self.get_hub(hub_id)
        return [r for r in self._compliance_records.values() if r.hub_id == hub_id]

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------

    def create_proposal(
        self, hub_id: str, proposer_id: str, title: str, description: str
    ) -> GovernanceProposal:
        """Create a governance proposal. Requires GOVERNANCE_VOTING feature."""
        self._require_feature(FEATURE_GOVERNANCE_VOTING)
        self.get_hub(hub_id)
        proposal_id = f"prop_{uuid.uuid4().hex[:8]}"
        proposal = GovernanceProposal(
            proposal_id=proposal_id,
            hub_id=hub_id,
            proposer_id=proposer_id,
            title=title,
            description=description,
            votes_for=0,
            votes_against=0,
            status="open",
        )
        self._proposals[proposal_id] = proposal
        return proposal

    def vote_on_proposal(
        self, proposal_id: str, voter_id: str, vote: bool
    ) -> GovernanceProposal:
        """Cast a vote on a proposal. True = for, False = against."""
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise WealthSystemBotNotFoundError(f"Proposal '{proposal_id}' not found.")
        if vote:
            proposal.votes_for += 1
        else:
            proposal.votes_against += 1
        return proposal

    def finalize_proposal(self, proposal_id: str) -> GovernanceProposal:
        """Finalize a proposal: approved if votes_for > votes_against."""
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise WealthSystemBotNotFoundError(f"Proposal '{proposal_id}' not found.")
        proposal.status = "approved" if proposal.votes_for > proposal.votes_against else "rejected"
        return proposal

    def list_proposals(self, hub_id: str) -> list:
        """Return all proposals for a hub."""
        self.get_hub(hub_id)
        return [p for p in self._proposals.values() if p.hub_id == hub_id]

    # ------------------------------------------------------------------
    # Asset Allocation
    # ------------------------------------------------------------------

    def set_asset_allocation(
        self,
        hub_id: str,
        stability_pct: float,
        growth_pct: float,
        high_growth_pct: float,
        assets: dict,
    ) -> AssetAllocation:
        """Set the asset allocation for a hub. Percentages must sum to 100."""
        self._require_feature(FEATURE_ASSET_ALLOCATION)
        self.get_hub(hub_id)
        total = stability_pct + growth_pct + high_growth_pct
        if abs(total - 100.0) > 0.001:
            raise ValueError(
                f"stability_pct + growth_pct + high_growth_pct must equal 100 (got {total})."
            )
        allocation_id = f"alloc_{uuid.uuid4().hex[:8]}"
        allocation = AssetAllocation(
            allocation_id=allocation_id,
            hub_id=hub_id,
            stability_pct=stability_pct,
            growth_pct=growth_pct,
            high_growth_pct=high_growth_pct,
            assets=assets,
            last_rebalanced=datetime.now(timezone.utc).isoformat(),
        )
        self._allocations[hub_id] = allocation
        return allocation

    def get_asset_allocation(self, hub_id: str) -> AssetAllocation:
        """Return the asset allocation for a hub or raise NotFoundError."""
        self.get_hub(hub_id)
        allocation = self._allocations.get(hub_id)
        if allocation is None:
            raise WealthSystemBotNotFoundError(
                f"No asset allocation set for hub '{hub_id}'."
            )
        return allocation

    def rebalance_portfolio(self, hub_id: str) -> AssetAllocation:
        """Update last_rebalanced timestamp for a hub's allocation."""
        allocation = self.get_asset_allocation(hub_id)
        allocation.last_rebalanced = datetime.now(timezone.utc).isoformat()
        return allocation

    # ------------------------------------------------------------------
    # Dividend Engine
    # ------------------------------------------------------------------

    def distribute_dividends(
        self,
        hub_id: str,
        profit_amount: float,
        payout_schedule: PayoutSchedule,
        reinvest_pct: float = 0.0,
    ) -> DividendRecord:
        """
        Distribute dividends to hub members proportional to ownership_pct.
        reinvest_pct (0-100) of profit_amount is reinvested back to treasury.
        """
        self._require_feature(FEATURE_DIVIDEND_ENGINE)
        hub = self.get_hub(hub_id)
        distributable = profit_amount * (1.0 - reinvest_pct / 100.0)
        reinvested = profit_amount - distributable
        hub.treasury_balance += reinvested

        members = self.get_hub_members(hub_id)
        member_payouts: dict[str, float] = {}
        for m in members:
            payout = distributable * (m.ownership_pct / 100.0)
            member_payouts[m.member_id] = payout

        dividend_id = f"div_{uuid.uuid4().hex[:8]}"
        record = DividendRecord(
            dividend_id=dividend_id,
            hub_id=hub_id,
            amount=distributable,
            payout_schedule=payout_schedule,
            distributed_at=datetime.now(timezone.utc).isoformat(),
            member_payouts=member_payouts,
        )
        self._dividends[dividend_id] = record
        return record

    def get_dividend_history(self, hub_id: str) -> list:
        """Return all dividend records for a hub."""
        self.get_hub(hub_id)
        return [d for d in self._dividends.values() if d.hub_id == hub_id]

    # ------------------------------------------------------------------
    # DreamCoin
    # ------------------------------------------------------------------

    def stake_dreamcoin(self, member_id: str, amount: float) -> Member:
        """Stake DreamCoin for a member. Requires DREAMCOIN feature."""
        self._require_feature(FEATURE_DREAMCOIN)
        member = self.get_member(member_id)
        member.dreamcoin_balance += amount
        return member

    def get_dreamcoin_balance(self, member_id: str) -> float:
        """Return the DreamCoin balance of a member."""
        return self.get_member(member_id).dreamcoin_balance

    # ------------------------------------------------------------------
    # Bot Tasks
    # ------------------------------------------------------------------

    def run_income_bot(self, hub_id: str, description: str) -> BotTask:
        """Run an income bot task. Requires INCOME_BOTS feature."""
        self._require_feature(FEATURE_INCOME_BOTS)
        self.get_hub(hub_id)
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = BotTask(
            task_id=task_id,
            hub_id=hub_id,
            bot_type=BotType.INCOME,
            description=description,
            earnings_usd=round(random.uniform(10.0, 500.0), 2),
            status="completed",
        )
        self._bot_tasks[task_id] = task
        return task

    def run_asset_bot(self, hub_id: str, description: str) -> BotTask:
        """Run an asset management bot task. Requires ASSET_BOTS feature."""
        self._require_feature(FEATURE_ASSET_BOTS)
        self.get_hub(hub_id)
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = BotTask(
            task_id=task_id,
            hub_id=hub_id,
            bot_type=BotType.ASSET,
            description=description,
            earnings_usd=round(random.uniform(50.0, 1000.0), 2),
            status="completed",
        )
        self._bot_tasks[task_id] = task
        return task

    def run_trading_bot(self, hub_id: str, description: str) -> BotTask:
        """Run a trading bot task. Requires TRADING_BOTS feature (ENTERPRISE+)."""
        self._require_feature(FEATURE_TRADING_BOTS)
        self.get_hub(hub_id)
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = BotTask(
            task_id=task_id,
            hub_id=hub_id,
            bot_type=BotType.FINANCE,
            description=description,
            earnings_usd=round(random.uniform(20.0, 2000.0), 2),
            status="completed",
        )
        self._bot_tasks[task_id] = task
        return task

    def list_bot_tasks(self, hub_id: str) -> list:
        """Return all bot tasks for a hub."""
        self.get_hub(hub_id)
        return [t for t in self._bot_tasks.values() if t.hub_id == hub_id]

    def get_total_bot_earnings(self, hub_id: str) -> float:
        """Return the sum of all bot task earnings for a hub."""
        return sum(t.earnings_usd for t in self.list_bot_tasks(hub_id))

    # ------------------------------------------------------------------
    # Referral System
    # ------------------------------------------------------------------

    def generate_referral_link(self, hub_id: str, user_id: str) -> str:
        """Generate a referral URL for a hub/user. Requires REFERRAL_SYSTEM feature."""
        self._require_feature(FEATURE_REFERRAL_SYSTEM)
        self.get_hub(hub_id)
        token = uuid.uuid4().hex[:12]
        return f"https://dreamco.io/join?hub={hub_id}&ref={user_id}&token={token}"

    # ------------------------------------------------------------------
    # Analytics (ENTERPRISE+)
    # ------------------------------------------------------------------

    def get_hub_analytics(self, hub_id: str) -> dict:
        """Return analytics for a hub. Requires ANALYTICS feature (ENTERPRISE+)."""
        self._require_feature(FEATURE_ANALYTICS)
        hub = self.get_hub(hub_id)
        members = self.get_hub_members(hub_id)
        total_contributions = sum(m.contribution_total for m in members)
        total_bot_earnings = self.get_total_bot_earnings(hub_id)
        dividends = self.get_dividend_history(hub_id)
        total_dividends = sum(d.amount for d in dividends)
        allocation = self._allocations.get(hub_id)
        allocation_summary = (
            {
                "stability_pct": allocation.stability_pct,
                "growth_pct": allocation.growth_pct,
                "high_growth_pct": allocation.high_growth_pct,
            }
            if allocation
            else None
        )
        return {
            "hub_id": hub_id,
            "treasury_balance": hub.treasury_balance,
            "member_count": len(members),
            "total_contributions": total_contributions,
            "total_bot_earnings": total_bot_earnings,
            "allocation_summary": allocation_summary,
            "total_dividends_distributed": total_dividends,
        }

    # ------------------------------------------------------------------
    # Chat / process interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """Return a helpful response describing the bot's capabilities."""
        msg = message.lower()

        if any(kw in msg for kw in ("hub", "create hub", "register hub", "wealth hub")):
            return (
                "Use register_hub(owner_id, name, city, state, country, region) "
                "to create a new Wealth Hub in any city or country worldwide."
            )

        if any(kw in msg for kw in ("member", "join", "add member")):
            return (
                "Use add_member(hub_id, user_id) to add a member to a hub, "
                "then contribute(member_id, amount_usd) to fund the treasury."
            )

        if any(kw in msg for kw in ("kyc", "aml", "compliance")):
            return (
                "KYC and AML compliance are available on the Pro tier. "
                "Use submit_kyc() or submit_aml_check() to initiate checks."
            )

        if any(kw in msg for kw in ("dividend", "payout", "earnings")):
            return (
                "Use distribute_dividends(hub_id, profit_amount, payout_schedule) "
                "to distribute profits to members proportional to their ownership."
            )

        if any(kw in msg for kw in ("bot", "income bot", "asset bot", "trading bot")):
            return (
                "Income and asset bots are available on Pro. "
                "Trading bots require the Enterprise tier. "
                "Use run_income_bot(), run_asset_bot(), or run_trading_bot()."
            )

        if any(kw in msg for kw in ("analytics", "stats", "report")):
            return (
                "Full hub analytics are available on the Enterprise tier. "
                "Use get_hub_analytics(hub_id) for a complete summary."
            )

        return (
            "DreamCo Wealth System Bot online. "
            f"Tier: {self.tier.value}. "
            "Commands: register_hub, add_member, contribute, create_proposal, "
            "distribute_dividends, run_income_bot, get_hub_analytics, and more."
        )

    def process(self, data: dict) -> dict:
        """Dispatch an action dict to the appropriate method."""
        action = data.get("action", "")
        try:
            if action == "register_hub":
                result = self.register_hub(
                    owner_id=data["owner_id"],
                    name=data["name"],
                    city=data["city"],
                    state=data["state"],
                    country=data["country"],
                    region=Region(data["region"]),
                    language=Language(data.get("language", "en")),
                    currency=data.get("currency", "USD"),
                )
                return {"success": True, "data": result}

            if action == "get_hub":
                return {"success": True, "data": self.get_hub(data["hub_id"])}

            if action == "list_hubs":
                region = Region(data["region"]) if "region" in data else None
                return {
                    "success": True,
                    "data": self.list_hubs(
                        region=region,
                        country=data.get("country"),
                        city=data.get("city"),
                    ),
                }

            if action == "add_member":
                result = self.add_member(data["hub_id"], data["user_id"])
                return {"success": True, "data": result}

            if action == "contribute":
                result = self.contribute(data["member_id"], float(data["amount_usd"]))
                return {"success": True, "data": result}

            if action == "chat":
                return {"success": True, "data": self.chat(data.get("message", ""))}

            return {"success": False, "data": f"Unknown action: '{action}'"}

        except (WealthSystemBotError, ValueError, KeyError) as exc:
            return {"success": False, "data": str(exc)}


# ---------------------------------------------------------------------------
# Module-level run() helper
# ---------------------------------------------------------------------------

def run(tier: Tier = Tier.FREE) -> None:  # pragma: no cover
    """Quick demo of the Wealth System Bot."""
    bot = WealthSystemBot(tier=tier)
    print(f"=== DreamCo Wealth System Bot [{tier.value.upper()}] ===")

    print("\n-- Registering a Wealth Hub --")
    hub = bot.register_hub(
        owner_id="user_001",
        name="Global Growth Hub",
        city="New York",
        state="NY",
        country="USA",
        region=Region.NORTH_AMERICA,
        language=Language.EN,
        currency="USD",
    )
    print(f"  Hub ID: {hub.hub_id} | Name: {hub.name} | Region: {hub.region.value}")

    print("\n-- Adding Members --")
    m1 = bot.add_member(hub.hub_id, "user_002")
    m2 = bot.add_member(hub.hub_id, "user_003")
    bot.contribute(m1.member_id, 5000)
    bot.contribute(m2.member_id, 3000)
    print(f"  Member 1 ownership: {bot.get_member(m1.member_id).ownership_pct:.1f}%")
    print(f"  Member 2 ownership: {bot.get_member(m2.member_id).ownership_pct:.1f}%")
    print(f"  Treasury balance: ${bot.get_hub(hub.hub_id).treasury_balance:,.2f}")

    print("\n-- Localization --")
    summary = bot.translate_hub_summary(hub.hub_id, Language.ES)
    print(f"  Greeting (ES): {summary['greeting']}")

    print("\n-- Region Config --")
    rc = bot.get_region_config(Region.NORTH_AMERICA)
    print(f"  Default currency: {rc.default_currency}")
    print(f"  AML threshold: ${rc.aml_threshold_usd:,.2f}")

    print("\n-- Chat --")
    print(f"  {bot.chat('tell me about wealth hubs')}")


if __name__ == "__main__":  # pragma: no cover
    run(Tier.FREE)
