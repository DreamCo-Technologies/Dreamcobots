"""
DreamCo Money OS — Home Dashboard Screen

FlutterFlow-style screen definition for real-time profit tracking.
Displays total earnings, active bots, pending cashback, and revenue trend.
"""

from datetime import datetime


class HomeDashboardScreen:
    """
    Main dashboard showing real-time profit tracking across all DreamCo bots.

    Fields
    ------
    total_earnings       : Cumulative earnings in USD.
    pending_cashback     : Cashback awaiting confirmation.
    active_bots          : Number of bots currently running.
    todays_revenue       : Revenue earned today.
    weekly_revenue       : Revenue earned this week.
    monthly_revenue      : Revenue earned this month.
    top_opportunity      : Highest-scoring opportunity right now.
    alerts_count         : Number of unread HIGH alerts.
    revenue_trend        : List of daily revenue values for chart.
    last_updated         : ISO timestamp of last data refresh.
    """

    SCREEN_NAME = "HomeDashboardScreen"
    ROUTE = "/dashboard/home"

    def __init__(
        self,
        total_earnings: float = 0.0,
        pending_cashback: float = 0.0,
        active_bots: int = 0,
        todays_revenue: float = 0.0,
        weekly_revenue: float = 0.0,
        monthly_revenue: float = 0.0,
        top_opportunity: dict = None,
        alerts_count: int = 0,
        revenue_trend: list = None,
    ):
        self.total_earnings = total_earnings
        self.pending_cashback = pending_cashback
        self.active_bots = active_bots
        self.todays_revenue = todays_revenue
        self.weekly_revenue = weekly_revenue
        self.monthly_revenue = monthly_revenue
        self.top_opportunity = top_opportunity or {}
        self.alerts_count = alerts_count
        self.revenue_trend = revenue_trend or []
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        """Return the screen's UI data model for FlutterFlow rendering."""
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "header": {"title": "DreamCo Money OS", "subtitle": "Your Personal Profit Machine"},
                "earnings_card": {
                    "total_earnings": f"${self.total_earnings:,.2f}",
                    "pending_cashback": f"${self.pending_cashback:,.2f}",
                    "color": "green",
                },
                "revenue_summary": {
                    "today": f"${self.todays_revenue:,.2f}",
                    "week": f"${self.weekly_revenue:,.2f}",
                    "month": f"${self.monthly_revenue:,.2f}",
                },
                "bot_status": {
                    "active_bots": self.active_bots,
                    "label": f"{self.active_bots} bot(s) running",
                },
                "top_opportunity": self.top_opportunity,
                "alerts_badge": {"count": self.alerts_count, "color": "red" if self.alerts_count > 0 else "grey"},
                "revenue_chart": {"data": self.revenue_trend, "type": "line"},
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        """Serialise all screen state to a plain dict."""
        return {
            "screen": self.SCREEN_NAME,
            "total_earnings": self.total_earnings,
            "pending_cashback": self.pending_cashback,
            "active_bots": self.active_bots,
            "todays_revenue": self.todays_revenue,
            "weekly_revenue": self.weekly_revenue,
            "monthly_revenue": self.monthly_revenue,
            "top_opportunity": self.top_opportunity,
            "alerts_count": self.alerts_count,
            "revenue_trend": self.revenue_trend,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "HomeDashboardScreen":
        """Return a pre-populated demo instance."""
        return cls(
            total_earnings=3_247.85,
            pending_cashback=42.10,
            active_bots=5,
            todays_revenue=128.50,
            weekly_revenue=847.30,
            monthly_revenue=3_247.85,
            top_opportunity={"type": "deal", "title": "Electronics Deal #1 at amazon", "savings": 75.00},
            alerts_count=3,
            revenue_trend=[45, 82, 60, 128, 97, 115, 128],
        )
