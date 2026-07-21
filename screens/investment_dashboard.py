"""
DreamCo — Investment Dashboard Screen

Shows a Wealth Hub's full investment portfolio: asset allocation by tier,
individual holdings, ROI tracking, and performance over time.

Fields
------
- Asset allocation breakdown (Protection / Growth / High-Growth)
- Individual asset holdings with current value and P&L
- Portfolio ROI chart (text-based sparkline)
- Performance metrics: total gain, best performer, worst performer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AssetHolding:
    """A single asset position in the portfolio."""
    asset_id: str
    name: str
    asset_class: str          # e.g. "Gold", "Stock", "Crypto"
    allocation_tier: str      # "wealth_protection" | "growth" | "high_growth"
    invested_usd: float = 0.0
    current_value_usd: float = 0.0
    quantity: float = 0.0
    unit_label: str = "units"   # e.g. "oz", "shares", "BTC"

    def gain_loss_usd(self) -> float:
        return self.current_value_usd - self.invested_usd

    def roi_pct(self) -> float:
        if self.invested_usd == 0:
            return 0.0
        return round((self.gain_loss_usd() / self.invested_usd) * 100, 2)

    def gain_loss_str(self) -> str:
        val = self.gain_loss_usd()
        sign = "+" if val >= 0 else ""
        return f"{sign}${val:,.2f}"


class InvestmentDashboardScreen:
    """
    Investment Dashboard Screen for the DreamCo platform.

    Presents a comprehensive view of a Wealth Hub's investment portfolio:
    allocation tiers, individual holdings, and ROI metrics.

    Usage
    -----
        screen = InvestmentDashboardScreen(
            hub_id="hub-001",
            hub_name="Family Wealth Circle",
            total_invested_usd=8500.0,
        )
        screen.add_holding(AssetHolding("gold", "Gold", "Commodity", "wealth_protection", ...))
        print(screen.render())
    """

    SCREEN_NAME = "Investment Dashboard"
    ROUTE = "/hub/{hub_id}/investments"

    def __init__(
        self,
        hub_id: str,
        hub_name: str,
        total_invested_usd: float = 0.0,
    ) -> None:
        self.hub_id = hub_id
        self.hub_name = hub_name
        self.total_invested_usd = total_invested_usd
        self._holdings: list[AssetHolding] = []

    def add_holding(self, holding: AssetHolding) -> None:
        self._holdings.append(holding)

    def total_current_value(self) -> float:
        return sum(h.current_value_usd for h in self._holdings)

    def total_gain_loss(self) -> float:
        return self.total_current_value() - self.total_invested_usd

    def portfolio_roi_pct(self) -> float:
        if self.total_invested_usd == 0:
            return 0.0
        return round(self.total_gain_loss() / self.total_invested_usd * 100, 2)

    def best_performer(self) -> Optional[AssetHolding]:
        if not self._holdings:
            return None
        return max(self._holdings, key=lambda h: h.roi_pct())

    def worst_performer(self) -> Optional[AssetHolding]:
        if not self._holdings:
            return None
        return min(self._holdings, key=lambda h: h.roi_pct())

    def holdings_by_tier(self, tier: str) -> list[AssetHolding]:
        return [h for h in self._holdings if h.allocation_tier == tier]

    def _tier_value(self, tier: str) -> float:
        return sum(h.current_value_usd for h in self.holdings_by_tier(tier))

    def render(self) -> str:
        """Return a plain-text demo rendering of the Investment Dashboard."""
        total_val = self.total_current_value()
        gain = self.total_gain_loss()
        gain_sign = "+" if gain >= 0 else ""
        roi = self.portfolio_roi_pct()
        best = self.best_performer()
        worst = self.worst_performer()

        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║       DREAMCO — INVESTMENT DASHBOARD                 ║",
            "╚══════════════════════════════════════════════════════╝",
            f"  Hub: {self.hub_name}",
            "",
            "  PORTFOLIO SUMMARY",
            f"  Total Invested:     ${self.total_invested_usd:,.2f}",
            f"  Current Value:      ${total_val:,.2f}",
            f"  Total Gain/Loss:    {gain_sign}${gain:,.2f}  ({gain_sign}{roi:.1f}%)",
        ]
        if best:
            lines.append(f"  Best Performer:     {best.name} ({best.roi_pct():+.1f}%)")
        if worst:
            lines.append(f"  Worst Performer:    {worst.name} ({worst.roi_pct():+.1f}%)")

        tier_labels = [
            ("wealth_protection", "🧱 WEALTH PROTECTION (40%)"),
            ("growth", "📈 GROWTH (40%)"),
            ("high_growth", "⚡ HIGH-GROWTH (20%)"),
        ]
        for tier_key, tier_label in tier_labels:
            tier_holdings = self.holdings_by_tier(tier_key)
            tier_val = self._tier_value(tier_key)
            lines += [
                "",
                f"  {tier_label}  — Current: ${tier_val:,.2f}",
                f"  {'Asset':<22} {'Qty':>10} {'Invested':>12} {'Value':>12} {'G/L':>12} {'ROI':>7}",
                "  " + "─" * 80,
            ]
            if not tier_holdings:
                lines.append("  No holdings in this tier.")
            else:
                for h in tier_holdings:
                    lines.append(
                        f"  {h.name:<22} {h.quantity:>8.4f} {h.unit_label[:2]:>2}  "
                        f"${h.invested_usd:>10,.2f} ${h.current_value_usd:>10,.2f} "
                        f"{h.gain_loss_str():>12} {h.roi_pct():>+6.1f}%"
                    )

        lines += [
            "",
            "  ACTIONS",
            "  [Rebalance]  [Add Asset]  [View History]  [Export Report]",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE.format(hub_id=self.hub_id),
            "hub_id": self.hub_id,
            "hub_name": self.hub_name,
            "total_invested_usd": round(self.total_invested_usd, 2),
            "total_current_value_usd": round(self.total_current_value(), 2),
            "total_gain_loss_usd": round(self.total_gain_loss(), 2),
            "portfolio_roi_pct": self.portfolio_roi_pct(),
            "best_performer": self.best_performer().name if self.best_performer() else None,
            "worst_performer": self.worst_performer().name if self.worst_performer() else None,
            "holdings": [
                {
                    "asset_id": h.asset_id,
                    "name": h.name,
                    "asset_class": h.asset_class,
                    "allocation_tier": h.allocation_tier,
                    "quantity": h.quantity,
                    "unit_label": h.unit_label,
                    "invested_usd": round(h.invested_usd, 2),
                    "current_value_usd": round(h.current_value_usd, 2),
                    "gain_loss_usd": round(h.gain_loss_usd(), 2),
                    "roi_pct": h.roi_pct(),
                }
                for h in self._holdings
            ],
        }

    @classmethod
    def demo(cls) -> "InvestmentDashboardScreen":
        """Return a pre-populated demo instance."""
        screen = cls(
            hub_id="hub-001",
            hub_name="Family Wealth Circle",
            total_invested_usd=8_500.00,
        )
        # Wealth Protection (40% = $3,400)
        screen.add_holding(AssetHolding(
            "gold", "Gold", "Commodity", "wealth_protection",
            invested_usd=2_000.0, current_value_usd=2_180.0,
            quantity=0.985, unit_label="oz",
        ))
        screen.add_holding(AssetHolding(
            "silver", "Silver", "Commodity", "wealth_protection",
            invested_usd=800.0, current_value_usd=854.0,
            quantity=32.5, unit_label="oz",
        ))
        screen.add_holding(AssetHolding(
            "tbills", "US T-Bills", "Fixed Income", "wealth_protection",
            invested_usd=600.0, current_value_usd=618.0,
            quantity=600.0, unit_label="USD",
        ))
        # Growth (40% = $3,400)
        screen.add_holding(AssetHolding(
            "spy", "S&P 500 ETF (SPY)", "ETF", "growth",
            invested_usd=2_000.0, current_value_usd=2_340.0,
            quantity=3.9, unit_label="shares",
        ))
        screen.add_holding(AssetHolding(
            "reits", "Real Estate (REITs)", "Real Estate", "growth",
            invested_usd=1_400.0, current_value_usd=1_350.0,
            quantity=12.5, unit_label="shares",
        ))
        # High-Growth (20% = $1,700)
        screen.add_holding(AssetHolding(
            "btc", "Bitcoin (BTC)", "Crypto", "high_growth",
            invested_usd=1_200.0, current_value_usd=1_540.0,
            quantity=0.0154, unit_label="BTC",
        ))
        screen.add_holding(AssetHolding(
            "eth", "Ethereum (ETH)", "Crypto", "high_growth",
            invested_usd=500.0, current_value_usd=448.0,
            quantity=0.135, unit_label="ETH",
        ))
        return screen
