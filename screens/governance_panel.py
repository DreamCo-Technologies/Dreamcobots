"""
DreamCo — Governance Panel Screen

Allows Wealth Hub members to view and vote on active proposals, see
proposal history, and track results.

Fields
------
- Active proposals list with vote counts and remaining time
- Proposal detail view
- Vote submission (Approve / Reject)
- Passed/Rejected proposal history
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ProposalDetail:
    """Full detail for a governance proposal."""
    proposal_id: str
    title: str
    description: str
    proposal_type: str
    proposer_name: str
    votes_for: int
    votes_against: int
    total_eligible_voters: int
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

    def participation_pct(self) -> float:
        total_votes = self.votes_for + self.votes_against
        if self.total_eligible_voters == 0:
            return 0.0
        return round(total_votes / self.total_eligible_voters * 100, 1)

    def approval_pct(self) -> float:
        total = self.votes_for + self.votes_against
        if total == 0:
            return 0.0
        return round(self.votes_for / total * 100, 1)

    def created_str(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")


class GovernancePanelScreen:
    """
    Governance Panel Screen for the DreamCo platform.

    Displays active and historical governance proposals for a Wealth Hub,
    shows voting results, and lets members cast their votes.

    Usage
    -----
        screen = GovernancePanelScreen(hub_id="hub-001", hub_name="Family Circle")
        screen.add_proposal(ProposalDetail(...))
        print(screen.render())
    """

    SCREEN_NAME = "Governance Panel"
    ROUTE = "/hub/{hub_id}/governance"

    def __init__(self, hub_id: str, hub_name: str, current_user_id: str = "") -> None:
        self.hub_id = hub_id
        self.hub_name = hub_name
        self.current_user_id = current_user_id
        self._proposals: list[ProposalDetail] = []

    def add_proposal(self, proposal: ProposalDetail) -> None:
        self._proposals.append(proposal)

    def open_proposals(self) -> list[ProposalDetail]:
        return [p for p in self._proposals if p.status == "open"]

    def closed_proposals(self) -> list[ProposalDetail]:
        return [p for p in self._proposals if p.status != "open"]

    def render(self) -> str:
        """Return a plain-text demo rendering of the Governance Panel."""
        open_props = self.open_proposals()
        closed_props = self.closed_proposals()
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║          DREAMCO — GOVERNANCE PANEL                  ║",
            "╚══════════════════════════════════════════════════════╝",
            f"  Hub: {self.hub_name}",
            f"  Open Proposals: {len(open_props)}  |  "
            f"Closed: {len(closed_props)}",
            "",
            "  ── ACTIVE PROPOSALS ──────────────────────────────────",
        ]
        if not open_props:
            lines.append("  No open proposals.")
        else:
            for p in open_props:
                bar_for = "█" * int(p.approval_pct() / 10)
                bar_against = "░" * (10 - int(p.approval_pct() / 10))
                lines += [
                    f"  [{p.proposal_type.upper():<12}] {p.title[:45]}",
                    f"  Proposed by: {p.proposer_name}  |  Created: {p.created_str()}",
                    f"  For: {p.votes_for}  Against: {p.votes_against}  "
                    f"Participation: {p.participation_pct():.0f}%",
                    f"  [{bar_for}{bar_against}] {p.approval_pct():.0f}% approval",
                    f"  [{p.description[:80]}]",
                    "  [Vote FOR]  [Vote AGAINST]  [View Detail]",
                    "  " + "─" * 55,
                ]
        lines += [
            "",
            "  ── CLOSED PROPOSALS ─────────────────────────────────",
        ]
        if not closed_props:
            lines.append("  No closed proposals.")
        else:
            for p in closed_props:
                result_icon = "✅ PASSED" if p.status == "passed" else "❌ REJECTED"
                lines.append(
                    f"  {result_icon}  {p.title[:40]:<40}  "
                    f"{p.votes_for}✅/{p.votes_against}❌"
                )
        lines += [
            "",
            "  ACTIONS",
            "  [New Proposal]  [View My Votes]  [Proposal History]",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        def _serialize(p: ProposalDetail) -> dict:
            return {
                "proposal_id": p.proposal_id,
                "title": p.title,
                "description": p.description,
                "proposal_type": p.proposal_type,
                "proposer_name": p.proposer_name,
                "votes_for": p.votes_for,
                "votes_against": p.votes_against,
                "total_eligible_voters": p.total_eligible_voters,
                "participation_pct": p.participation_pct(),
                "approval_pct": p.approval_pct(),
                "status": p.status,
                "created_at": p.created_str(),
            }

        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE.format(hub_id=self.hub_id),
            "hub_id": self.hub_id,
            "hub_name": self.hub_name,
            "open_proposals": [_serialize(p) for p in self.open_proposals()],
            "closed_proposals": [_serialize(p) for p in self.closed_proposals()],
        }

    @classmethod
    def demo(cls) -> "GovernancePanelScreen":
        """Return a pre-populated demo instance."""
        from datetime import timedelta
        screen = cls(hub_id="hub-001", hub_name="Family Wealth Circle", current_user_id="alice")
        base = datetime(2025, 3, 1, tzinfo=timezone.utc)
        screen.add_proposal(ProposalDetail(
            "prop-1", "Allocate 10% to Bitcoin", "Move 10% of growth allocation into BTC.",
            "investment", "Alice Johnson", 3, 1, 4, "open", created_at=base,
        ))
        screen.add_proposal(ProposalDetail(
            "prop-2", "Monthly dividend payout schedule",
            "Change from quarterly to monthly dividend distributions.",
            "payout", "Bob Williams", 4, 0, 4, "open", created_at=base + timedelta(days=3),
        ))
        screen.add_proposal(ProposalDetail(
            "prop-3", "Increase reinvestment rate to 30%",
            "Raise the auto-reinvestment rate from 20% to 30%.",
            "risk_level", "Carol Davis", 2, 2, 4, "rejected",
            created_at=base - timedelta(days=15),
            closed_at=base - timedelta(days=7),
        ))
        screen.add_proposal(ProposalDetail(
            "prop-4", "Add Real Estate Bot to hub",
            "Activate the Real Estate Bot for automated deal finding.",
            "other", "Alice Johnson", 4, 0, 4, "passed",
            created_at=base - timedelta(days=30),
            closed_at=base - timedelta(days=22),
        ))
        return screen
