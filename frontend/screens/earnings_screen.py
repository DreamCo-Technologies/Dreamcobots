"""
DreamCo Money OS — Earnings Screen

FlutterFlow-style screen showing pending, completed, referral, and
premium subscription earnings.
"""

from datetime import datetime


class EarningsScreen:
    """
    Detailed earnings breakdown: pending, completed, referrals, and premium.

    Fields
    ------
    pending_earnings     : Earnings awaiting confirmation/payout.
    completed_earnings   : Confirmed and paid-out earnings.
    referral_earnings    : Earnings from user referrals.
    premium_revenue      : Revenue from premium subscription.
    total_earnings       : Sum of all earning categories.
    payout_history       : List of past payouts.
    upcoming_payouts     : Scheduled upcoming payments.
    subscription_tier    : 'free' | 'pro' | 'enterprise'.
    last_updated         : ISO timestamp.
    """

    SCREEN_NAME = "EarningsScreen"
    ROUTE = "/earnings"

    def __init__(
        self,
        pending_earnings: float = 0.0,
        completed_earnings: float = 0.0,
        referral_earnings: float = 0.0,
        premium_revenue: float = 0.0,
        payout_history: list = None,
        upcoming_payouts: list = None,
        subscription_tier: str = "free",
    ):
        self.pending_earnings = pending_earnings
        self.completed_earnings = completed_earnings
        self.referral_earnings = referral_earnings
        self.premium_revenue = premium_revenue
        self.total_earnings = round(
            pending_earnings + completed_earnings + referral_earnings + premium_revenue, 2
        )
        self.payout_history = payout_history or []
        self.upcoming_payouts = upcoming_payouts or []
        self.subscription_tier = subscription_tier
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "total_card": {
                    "total": f"${self.total_earnings:,.2f}",
                    "label": "Total Earnings",
                    "color": "green",
                },
                "breakdown": {
                    "pending": {"label": "Pending", "value": f"${self.pending_earnings:,.2f}", "color": "orange"},
                    "completed": {"label": "Completed", "value": f"${self.completed_earnings:,.2f}", "color": "green"},
                    "referrals": {"label": "Referrals", "value": f"${self.referral_earnings:,.2f}", "color": "blue"},
                    "premium": {"label": "Premium", "value": f"${self.premium_revenue:,.2f}", "color": "purple"},
                },
                "subscription_badge": {
                    "tier": self.subscription_tier.upper(),
                    "color": {"free": "grey", "pro": "blue", "enterprise": "gold"}.get(self.subscription_tier, "grey"),
                },
                "payout_history": {"items": self.payout_history, "count": len(self.payout_history)},
                "upcoming_payouts": {"items": self.upcoming_payouts, "count": len(self.upcoming_payouts)},
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "pending_earnings": self.pending_earnings,
            "completed_earnings": self.completed_earnings,
            "referral_earnings": self.referral_earnings,
            "premium_revenue": self.premium_revenue,
            "total_earnings": self.total_earnings,
            "payout_history": self.payout_history,
            "upcoming_payouts": self.upcoming_payouts,
            "subscription_tier": self.subscription_tier,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "EarningsScreen":
        return cls(
            pending_earnings=127.50,
            completed_earnings=2_890.35,
            referral_earnings=180.00,
            premium_revenue=99.00,
            payout_history=[
                {"date": "2025-06-01", "amount": 450.00, "method": "PayPal", "status": "completed"},
                {"date": "2025-05-15", "amount": 320.75, "method": "Direct Deposit", "status": "completed"},
            ],
            upcoming_payouts=[
                {"date": "2025-07-01", "amount": 127.50, "method": "PayPal", "status": "pending"},
            ],
            subscription_tier="pro",
        )
