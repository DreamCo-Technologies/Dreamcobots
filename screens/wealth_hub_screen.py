"""
DreamCo — Wealth Hub Screen

Displays a single Wealth Hub's details: treasury value, member list with
ownership percentages, active bots, and the governance voting panel.

Fields
------
- Hub name, description, created date
- Treasury value with asset allocation breakdown
- Member table (name, contribution, ownership %, dividends earned)
- Active bots panel
- Governance: open proposals with vote counts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemberRow:
    """A single row in the member table."""
    user_id: str
    name: str
    contribution_usd: float
    ownership_pct: float
    total_dividends_usd: float
    kyc_verified: bool = True
    votes_cast: int = 0


@dataclass
class ProposalRow:
    """A summary row for a governance proposal."""
    proposal_id: str
    title: str
    proposal_type: str
    votes_for: int
    votes_against: int
    status: str


class WealthHubScreen:
    """
    Wealth Hub Screen for the DreamCo platform.

    Shows the full detail view of a single Wealth Hub, including
    treasury breakdown, member ownership table, active bots, and
    open governance proposals.

    Usage
    -----
        screen = WealthHubScreen(
            hub_id="hub-001",
            name="Family Wealth Circle",
            treasury_usd=8500.0,
        )
        screen.add_member(MemberRow("alice", "Alice J.", 3000.0, 35.0, 420.0))
        print(screen.render())
    """

    SCREEN_NAME = "Wealth Hub"
    ROUTE = "/hub/{hub_id}"

    def __init__(
        self,
        hub_id: str,
        name: str,
        description: str = "",
        treasury_usd: float = 0.0,
        reinvestment_rate_pct: float = 20.0,
        allocation: Optional[dict] = None,
        active_bots: Optional[list[str]] = None,
    ) -> None:
        self.hub_id = hub_id
        self.name = name
        self.description = description
        self.treasury_usd = treasury_usd
        self.reinvestment_rate_pct = reinvestment_rate_pct
        self.allocation = allocation or {
            "wealth_protection": {"pct": 40.0, "usd": treasury_usd * 0.4, "assets": ["Gold", "Silver"]},
            "growth": {"pct": 40.0, "usd": treasury_usd * 0.4, "assets": ["Stocks", "Real Estate"]},
            "high_growth": {"pct": 20.0, "usd": treasury_usd * 0.2, "assets": ["Crypto", "Startups"]},
        }
        self.active_bots: list[str] = active_bots or []
        self._members: list[MemberRow] = []
        self._proposals: list[ProposalRow] = []

    def add_member(self, member: MemberRow) -> None:
        self._members.append(member)

    def add_proposal(self, proposal: ProposalRow) -> None:
        self._proposals.append(proposal)

    def member_count(self) -> int:
        return len(self._members)

    def render(self) -> str:
        """Return a plain-text demo rendering of the Wealth Hub screen."""
        alloc = self.allocation
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            f"║  WEALTH HUB: {self.name[:38]:<38}  ║",
            "╚══════════════════════════════════════════════════════╝",
        ]
        if self.description:
            lines.append(f"  {self.description}")
        lines += [
            "",
            "  TREASURY",
            f"  Total: ${self.treasury_usd:,.2f}  |  "
            f"Reinvestment Rate: {self.reinvestment_rate_pct:.0f}%",
            "",
            "  ASSET ALLOCATION",
            f"  🧱 Wealth Protection ({alloc['wealth_protection']['pct']:.0f}%): "
            f"${alloc['wealth_protection']['usd']:,.2f}",
            f"     Assets: {', '.join(alloc['wealth_protection']['assets'])}",
            f"  📈 Growth ({alloc['growth']['pct']:.0f}%): "
            f"${alloc['growth']['usd']:,.2f}",
            f"     Assets: {', '.join(alloc['growth']['assets'])}",
            f"  ⚡ High-Growth ({alloc['high_growth']['pct']:.0f}%): "
            f"${alloc['high_growth']['usd']:,.2f}",
            f"     Assets: {', '.join(alloc['high_growth']['assets'])}",
            "",
            "  MEMBERS",
            f"  {'Name':<20} {'Contribution':>14} {'Ownership':>10} {'Dividends':>12} {'KYC':>5}",
            "  " + "─" * 65,
        ]
        if not self._members:
            lines.append("  No members yet.")
        else:
            for m in self._members:
                kyc = "✅" if m.kyc_verified else "⚠️"
                lines.append(
                    f"  {m.name:<20} ${m.contribution_usd:>12,.2f} "
                    f"{m.ownership_pct:>9.1f}% ${m.total_dividends_usd:>11,.2f} {kyc:>4}"
                )
        lines += [
            "",
            f"  🤖 ACTIVE BOTS: {', '.join(self.active_bots) or 'None'}",
            "",
            "  GOVERNANCE — OPEN PROPOSALS",
        ]
        open_props = [p for p in self._proposals if p.status == "open"]
        if not open_props:
            lines.append("  No open proposals.")
        else:
            for p in open_props:
                lines.append(
                    f"  [{p.proposal_type.upper():<12}] {p.title[:35]:<35} "
                    f"✅{p.votes_for} / ❌{p.votes_against}"
                )
        lines += [
            "",
            "  ACTIONS",
            "  [Deposit]  [Withdraw]  [New Proposal]  [Run Bot]  [Analytics]",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE.format(hub_id=self.hub_id),
            "hub_id": self.hub_id,
            "name": self.name,
            "description": self.description,
            "treasury_usd": round(self.treasury_usd, 2),
            "reinvestment_rate_pct": self.reinvestment_rate_pct,
            "allocation": self.allocation,
            "active_bots": self.active_bots,
            "members": [
                {
                    "user_id": m.user_id,
                    "name": m.name,
                    "contribution_usd": round(m.contribution_usd, 2),
                    "ownership_pct": m.ownership_pct,
                    "total_dividends_usd": round(m.total_dividends_usd, 2),
                    "kyc_verified": m.kyc_verified,
                    "votes_cast": m.votes_cast,
                }
                for m in self._members
            ],
            "open_proposals": [
                {
                    "proposal_id": p.proposal_id,
                    "title": p.title,
                    "proposal_type": p.proposal_type,
                    "votes_for": p.votes_for,
                    "votes_against": p.votes_against,
                    "status": p.status,
                }
                for p in self._proposals
            ],
        }

    @classmethod
    def demo(cls) -> "WealthHubScreen":
        """Return a pre-populated demo instance."""
        screen = cls(
            hub_id="hub-001",
            name="Family Wealth Circle",
            description="Our family's shared investment pool — building generational wealth together.",
            treasury_usd=8_500.00,
            reinvestment_rate_pct=20.0,
            active_bots=["money_finder", "referral", "trading"],
        )
        screen.add_member(MemberRow("alice", "Alice Johnson", 3_000.0, 35.3, 420.50, True, 3))
        screen.add_member(MemberRow("bob", "Bob Williams", 2_500.0, 29.4, 350.25, True, 2))
        screen.add_member(MemberRow("carol", "Carol Davis", 2_000.0, 23.5, 280.00, True, 1))
        screen.add_member(MemberRow("dave", "Dave Miller", 1_000.0, 11.8, 140.00, False, 0))
        screen.add_proposal(ProposalRow(
            "prop-1", "Allocate 10% to Bitcoin", "investment", 3, 1, "open"
        ))
        screen.add_proposal(ProposalRow(
            "prop-2", "Monthly dividend payout schedule", "payout", 4, 0, "open"
        ))
        return screen
