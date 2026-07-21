"""EarningsScreen — earnings summary across all revenue streams."""


class EarningsScreen:
    SCREEN_ID = "earnings"

    def __init__(self, daily=0.0, weekly=0.0, monthly=0.0, breakdown=None):
        self.daily = daily
        self.weekly = weekly
        self.monthly = monthly
        self.breakdown = breakdown or {}

    def render(self) -> str:
        lines = [
            "=== DreamCo — Earnings Dashboard ===",
            f"Today:    ${self.daily:.2f}",
            f"This Week: ${self.weekly:.2f}",
            f"This Month: ${self.monthly:.2f}",
        ]
        if self.breakdown:
            lines.append("Breakdown:")
            for source, amount in self.breakdown.items():
                lines.append(f"  {source}: ${amount:.2f}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "daily": self.daily,
            "weekly": self.weekly,
            "monthly": self.monthly,
            "breakdown": self.breakdown,
        }

    @classmethod
    def demo(cls) -> "EarningsScreen":
        return cls(
            daily=127.50,
            weekly=892.75,
            monthly=3210.00,
            breakdown={"deals": 580.0, "flips": 215.0, "cashback": 45.0, "coupons": 62.0},
        )
