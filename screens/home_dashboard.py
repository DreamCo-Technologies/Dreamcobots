"""
DreamCo — Home Dashboard Screen

The first screen a user sees after login. Summarizes their total balance,
daily earnings, active bots, and an overview of their Wealth Hubs.

Fields
------
- Total Balance (USD + DreamCoin)
- Daily Earnings
- Active Bots count + status indicators
- Wealth Hub cards (treasury, members, recent activity)
- Quick-action buttons (Deposit, Run Bots, View Hub)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HubCard:
    """A compact Wealth Hub card shown on the home dashboard."""
    hub_id: str
    name: str
    treasury_usd: float
    member_count: int
    active_bots: int
    last_dividend_usd: float = 0.0
    ownership_pct: float = 0.0


@dataclass
class EarningsSummary:
    """Earnings summary widget."""
    today_usd: float = 0.0
    this_week_usd: float = 0.0
    this_month_usd: float = 0.0
    all_time_usd: float = 0.0


class HomeDashboardScreen:
    """
    Home Dashboard Screen for the DreamCo platform.

    Renders a top-level overview of the user's financial activity:
    total portfolio balance, recent earnings, active bot count, and
    Wealth Hub cards.

    Usage
    -----
        screen = HomeDashboardScreen(
            user_name="Alice",
            total_balance_usd=12500.00,
            dreamcoin_balance=450.0,
            earnings=EarningsSummary(today_usd=42.50, this_month_usd=1200.0),
        )
        screen.add_hub(HubCard("hub-1", "Family Circle", 8500.0, 5, 3, 120.0, 35.0))
        print(screen.render())
    """

    SCREEN_NAME = "Home Dashboard"
    ROUTE = "/"

    def __init__(
        self,
        user_name: str = "Member",
        total_balance_usd: float = 0.0,
        dreamcoin_balance: float = 0.0,
        earnings: Optional[EarningsSummary] = None,
        active_bot_count: int = 0,
        kyc_verified: bool = False,
    ) -> None:
        self.user_name = user_name
        self.total_balance_usd = total_balance_usd
        self.dreamcoin_balance = dreamcoin_balance
        self.earnings = earnings or EarningsSummary()
        self.active_bot_count = active_bot_count
        self.kyc_verified = kyc_verified
        self._hubs: list[HubCard] = []

    def add_hub(self, hub: HubCard) -> None:
        """Add a Wealth Hub card to the dashboard."""
        self._hubs.append(hub)

    def hub_count(self) -> int:
        return len(self._hubs)

    def render(self) -> str:
        """Return a plain-text demo rendering of the Home Dashboard."""
        kyc_badge = "✅ KYC Verified" if self.kyc_verified else "⚠️ KYC Pending"
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║          DREAMCO — HOME DASHBOARD                    ║",
            "╚══════════════════════════════════════════════════════╝",
            f"  Welcome back, {self.user_name}!   {kyc_badge}",
            "",
            "  ┌─────────────────────────────────────────────────┐",
            "  │  TOTAL BALANCE                                   │",
            f"  │  ${self.total_balance_usd:,.2f} USD                               │",
            f"  │  {self.dreamcoin_balance:,.0f} DreamCoin                           │",
            "  └─────────────────────────────────────────────────┘",
            "",
            "  EARNINGS",
            f"  Today:      ${self.earnings.today_usd:,.2f}",
            f"  This Week:  ${self.earnings.this_week_usd:,.2f}",
            f"  This Month: ${self.earnings.this_month_usd:,.2f}",
            f"  All Time:   ${self.earnings.all_time_usd:,.2f}",
            "",
            f"  🤖 Active Bots: {self.active_bot_count}",
            "",
            "  WEALTH HUBS",
        ]
        if not self._hubs:
            lines.append("  No Wealth Hubs yet. Create or join one to start!")
        else:
            for hub in self._hubs:
                lines += [
                    f"  ┌── {hub.name} ──────────────────────────────",
                    f"  │  Treasury: ${hub.treasury_usd:,.2f}  |  "
                    f"Members: {hub.member_count}  |  Your share: {hub.ownership_pct:.1f}%",
                    f"  │  Active Bots: {hub.active_bots}  |  "
                    f"Last Dividend: ${hub.last_dividend_usd:,.2f}",
                    "  └─────────────────────────────────────────────",
                ]
        lines += [
            "",
            "  QUICK ACTIONS",
            "  [Deposit]  [Run Bots]  [View Hub]  [Governance]  [Wallet]",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Return structured data for the frontend renderer."""
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "user_name": self.user_name,
            "kyc_verified": self.kyc_verified,
            "total_balance_usd": round(self.total_balance_usd, 2),
            "dreamcoin_balance": self.dreamcoin_balance,
            "earnings": {
                "today_usd": round(self.earnings.today_usd, 2),
                "this_week_usd": round(self.earnings.this_week_usd, 2),
                "this_month_usd": round(self.earnings.this_month_usd, 2),
                "all_time_usd": round(self.earnings.all_time_usd, 2),
            },
            "active_bot_count": self.active_bot_count,
            "wealth_hubs": [
                {
                    "hub_id": h.hub_id,
                    "name": h.name,
                    "treasury_usd": round(h.treasury_usd, 2),
                    "member_count": h.member_count,
                    "active_bots": h.active_bots,
                    "last_dividend_usd": round(h.last_dividend_usd, 2),
                    "ownership_pct": h.ownership_pct,
                }
                for h in self._hubs
            ],
        }

    @classmethod
    def demo(cls) -> "HomeDashboardScreen":
        """Return a pre-populated demo instance."""
        screen = cls(
            user_name="Alex Johnson",
            total_balance_usd=12_547.50,
            dreamcoin_balance=850.0,
            earnings=EarningsSummary(
                today_usd=42.50,
                this_week_usd=298.75,
                this_month_usd=1_203.40,
                all_time_usd=4_820.00,
            ),
            active_bot_count=4,
            kyc_verified=True,
        )
        screen.add_hub(HubCard(
            hub_id="hub-001",
            name="Family Wealth Circle",
            treasury_usd=8_500.00,
            member_count=5,
            active_bots=3,
            last_dividend_usd=320.50,
            ownership_pct=35.0,
        ))
        screen.add_hub(HubCard(
            hub_id="hub-002",
            name="Tech Entrepreneurs Pool",
            treasury_usd=24_200.00,
            member_count=12,
            active_bots=5,
            last_dividend_usd=880.75,
            ownership_pct=8.3,
        ))
        return screen
