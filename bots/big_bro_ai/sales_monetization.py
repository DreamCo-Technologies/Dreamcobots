"""
Big Bro AI — Sales & Monetization Engine

Tracks income streams, pricing logic, upsells, payment methods, and
compound interest / day-trading intelligence.  Every money concept is
explained in plain language so users understand HOW money works, not
just THAT it works.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Income stream types
# ---------------------------------------------------------------------------

class IncomeStreamType(Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    SERVICE = "service"
    DIGITAL_PRODUCT = "digital_product"
    AFFILIATE = "affiliate"
    SAAS = "saas"
    CONSULTING = "consulting"
    WHITE_LABEL = "white_label"
    FRANCHISE_FEE = "franchise_fee"
    CATALOG_COMMISSION = "catalog_commission"
    DAY_TRADING = "day_trading"
    INVESTMENT = "investment"


# ---------------------------------------------------------------------------
# Payment methods
# ---------------------------------------------------------------------------

PAYMENT_METHODS: list[str] = [
    "credit_card",
    "debit_card",
    "apple_pay",
    "google_pay",
    "paypal",
    "stripe",
    "venmo",
    "cashapp",
    "zelle",
    "crypto",
    "bank_transfer",
    "payment_link",
]


# ---------------------------------------------------------------------------
# Income stream
# ---------------------------------------------------------------------------

@dataclass
class IncomeStream:
    """
    A single revenue-generating income stream.

    Attributes
    ----------
    stream_id : str
        Unique identifier.
    name : str
        Display name.
    stream_type : IncomeStreamType
        Revenue model type.
    price_usd : float
        Base price per unit / month.
    is_recurring : bool
        Whether this stream generates recurring revenue.
    active_customers : int
        Current paying customers.
    monthly_revenue_usd : float
        Derived monthly revenue.
    upsell_opportunity : str
        Description of the next-level upsell.
    explanation : str
        Big Bro's plain-language explanation of why this works.
    """

    stream_id: str
    name: str
    stream_type: IncomeStreamType
    price_usd: float
    is_recurring: bool = False
    active_customers: int = 0
    upsell_opportunity: str = ""
    explanation: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def monthly_revenue_usd(self) -> float:
        """Monthly revenue from this stream."""
        if self.is_recurring:
            return round(self.price_usd * self.active_customers, 2)
        return 0.0

    def add_customers(self, count: int) -> None:
        """Add *count* customers to this stream."""
        self.active_customers += count

    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "name": self.name,
            "stream_type": self.stream_type.value,
            "price_usd": self.price_usd,
            "is_recurring": self.is_recurring,
            "active_customers": self.active_customers,
            "monthly_revenue_usd": self.monthly_revenue_usd,
            "upsell_opportunity": self.upsell_opportunity,
            "explanation": self.explanation,
        }


# ---------------------------------------------------------------------------
# Compound interest calculator
# ---------------------------------------------------------------------------

def compound_interest(
    principal: float,
    rate: float,
    periods: int,
    compounds_per_period: int = 12,
) -> dict:
    """
    Calculate compound interest.

    Parameters
    ----------
    principal : float
        Initial investment amount.
    rate : float
        Annual interest rate (e.g., 0.07 for 7 %).
    periods : int
        Number of years.
    compounds_per_period : int
        Compounding frequency per year (default: 12 = monthly).

    Returns
    -------
    dict
        final_amount, total_interest, growth_multiplier
    """
    n = compounds_per_period
    final = principal * (1 + rate / n) ** (n * periods)
    return {
        "principal": round(principal, 2),
        "rate_annual_pct": round(rate * 100, 2),
        "periods_years": periods,
        "final_amount": round(final, 2),
        "total_interest": round(final - principal, 2),
        "growth_multiplier": round(final / principal, 4) if principal > 0 else 0,
        "explanation": (
            f"${principal:,.2f} invested at {rate*100:.1f}% annual rate "
            f"compounded monthly for {periods} years grows to ${final:,.2f}. "
            "That's why starting early matters — time does the heavy lifting."
        ),
    }


# ---------------------------------------------------------------------------
# Sales & Monetization Engine
# ---------------------------------------------------------------------------

class SalesMonetizationError(Exception):
    """Raised when a sales/monetization operation fails."""


class SalesMonetizationEngine:
    """
    Manages income streams, pricing, upsells, and financial intelligence
    for Big Bro AI.
    """

    def __init__(self) -> None:
        self._streams: dict[str, IncomeStream] = {}
        self._stream_counter: int = 0
        self._transactions: list[dict] = []
        self._seed_streams()

    # ------------------------------------------------------------------
    # Seed built-in income streams
    # ------------------------------------------------------------------

    def _seed_streams(self) -> None:
        seeds = [
            {
                "name": "Big Bro Pro Subscription",
                "stream_type": IncomeStreamType.SUBSCRIPTION,
                "price_usd": 49.0,
                "is_recurring": True,
                "upsell_opportunity": "Upgrade to Enterprise for franchise + white-label access.",
                "explanation": (
                    "Monthly subscriptions compound automatically. "
                    "100 subscribers = $4,900/month without lifting a finger."
                ),
            },
            {
                "name": "Bot Factory Access",
                "stream_type": IncomeStreamType.SAAS,
                "price_usd": 29.0,
                "is_recurring": True,
                "upsell_opportunity": "Sell custom bots to clients for $500–$5,000 each.",
                "explanation": (
                    "You build the tool once. Every user who needs bots pays you monthly."
                ),
            },
            {
                "name": "DreamCo Catalog Commission",
                "stream_type": IncomeStreamType.CATALOG_COMMISSION,
                "price_usd": 15.0,
                "is_recurring": False,
                "upsell_opportunity": "Open a franchise to earn recurring territory fees.",
                "explanation": (
                    "Every order placed through your catalog earns you a commission. "
                    "Build the catalog once. Orders keep coming."
                ),
            },
            {
                "name": "Roast Bot One-Time License",
                "stream_type": IncomeStreamType.DIGITAL_PRODUCT,
                "price_usd": 97.0,
                "is_recurring": False,
                "upsell_opportunity": "Upsell to monthly support + updates for $19/mo.",
                "explanation": (
                    "One-time digital products create an initial revenue spike. "
                    "Convert buyers into subscribers for recurring income."
                ),
            },
        ]
        for s in seeds:
            self._stream_counter += 1
            stream_id = f"stm_{self._stream_counter:04d}"
            stream = IncomeStream(
                stream_id=stream_id,
                name=s["name"],
                stream_type=s["stream_type"],
                price_usd=s["price_usd"],
                is_recurring=s["is_recurring"],
                upsell_opportunity=s.get("upsell_opportunity", ""),
                explanation=s.get("explanation", ""),
            )
            self._streams[stream_id] = stream

    # ------------------------------------------------------------------
    # Stream management
    # ------------------------------------------------------------------

    def create_stream(
        self,
        name: str,
        stream_type: IncomeStreamType,
        price_usd: float,
        is_recurring: bool = False,
        upsell_opportunity: str = "",
        explanation: str = "",
    ) -> IncomeStream:
        """Create and register a new income stream."""
        self._stream_counter += 1
        stream_id = f"stm_{self._stream_counter:04d}"
        stream = IncomeStream(
            stream_id=stream_id,
            name=name,
            stream_type=stream_type,
            price_usd=price_usd,
            is_recurring=is_recurring,
            upsell_opportunity=upsell_opportunity,
            explanation=explanation,
        )
        self._streams[stream_id] = stream
        return stream

    def get_stream(self, stream_id: str) -> Optional[IncomeStream]:
        return self._streams.get(stream_id)

    def list_streams(
        self, stream_type: Optional[IncomeStreamType] = None
    ) -> list[IncomeStream]:
        streams = list(self._streams.values())
        if stream_type is not None:
            streams = [s for s in streams if s.stream_type == stream_type]
        return streams

    # ------------------------------------------------------------------
    # Revenue tracking
    # ------------------------------------------------------------------

    def record_transaction(
        self, stream_id: str, amount: float, customer_id: str = ""
    ) -> dict:
        """Record a transaction for an income stream."""
        stream = self._streams.get(stream_id)
        if stream is None:
            raise SalesMonetizationError(f"Stream '{stream_id}' not found.")
        tx = {
            "stream_id": stream_id,
            "stream_name": stream.name,
            "amount": amount,
            "customer_id": customer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._transactions.append(tx)
        return tx

    def total_revenue(self) -> float:
        return round(sum(t["amount"] for t in self._transactions), 2)

    def monthly_recurring_revenue(self) -> float:
        """Sum MRR across all recurring streams."""
        return round(
            sum(s.monthly_revenue_usd for s in self._streams.values() if s.is_recurring),
            2,
        )

    # ------------------------------------------------------------------
    # Compound interest
    # ------------------------------------------------------------------

    def calculate_compound(
        self,
        principal: float,
        rate: float,
        periods: int,
        compounds_per_period: int = 12,
    ) -> dict:
        """Delegate to the compound_interest function."""
        return compound_interest(principal, rate, periods, compounds_per_period)

    # ------------------------------------------------------------------
    # Money goal projection
    # ------------------------------------------------------------------

    def project_goal(
        self, daily_users: int, price_per_user: float
    ) -> dict:
        """
        Project revenue math the way Big Bro teaches it.

        Parameters
        ----------
        daily_users : int
            New paying users per day.
        price_per_user : float
            Price per user per month.
        """
        daily_revenue = daily_users * price_per_user
        monthly_revenue = daily_revenue * 30
        weekly_revenue = daily_revenue * 7
        return {
            "daily_users": daily_users,
            "price_per_user_usd": price_per_user,
            "daily_revenue_usd": round(daily_revenue, 2),
            "weekly_revenue_usd": round(weekly_revenue, 2),
            "monthly_revenue_usd": round(monthly_revenue, 2),
            "explanation": (
                f"If {daily_users} users pay ${price_per_user}/month, "
                f"that's ${daily_revenue:.0f}/day, "
                f"${weekly_revenue:.0f}/week, "
                f"${monthly_revenue:.0f}/month. "
                "It's math, not motivation."
            ),
        }

    # ------------------------------------------------------------------
    # Dashboard summary
    # ------------------------------------------------------------------

    def revenue_dashboard(self) -> dict:
        """Return a full revenue summary."""
        streams = list(self._streams.values())
        by_type: dict[str, int] = {}
        for s in streams:
            by_type[s.stream_type.value] = by_type.get(s.stream_type.value, 0) + 1
        return {
            "total_streams": len(streams),
            "total_transactions": len(self._transactions),
            "total_revenue_usd": self.total_revenue(),
            "monthly_recurring_revenue_usd": self.monthly_recurring_revenue(),
            "streams_by_type": by_type,
            "payment_methods_supported": PAYMENT_METHODS,
        }
