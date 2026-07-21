"""HomeDashboardScreen — main dashboard showing profit summary and top deals."""


class HomeDashboardScreen:
    SCREEN_ID = "home_dashboard"

    def __init__(self, user_tier="FREE", daily_profit=0.0, top_deals=None, alerts=None):
        self.user_tier = user_tier
        self.daily_profit = daily_profit
        self.top_deals = top_deals or []
        self.alerts = alerts or []

    def render(self) -> str:
        lines = [
            "=== DreamCo Money OS — Home Dashboard ===",
            f"Tier: {self.user_tier}",
            f"Estimated Daily Profit: ${self.daily_profit:.2f}",
            f"Active Alerts: {len(self.alerts)}",
            f"Top Deals: {len(self.top_deals)}",
        ]
        if self.top_deals:
            lines.append("Top Deals:")
            for d in self.top_deals[:3]:
                lines.append(f"  • {d.get('name', 'Deal')} — ${d.get('profit', 0):.2f} profit")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "user_tier": self.user_tier,
            "daily_profit": self.daily_profit,
            "top_deals": self.top_deals,
            "alerts": self.alerts,
        }

    @classmethod
    def demo(cls) -> "HomeDashboardScreen":
        return cls(
            user_tier="PRO",
            daily_profit=127.50,
            top_deals=[
                {"name": "PS5 Clearance", "profit": 85.0},
                {"name": "Dyson Refurb", "profit": 42.5},
            ],
            alerts=[{"urgency": "HIGH", "message": "PS5 deal expiring soon"}],
        )
