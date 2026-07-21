"""
Financial Literacy Bot — Main Module

Educates users on building credit, leveraging credit for investments,
and generating income.  Provides actionable advice, automated reminders,
investment calculators, mock bank/credit-bureau integration, a personalized
education path, and a community platform.

Tier-aware: FREE gets basic credit tips + 1 investment calculator;
PRO adds alerts, OPM strategies, bank integration, and education paths;
ENTERPRISE unlocks full community, analytics, white-label, and Stripe billing.

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

from bots.financial_literacy_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_CREDIT_TIPS,
    FEATURE_CREDIT_ALERTS,
    FEATURE_OPM_STRATEGIES,
    FEATURE_INVESTMENT_CALCULATOR,
    FEATURE_BANK_INTEGRATION,
    FEATURE_AUTOMATED_REMINDERS,
    FEATURE_EDUCATION_PATHS,
    FEATURE_COMMUNITY_READ,
    FEATURE_COMMUNITY_POST,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
    FEATURE_PRODUCT_MATCHING,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FinancialLiteracyBotError(Exception):
    """Base exception for Financial Literacy Bot errors."""


class FinancialLiteracyBotTierError(FinancialLiteracyBotError):
    """Raised when a feature is not available on the current tier."""


class FinancialLiteracyBotNotFoundError(FinancialLiteracyBotError):
    """Raised when a requested resource is not found."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class InvestmentType(Enum):
    REAL_ESTATE = "real_estate"
    STOCKS = "stocks"
    STARTUP = "startup"
    INDEX_FUND = "index_fund"
    CRYPTO = "crypto"


class CreditScoreRange(Enum):
    POOR = "poor"           # 300–579
    FAIR = "fair"           # 580–669
    GOOD = "good"           # 670–739
    VERY_GOOD = "very_good" # 740–799
    EXCEPTIONAL = "exceptional"  # 800–850


class EducationLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ReminderType(Enum):
    PAYMENT_DUE = "payment_due"
    UTILIZATION_CHECK = "utilization_check"
    CREDIT_REPORT = "credit_report"
    INVESTMENT_REVIEW = "investment_review"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CreditProfile:
    profile_id: str
    user_id: str
    credit_score: int
    total_credit_limit: float
    total_balance: float
    on_time_payments: int
    missed_payments: int
    oldest_account_years: float
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def utilization_rate(self) -> float:
        if self.total_credit_limit <= 0:
            return 0.0
        return self.total_balance / self.total_credit_limit

    @property
    def score_range(self) -> CreditScoreRange:
        if self.credit_score < 580:
            return CreditScoreRange.POOR
        if self.credit_score < 670:
            return CreditScoreRange.FAIR
        if self.credit_score < 740:
            return CreditScoreRange.GOOD
        if self.credit_score < 800:
            return CreditScoreRange.VERY_GOOD
        return CreditScoreRange.EXCEPTIONAL


@dataclass
class InvestmentCalculation:
    calc_id: str
    investment_type: InvestmentType
    principal: float
    annual_return_pct: float
    years: int
    credit_rate_pct: float
    result_roi_pct: float
    result_net_profit: float
    result_total_value: float
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class EducationModule:
    module_id: str
    title: str
    level: EducationLevel
    topic: str
    content_summary: str
    estimated_minutes: int
    tags: list = field(default_factory=list)


@dataclass
class Reminder:
    reminder_id: str
    user_id: str
    reminder_type: ReminderType
    message: str
    due_date: Optional[str] = None
    sent: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class CommunityPost:
    post_id: str
    user_id: str
    title: str
    body: str
    tags: list = field(default_factory=list)
    upvotes: int = 0
    replies: list = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class FinancialProduct:
    product_id: str
    name: str
    product_type: str           # credit_card | personal_loan | heloc
    apr_pct: float
    credit_score_min: int
    credit_limit_max: Optional[float]
    promotional_apr_pct: Optional[float]   # e.g. 0% intro APR
    promotional_months: Optional[int]
    description: str


# ---------------------------------------------------------------------------
# Education content catalogue
# ---------------------------------------------------------------------------

EDUCATION_CATALOGUE: list[EducationModule] = [
    EducationModule(
        module_id="edu_001",
        title="Understanding Your Credit Score",
        level=EducationLevel.BEGINNER,
        topic="credit_basics",
        content_summary=(
            "Learn what makes up your credit score: payment history (35%), "
            "utilization (30%), length of history (15%), new credit (10%), "
            "and credit mix (10%)."
        ),
        estimated_minutes=10,
        tags=["credit score", "basics", "payment history"],
    ),
    EducationModule(
        module_id="edu_002",
        title="Keeping Utilization Below 30%",
        level=EducationLevel.BEGINNER,
        topic="utilization",
        content_summary=(
            "Keeping your credit utilization below 30% (ideally below 10%) "
            "signals responsible borrowing and directly boosts your score."
        ),
        estimated_minutes=8,
        tags=["utilization", "credit card", "basics"],
    ),
    EducationModule(
        module_id="edu_003",
        title="Building Credit From Scratch",
        level=EducationLevel.BEGINNER,
        topic="credit_building",
        content_summary=(
            "Strategies for those with no credit history: secured cards, "
            "credit-builder loans, becoming an authorized user, and reporting "
            "rent/utilities."
        ),
        estimated_minutes=12,
        tags=["no credit", "secured card", "credit builder loan"],
    ),
    EducationModule(
        module_id="edu_004",
        title="OPM: Using Other People's Money to Invest",
        level=EducationLevel.INTERMEDIATE,
        topic="opm_strategies",
        content_summary=(
            "How to responsibly leverage 0% APR promotional periods, HELOCs, "
            "and business credit lines to fund investments and generate returns "
            "that exceed borrowing costs."
        ),
        estimated_minutes=20,
        tags=["OPM", "leverage", "0% APR", "HELOC", "investing"],
    ),
    EducationModule(
        module_id="edu_005",
        title="Real Estate Investing With Credit",
        level=EducationLevel.INTERMEDIATE,
        topic="real_estate",
        content_summary=(
            "Using HELOCs and low-interest credit to fund down payments or "
            "renovations, structuring deals for positive cash flow, and "
            "understanding LTV ratios."
        ),
        estimated_minutes=25,
        tags=["real estate", "HELOC", "cash flow", "LTV"],
    ),
    EducationModule(
        module_id="edu_006",
        title="Reading and Disputing Your Credit Report",
        level=EducationLevel.INTERMEDIATE,
        topic="credit_report",
        content_summary=(
            "How to pull your free annual credit reports, identify errors, "
            "write dispute letters to Equifax / Experian / TransUnion, and "
            "follow up effectively."
        ),
        estimated_minutes=15,
        tags=["credit report", "dispute", "Equifax", "Experian", "TransUnion"],
    ),
    EducationModule(
        module_id="edu_007",
        title="Advanced Credit Arbitrage",
        level=EducationLevel.ADVANCED,
        topic="credit_arbitrage",
        content_summary=(
            "Sophisticated strategies: balance-transfer arbitrage, manufactured "
            "spending for rewards, leveraging business credit lines at scale, and "
            "maintaining credit health during heavy utilization."
        ),
        estimated_minutes=35,
        tags=["arbitrage", "balance transfer", "business credit", "rewards"],
    ),
    EducationModule(
        module_id="edu_008",
        title="Building a Stock Portfolio With Margin",
        level=EducationLevel.ADVANCED,
        topic="stocks_margin",
        content_summary=(
            "Understanding margin accounts, calculating margin calls, "
            "diversification strategies, and when to use leverage vs. "
            "avoid it in volatile markets."
        ),
        estimated_minutes=30,
        tags=["stocks", "margin", "portfolio", "leverage"],
    ),
]

# ---------------------------------------------------------------------------
# Financial product catalogue (mock/demo data)
# ---------------------------------------------------------------------------

PRODUCT_CATALOGUE: list[FinancialProduct] = [
    FinancialProduct(
        product_id="prod_001",
        name="DreamCo 0% APR Starter Card",
        product_type="credit_card",
        apr_pct=22.99,
        credit_score_min=580,
        credit_limit_max=5000.0,
        promotional_apr_pct=0.0,
        promotional_months=15,
        description="15 months 0% APR on purchases. Great for OPM strategies.",
    ),
    FinancialProduct(
        product_id="prod_002",
        name="DreamCo Builder Secured Card",
        product_type="credit_card",
        apr_pct=19.99,
        credit_score_min=300,
        credit_limit_max=2500.0,
        promotional_apr_pct=None,
        promotional_months=None,
        description="Secured card for building or rebuilding credit. No min score.",
    ),
    FinancialProduct(
        product_id="prod_003",
        name="DreamCo Premium Rewards Card",
        product_type="credit_card",
        apr_pct=17.99,
        credit_score_min=740,
        credit_limit_max=None,
        promotional_apr_pct=0.0,
        promotional_months=12,
        description="2% cash back, travel perks, 12-month 0% APR for excellent credit.",
    ),
    FinancialProduct(
        product_id="prod_004",
        name="DreamCo Personal Loan",
        product_type="personal_loan",
        apr_pct=9.99,
        credit_score_min=670,
        credit_limit_max=50000.0,
        promotional_apr_pct=None,
        promotional_months=None,
        description="Low-interest personal loan for debt consolidation or investing.",
    ),
    FinancialProduct(
        product_id="prod_005",
        name="DreamCo HELOC",
        product_type="heloc",
        apr_pct=7.49,
        credit_score_min=700,
        credit_limit_max=250000.0,
        promotional_apr_pct=None,
        promotional_months=None,
        description="Home equity line for real estate investing. Variable APR.",
    ),
]

# ---------------------------------------------------------------------------
# Credit tips (FREE tier)
# ---------------------------------------------------------------------------

CREDIT_TIPS: list[str] = [
    "Pay all bills on time — payment history is 35% of your score.",
    "Keep credit utilization below 30%; below 10% is ideal.",
    "Don't close old accounts — length of credit history helps your score.",
    "Limit hard inquiries; space out credit applications by 6+ months.",
    "Dispute errors on your credit report with all three bureaus annually.",
    "Become an authorized user on a family member's long-standing account.",
    "Diversify your credit mix with both revolving and installment accounts.",
    "Set up autopay for at least the minimum to avoid missed payments.",
    "Request a credit-limit increase annually to lower utilization passively.",
    "Use a secured card if you have no credit history — deposit = limit.",
]

# ---------------------------------------------------------------------------
# OPM Strategy templates (PRO+)
# ---------------------------------------------------------------------------

OPM_STRATEGIES: list[dict] = [
    {
        "strategy_id": "opm_001",
        "name": "0% APR Cash-Flow Arbitrage",
        "description": (
            "Apply for a 0% APR promotional credit card. "
            "Transfer balance or use cash advance into a high-yield savings account "
            "(4–5% APY). Earn interest on borrowed money during the promo period. "
            "Pay off the full balance before the promo ends."
        ),
        "risk_level": "low",
        "required_credit_score": 670,
        "estimated_return_pct": 4.5,
    },
    {
        "strategy_id": "opm_002",
        "name": "HELOC Real Estate Down Payment",
        "description": (
            "Use a HELOC on your primary residence to fund a down payment on a "
            "rental property. Rental income services both mortgages; appreciation "
            "builds equity. Requires positive cash flow analysis."
        ),
        "risk_level": "medium",
        "required_credit_score": 700,
        "estimated_return_pct": 12.0,
    },
    {
        "strategy_id": "opm_003",
        "name": "Business Credit Line for E-Commerce Inventory",
        "description": (
            "Open a business credit line (Net-30 or revolving). "
            "Purchase inventory at wholesale, sell at retail margin. "
            "Repay line from sale proceeds. Cycle repeats each month."
        ),
        "risk_level": "medium",
        "required_credit_score": 680,
        "estimated_return_pct": 20.0,
    },
    {
        "strategy_id": "opm_004",
        "name": "Balance Transfer Stack",
        "description": (
            "Use multiple 0% APR balance-transfer cards to consolidate high-interest "
            "debt. Free up cash flow that gets redirected into index funds or "
            "rental property. Clear balances before promo periods expire."
        ),
        "risk_level": "low",
        "required_credit_score": 660,
        "estimated_return_pct": 8.0,
    },
]


# ---------------------------------------------------------------------------
# Main Bot
# ---------------------------------------------------------------------------

class FinancialLiteracyBot:
    """
    Tier-aware financial literacy and credit automation bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    user_id : str | None
        Optional identifier for the current user session.
    """

    def __init__(self, tier: Tier = Tier.FREE, user_id: Optional[str] = None) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id: str = user_id or f"user_{uuid.uuid4().hex[:8]}"

        self._credit_profiles: dict[str, CreditProfile] = {}
        self._calculations: list[InvestmentCalculation] = []
        self._reminders: list[Reminder] = []
        self._community_posts: list[CommunityPost] = []
        self._completed_modules: list[str] = []
        self._calc_counter: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = f" Upgrade to {upgrade.name} to unlock." if upgrade else ""
            raise FinancialLiteracyBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # 1. Credit Building Assistance
    # ------------------------------------------------------------------

    def get_credit_tips(self, count: int = 5) -> list[str]:
        """Return actionable credit-improvement tips (FREE+)."""
        self._require_feature(FEATURE_CREDIT_TIPS)
        count = max(1, min(count, len(CREDIT_TIPS)))
        return random.sample(CREDIT_TIPS, count)

    def analyze_credit_profile(
        self,
        credit_score: int,
        total_credit_limit: float,
        total_balance: float,
        on_time_payments: int = 0,
        missed_payments: int = 0,
        oldest_account_years: float = 0.0,
    ) -> dict:
        """
        Store a credit profile and return personalised improvement advice (FREE+).
        """
        self._require_feature(FEATURE_CREDIT_TIPS)
        if not (300 <= credit_score <= 850):
            raise FinancialLiteracyBotError(
                "credit_score must be between 300 and 850."
            )
        if total_credit_limit < 0 or total_balance < 0:
            raise FinancialLiteracyBotError(
                "total_credit_limit and total_balance must be non-negative."
            )

        profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        profile = CreditProfile(
            profile_id=profile_id,
            user_id=self.user_id,
            credit_score=credit_score,
            total_credit_limit=total_credit_limit,
            total_balance=total_balance,
            on_time_payments=on_time_payments,
            missed_payments=missed_payments,
            oldest_account_years=oldest_account_years,
        )
        self._credit_profiles[profile_id] = profile

        advice = []
        utilization = profile.utilization_rate
        if utilization > 0.30:
            advice.append(
                f"Your utilization is {utilization:.0%}. Pay down balances to get below 30%."
            )
        elif utilization > 0.10:
            advice.append(
                f"Utilization at {utilization:.0%}. Getting below 10% will further boost your score."
            )
        else:
            advice.append(f"Excellent utilization at {utilization:.0%}. Keep it up!")

        if missed_payments > 0:
            advice.append(
                f"You have {missed_payments} missed payment(s). Set up autopay to prevent future misses."
            )
        if oldest_account_years < 2:
            advice.append("Your credit history is short. Avoid closing old accounts.")
        if credit_score < 670:
            advice.append("Consider a secured card or credit-builder loan to improve your score faster.")

        return {
            "profile_id": profile_id,
            "credit_score": credit_score,
            "score_range": profile.score_range.value,
            "utilization_rate": round(utilization, 4),
            "advice": advice,
        }

    def get_credit_alerts(self, profile_id: str) -> list[dict]:
        """
        Return upcoming-payment and utilization alerts for a profile (PRO+).
        """
        self._require_feature(FEATURE_CREDIT_ALERTS)
        if profile_id not in self._credit_profiles:
            raise FinancialLiteracyBotNotFoundError(
                f"Credit profile '{profile_id}' not found."
            )
        profile = self._credit_profiles[profile_id]
        alerts = []

        if profile.utilization_rate > 0.30:
            alerts.append({
                "type": "utilization_warning",
                "message": (
                    f"Utilization at {profile.utilization_rate:.0%}. "
                    "Pay down balances before your next statement to protect your score."
                ),
                "severity": "high",
            })
        if profile.missed_payments > 0:
            alerts.append({
                "type": "missed_payment",
                "message": (
                    f"{profile.missed_payments} missed payment(s) on record. "
                    "Dispute if incorrect, or establish consistent autopay."
                ),
                "severity": "critical",
            })
        if profile.credit_score < 620:
            alerts.append({
                "type": "score_at_risk",
                "message": (
                    "Credit score below 620. You may be denied for most credit products. "
                    "Focus on on-time payments and reducing balances."
                ),
                "severity": "critical",
            })
        if not alerts:
            alerts.append({
                "type": "all_clear",
                "message": "No urgent alerts. Your credit profile looks healthy.",
                "severity": "info",
            })
        return alerts

    # ------------------------------------------------------------------
    # 2. Leveraging Credit for Income (OPM)
    # ------------------------------------------------------------------

    def get_opm_strategies(self, credit_score: int) -> list[dict]:
        """
        Return OPM strategies suitable for the user's credit score (PRO+).
        """
        self._require_feature(FEATURE_OPM_STRATEGIES)
        if not (300 <= credit_score <= 850):
            raise FinancialLiteracyBotError("credit_score must be between 300 and 850.")
        eligible = [
            s for s in OPM_STRATEGIES
            if credit_score >= s["required_credit_score"]
        ]
        return eligible

    # ------------------------------------------------------------------
    # 3. Investment Calculators
    # ------------------------------------------------------------------

    def calculate_roi(
        self,
        investment_type: InvestmentType,
        principal: float,
        annual_return_pct: float,
        years: int,
        credit_rate_pct: float = 0.0,
    ) -> dict:
        """
        Calculate ROI for an investment, optionally factoring in credit borrowing cost (FREE+).

        Parameters
        ----------
        principal : float
            Amount invested (USD).
        annual_return_pct : float
            Expected annual return percentage (e.g. 8.0 for 8%).
        years : int
            Investment horizon in years.
        credit_rate_pct : float
            Annual interest rate on borrowed capital (0 = own money).

        Returns
        -------
        dict with roi_pct, net_profit, and total_value.
        """
        self._require_feature(FEATURE_INVESTMENT_CALCULATOR)

        tier_limit = self.config.max_investment_calculators
        if tier_limit is not None and self._calc_counter >= tier_limit:
            raise FinancialLiteracyBotTierError(
                f"Calculation limit of {tier_limit} reached for the {self.config.name} tier."
            )
        if principal <= 0:
            raise FinancialLiteracyBotError("principal must be positive.")
        if years < 1:
            raise FinancialLiteracyBotError("years must be at least 1.")

        # Compound growth
        total_value = principal * ((1 + annual_return_pct / 100) ** years)
        # Total interest cost on borrowed capital
        total_interest_cost = principal * (credit_rate_pct / 100) * years
        net_profit = total_value - principal - total_interest_cost
        roi_pct = (net_profit / principal) * 100

        self._calc_counter += 1
        calc_id = f"calc_{uuid.uuid4().hex[:8]}"
        calc = InvestmentCalculation(
            calc_id=calc_id,
            investment_type=investment_type,
            principal=principal,
            annual_return_pct=annual_return_pct,
            years=years,
            credit_rate_pct=credit_rate_pct,
            result_roi_pct=round(roi_pct, 2),
            result_net_profit=round(net_profit, 2),
            result_total_value=round(total_value, 2),
        )
        self._calculations.append(calc)

        return {
            "calc_id": calc_id,
            "investment_type": investment_type.value,
            "principal": principal,
            "annual_return_pct": annual_return_pct,
            "years": years,
            "credit_rate_pct": credit_rate_pct,
            "total_value": calc.result_total_value,
            "net_profit": calc.result_net_profit,
            "roi_pct": calc.result_roi_pct,
        }

    def get_calculations(self) -> list[dict]:
        """Return all stored investment calculations (FREE+)."""
        return [
            {
                "calc_id": c.calc_id,
                "investment_type": c.investment_type.value,
                "principal": c.principal,
                "roi_pct": c.result_roi_pct,
                "net_profit": c.result_net_profit,
                "created_at": c.created_at,
            }
            for c in self._calculations
        ]

    # ------------------------------------------------------------------
    # 4. Bank / Credit Bureau Integration (mock)
    # ------------------------------------------------------------------

    def fetch_credit_score(self, user_identifier: str) -> dict:
        """
        Mock fetch of a credit score via credit bureau API (PRO+).
        In production, this calls Equifax / Experian / TransUnion or Plaid.
        """
        self._require_feature(FEATURE_BANK_INTEGRATION)
        if not user_identifier:
            raise FinancialLiteracyBotError("user_identifier must not be empty.")
        # Mock deterministic score based on identifier hash
        mock_score = 580 + (hash(user_identifier) % 271)
        mock_score = max(300, min(850, mock_score))
        return {
            "user_identifier": user_identifier,
            "credit_score": mock_score,
            "bureau": "Equifax (mock)",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def match_financial_products(self, credit_score: int) -> list[dict]:
        """
        Match the user's credit score to suitable financial products (PRO+).
        """
        self._require_feature(FEATURE_PRODUCT_MATCHING)
        if not (300 <= credit_score <= 850):
            raise FinancialLiteracyBotError("credit_score must be between 300 and 850.")
        matched = [
            {
                "product_id": p.product_id,
                "name": p.name,
                "product_type": p.product_type,
                "apr_pct": p.apr_pct,
                "promotional_apr_pct": p.promotional_apr_pct,
                "promotional_months": p.promotional_months,
                "description": p.description,
            }
            for p in PRODUCT_CATALOGUE
            if credit_score >= p.credit_score_min
        ]
        return matched

    # ------------------------------------------------------------------
    # 5. Automated Reminders
    # ------------------------------------------------------------------

    def create_reminder(
        self,
        reminder_type: ReminderType,
        message: str,
        due_date: Optional[str] = None,
    ) -> dict:
        """Create an automated reminder (PRO+)."""
        self._require_feature(FEATURE_AUTOMATED_REMINDERS)
        reminder_id = f"rem_{uuid.uuid4().hex[:8]}"
        reminder = Reminder(
            reminder_id=reminder_id,
            user_id=self.user_id,
            reminder_type=reminder_type,
            message=message,
            due_date=due_date,
        )
        self._reminders.append(reminder)
        return {
            "reminder_id": reminder_id,
            "type": reminder_type.value,
            "message": message,
            "due_date": due_date,
            "sent": False,
        }

    def send_reminders(self) -> list[dict]:
        """Mark all unsent reminders as sent and return them (PRO+)."""
        self._require_feature(FEATURE_AUTOMATED_REMINDERS)
        sent = []
        for rem in self._reminders:
            if not rem.sent:
                rem.sent = True
                sent.append({
                    "reminder_id": rem.reminder_id,
                    "type": rem.reminder_type.value,
                    "message": rem.message,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                })
        return sent

    def get_reminders(self, unsent_only: bool = False) -> list[dict]:
        """Return stored reminders (PRO+)."""
        self._require_feature(FEATURE_AUTOMATED_REMINDERS)
        items = self._reminders if not unsent_only else [r for r in self._reminders if not r.sent]
        return [
            {
                "reminder_id": r.reminder_id,
                "type": r.reminder_type.value,
                "message": r.message,
                "due_date": r.due_date,
                "sent": r.sent,
            }
            for r in items
        ]

    # ------------------------------------------------------------------
    # 6. Education Module
    # ------------------------------------------------------------------

    def get_education_modules(
        self,
        level: Optional[EducationLevel] = None,
        topic: Optional[str] = None,
    ) -> list[dict]:
        """
        Return available education modules (FREE: up to 3; PRO: up to 20; ENTERPRISE: all).
        Optionally filter by level or topic.
        """
        self._require_feature(FEATURE_CREDIT_TIPS)
        filtered = EDUCATION_CATALOGUE
        if level is not None:
            filtered = [m for m in filtered if m.level == level]
        if topic is not None:
            filtered = [m for m in filtered if topic.lower() in m.topic.lower()]

        limit = self.config.max_education_modules
        if limit is not None:
            filtered = filtered[:limit]

        return [
            {
                "module_id": m.module_id,
                "title": m.title,
                "level": m.level.value,
                "topic": m.topic,
                "content_summary": m.content_summary,
                "estimated_minutes": m.estimated_minutes,
                "tags": m.tags,
            }
            for m in filtered
        ]

    def complete_module(self, module_id: str) -> dict:
        """Mark an education module as completed (PRO+)."""
        self._require_feature(FEATURE_EDUCATION_PATHS)
        module_ids = [m.module_id for m in EDUCATION_CATALOGUE]
        if module_id not in module_ids:
            raise FinancialLiteracyBotNotFoundError(f"Module '{module_id}' not found.")
        if module_id not in self._completed_modules:
            self._completed_modules.append(module_id)
        total = len(EDUCATION_CATALOGUE)
        completed = len(self._completed_modules)
        return {
            "module_id": module_id,
            "completed": True,
            "progress_pct": round(completed / total * 100, 1),
            "modules_completed": completed,
            "modules_total": total,
        }

    def get_education_path(self) -> dict:
        """
        Return a personalised education path based on completed modules (PRO+).
        """
        self._require_feature(FEATURE_EDUCATION_PATHS)
        completed_ids = set(self._completed_modules)
        remaining = [
            {
                "module_id": m.module_id,
                "title": m.title,
                "level": m.level.value,
                "estimated_minutes": m.estimated_minutes,
            }
            for m in EDUCATION_CATALOGUE
            if m.module_id not in completed_ids
        ]
        # Sort by level: beginner → intermediate → advanced
        level_order = {
            EducationLevel.BEGINNER: 0,
            EducationLevel.INTERMEDIATE: 1,
            EducationLevel.ADVANCED: 2,
        }
        remaining_sorted = sorted(
            remaining,
            key=lambda x: level_order.get(
                EducationLevel(x["level"]), 99
            ),
        )
        return {
            "completed_modules": list(completed_ids),
            "next_modules": remaining_sorted[:5],
            "total_remaining": len(remaining),
        }

    # ------------------------------------------------------------------
    # 7. Community Platform
    # ------------------------------------------------------------------

    def get_community_posts(self, tag: Optional[str] = None) -> list[dict]:
        """Return community posts (FREE: read-only)."""
        self._require_feature(FEATURE_COMMUNITY_READ)
        posts = self._community_posts
        if tag:
            posts = [p for p in posts if tag.lower() in [t.lower() for t in p.tags]]
        return [
            {
                "post_id": p.post_id,
                "user_id": p.user_id,
                "title": p.title,
                "body": p.body,
                "tags": p.tags,
                "upvotes": p.upvotes,
                "reply_count": len(p.replies),
                "created_at": p.created_at,
            }
            for p in posts
        ]

    def create_community_post(
        self, title: str, body: str, tags: Optional[list] = None
    ) -> dict:
        """Create a community post (ENTERPRISE+)."""
        self._require_feature(FEATURE_COMMUNITY_POST)
        if not title.strip():
            raise FinancialLiteracyBotError("Post title must not be empty.")
        if not body.strip():
            raise FinancialLiteracyBotError("Post body must not be empty.")
        post_id = f"post_{uuid.uuid4().hex[:8]}"
        post = CommunityPost(
            post_id=post_id,
            user_id=self.user_id,
            title=title.strip(),
            body=body.strip(),
            tags=tags or [],
        )
        self._community_posts.append(post)
        return {
            "post_id": post_id,
            "title": post.title,
            "body": post.body,
            "tags": post.tags,
            "upvotes": 0,
            "reply_count": 0,
            "created_at": post.created_at,
        }

    def reply_to_post(self, post_id: str, reply_body: str) -> dict:
        """Add a reply to a community post (ENTERPRISE+)."""
        self._require_feature(FEATURE_COMMUNITY_POST)
        post = next((p for p in self._community_posts if p.post_id == post_id), None)
        if post is None:
            raise FinancialLiteracyBotNotFoundError(f"Post '{post_id}' not found.")
        if not reply_body.strip():
            raise FinancialLiteracyBotError("Reply body must not be empty.")
        reply = {
            "reply_id": f"reply_{uuid.uuid4().hex[:8]}",
            "user_id": self.user_id,
            "body": reply_body.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        post.replies.append(reply)
        return reply

    def upvote_post(self, post_id: str) -> dict:
        """Upvote a community post (FREE read → ENTERPRISE write; upvote counts as read)."""
        self._require_feature(FEATURE_COMMUNITY_READ)
        post = next((p for p in self._community_posts if p.post_id == post_id), None)
        if post is None:
            raise FinancialLiteracyBotNotFoundError(f"Post '{post_id}' not found.")
        post.upvotes += 1
        return {"post_id": post_id, "upvotes": post.upvotes}

    # ------------------------------------------------------------------
    # 8. Analytics (ENTERPRISE+)
    # ------------------------------------------------------------------

    def get_analytics(self) -> dict:
        """Return usage analytics (ENTERPRISE+)."""
        self._require_feature(FEATURE_ANALYTICS)
        return {
            "total_calculations": len(self._calculations),
            "total_reminders": len(self._reminders),
            "sent_reminders": sum(1 for r in self._reminders if r.sent),
            "completed_modules": len(self._completed_modules),
            "community_posts": len(self._community_posts),
            "credit_profiles": len(self._credit_profiles),
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Chat / process interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Natural-language routing for the bot."""
        msg = message.lower()

        if any(kw in msg for kw in ("tip", "improve credit", "credit score", "credit advice")):
            tips = self.get_credit_tips(3)
            return {"message": "Here are 3 credit tips for you.", "data": tips}

        if any(kw in msg for kw in ("opm", "leverage", "other people", "invest with credit")):
            if not self.config.has_feature(FEATURE_OPM_STRATEGIES):
                return {
                    "message": (
                        "OPM strategies are available on the Pro tier and above. "
                        "Upgrade to unlock!"
                    ),
                    "data": None,
                }
            strategies = self.get_opm_strategies(700)
            return {
                "message": f"{len(strategies)} OPM strategies found for a 700+ credit score.",
                "data": strategies,
            }

        if any(kw in msg for kw in ("calculator", "roi", "return", "calculate")):
            return {
                "message": (
                    "Use calculate_roi(investment_type, principal, annual_return_pct, years) "
                    "to compute your ROI."
                ),
                "data": None,
            }

        if any(kw in msg for kw in ("education", "learn", "module", "course")):
            modules = self.get_education_modules()
            return {
                "message": f"{len(modules)} education module(s) available.",
                "data": modules,
            }

        if any(kw in msg for kw in ("community", "post", "story", "peer")):
            posts = self.get_community_posts()
            return {
                "message": f"{len(posts)} community post(s) available.",
                "data": posts,
            }

        return {
            "message": (
                "DreamCo Financial Literacy Bot online. "
                f"Tier: {self.tier.value}. "
                "Ask about credit tips, OPM strategies, ROI calculators, "
                "education modules, or community posts."
            ),
            "data": None,
        }

    def get_summary(self) -> dict:
        """Return a high-level summary of the bot instance."""
        return {
            "tier": self.tier.value,
            "user_id": self.user_id,
            "credit_profiles": len(self._credit_profiles),
            "calculations_run": len(self._calculations),
            "reminders_created": len(self._reminders),
            "modules_completed": len(self._completed_modules),
            "community_posts": len(self._community_posts),
        }


# ---------------------------------------------------------------------------
# Module-level run() helper
# ---------------------------------------------------------------------------

def run(tier: Tier = Tier.FREE) -> None:  # pragma: no cover
    """Quick demo of the Financial Literacy Bot."""
    bot = FinancialLiteracyBot(tier=tier)
    print(f"=== DreamCo Financial Literacy Bot [{tier.value.upper()}] ===")
    print("\n-- Credit Tips --")
    for tip in bot.get_credit_tips(3):
        print(f"  • {tip}")

    print("\n-- Investment ROI Calculator --")
    result = bot.calculate_roi(
        InvestmentType.REAL_ESTATE,
        principal=10000,
        annual_return_pct=8,
        years=5,
        credit_rate_pct=3,
    )
    print(f"  Total value: ${result['total_value']:,.2f}")
    print(f"  Net profit:  ${result['net_profit']:,.2f}")
    print(f"  ROI:         {result['roi_pct']}%")

    print("\n-- Education Modules --")
    for mod in bot.get_education_modules():
        print(f"  [{mod['level']}] {mod['title']} ({mod['estimated_minutes']} min)")

    print("\n-- Summary --")
    for k, v in bot.get_summary().items():
        print(f"  {k}: {v}")


if __name__ == "__main__":  # pragma: no cover
    run(Tier.PRO)
