"""
DreamCo — Bot Control Center Screen

Gives users full control over their AI bot fleet: toggle bots on/off,
view earnings per bot, configure automation settings, and see run history.

Fields
------
- Bot cards: name, status (on/off), earnings, last run timestamp
- Automation settings per bot
- Total bot-generated earnings
- Quick-run button for each bot
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class BotCard:
    """Status card for a single AI bot."""
    bot_type: str
    display_name: str
    description: str
    is_active: bool = False
    total_earnings_usd: float = 0.0
    last_run: Optional[datetime] = None
    run_count: int = 0
    tier_required: str = "FREE"
    is_available: bool = True

    def last_run_str(self) -> str:
        if self.last_run is None:
            return "Never"
        return self.last_run.strftime("%Y-%m-%d %H:%M UTC")


class BotControlCenterScreen:
    """
    Bot Control Center Screen for the DreamCo platform.

    Allows users to manage all AI bots assigned to their Wealth Hubs:
    activate/deactivate bots, review per-bot earnings, and configure
    automation schedules.

    Usage
    -----
        screen = BotControlCenterScreen(hub_id="hub-001", hub_name="Family Circle")
        screen.add_bot(BotCard("money_finder", "Money Finder Bot", "Finds unclaimed funds"))
        print(screen.render())
    """

    SCREEN_NAME = "Bot Control Center"
    ROUTE = "/hub/{hub_id}/bots"

    # Full bot catalogue with descriptions
    BOT_CATALOGUE = [
        ("money_finder", "💰 Money Finder Bot", "Scrapes grants, unclaimed funds & opportunities", "FREE"),
        ("referral", "📢 Referral Bot", "Auto-promotes apps and affiliate programs", "PRO"),
        ("real_estate", "🏠 Real Estate Bot", "Finds foreclosures, deals & rental properties", "PRO"),
        ("trading", "📊 Trading Bot", "Executes AI-driven stock & crypto trades", "PRO"),
        ("arbitrage", "🛒 Arbitrage Bot", "Flips products across platforms automatically", "ENTERPRISE"),
        ("grant_finder", "🔍 Grant Finder Bot", "Discovers government & private grants", "FREE"),
        ("lead_gen", "🎯 Lead Gen Bot", "Generates high-quality leads for member businesses", "PRO"),
    ]

    def __init__(self, hub_id: str, hub_name: str) -> None:
        self.hub_id = hub_id
        self.hub_name = hub_name
        self._bots: dict[str, BotCard] = {}

    def add_bot(self, bot: BotCard) -> None:
        self._bots[bot.bot_type] = bot

    def get_bot(self, bot_type: str) -> Optional[BotCard]:
        return self._bots.get(bot_type)

    def active_bots(self) -> list[BotCard]:
        return [b for b in self._bots.values() if b.is_active]

    def total_earnings(self) -> float:
        return sum(b.total_earnings_usd for b in self._bots.values())

    def render(self) -> str:
        """Return a plain-text demo rendering of the Bot Control Center."""
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║          DREAMCO — BOT CONTROL CENTER                ║",
            "╚══════════════════════════════════════════════════════╝",
            f"  Hub: {self.hub_name}",
            f"  Total Bot Earnings: ${self.total_earnings():,.2f}  |  "
            f"Active Bots: {len(self.active_bots())}",
            "",
            f"  {'Bot':<28} {'Status':>7} {'Earnings':>12} {'Runs':>6} {'Last Run':>22}",
            "  " + "─" * 80,
        ]
        if not self._bots:
            lines.append("  No bots configured yet.")
        else:
            for bot in self._bots.values():
                status = "🟢 ON " if bot.is_active else "🔴 OFF"
                avail = "" if bot.is_available else " [LOCKED]"
                lines.append(
                    f"  {bot.display_name[:28]:<28} {status:>7} "
                    f"${bot.total_earnings_usd:>10,.2f} {bot.run_count:>6}  "
                    f"{bot.last_run_str():>22}{avail}"
                )
        lines += [
            "",
            "  AUTOMATION SETTINGS",
            "  ┌─────────────────────────────────────────────────┐",
            "  │  Auto-reinvest profits:    ✅ Enabled           │",
            "  │  Daily run schedule:       6:00 AM UTC          │",
            "  │  Profit alerts:            ✅ Enabled           │",
            "  │  Risk tolerance:           Medium               │",
            "  └─────────────────────────────────────────────────┘",
            "",
            "  ACTIONS",
            "  [Activate Bot]  [Run Now]  [View Earnings]  [Settings]",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE.format(hub_id=self.hub_id),
            "hub_id": self.hub_id,
            "hub_name": self.hub_name,
            "total_earnings_usd": round(self.total_earnings(), 2),
            "active_bot_count": len(self.active_bots()),
            "bots": [
                {
                    "bot_type": b.bot_type,
                    "display_name": b.display_name,
                    "description": b.description,
                    "is_active": b.is_active,
                    "total_earnings_usd": round(b.total_earnings_usd, 2),
                    "last_run": b.last_run_str(),
                    "run_count": b.run_count,
                    "tier_required": b.tier_required,
                    "is_available": b.is_available,
                }
                for b in self._bots.values()
            ],
        }

    @classmethod
    def demo(cls) -> "BotControlCenterScreen":
        """Return a pre-populated demo instance."""
        screen = cls(hub_id="hub-001", hub_name="Family Wealth Circle")
        now = datetime.now(timezone.utc)
        screen.add_bot(BotCard(
            "money_finder", "💰 Money Finder Bot",
            "Scrapes grants, unclaimed funds & opportunities",
            is_active=True, total_earnings_usd=1_240.50,
            last_run=now, run_count=47, tier_required="FREE",
        ))
        screen.add_bot(BotCard(
            "referral", "📢 Referral Bot",
            "Auto-promotes apps and affiliate programs",
            is_active=True, total_earnings_usd=3_820.75,
            last_run=now, run_count=120, tier_required="PRO",
        ))
        screen.add_bot(BotCard(
            "real_estate", "🏠 Real Estate Bot",
            "Finds foreclosures, deals & rental properties",
            is_active=True, total_earnings_usd=0.0,
            last_run=None, run_count=12, tier_required="PRO",
        ))
        screen.add_bot(BotCard(
            "trading", "📊 Trading Bot",
            "Executes AI-driven stock & crypto trades",
            is_active=False, total_earnings_usd=520.00,
            last_run=now, run_count=8, tier_required="PRO",
        ))
        screen.add_bot(BotCard(
            "arbitrage", "🛒 Arbitrage Bot",
            "Flips products across platforms automatically",
            is_active=False, total_earnings_usd=0.0,
            last_run=None, run_count=0,
            tier_required="ENTERPRISE", is_available=False,
        ))
        return screen
