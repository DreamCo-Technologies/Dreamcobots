"""
DreamCo — Referral System Screen

Displays a user's referral performance: invite links, per-referral earnings,
team growth tree, and leaderboard position.

Fields
------
- Unique invite link for user
- Earnings per referral program
- Team tree visualization (referred members and their sub-referrals)
- Leaderboard: top referrers in the hub
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReferralProgram:
    """A referral/affiliate program a user is enrolled in."""
    program_id: str
    program_name: str
    payout_per_referral_usd: float
    referrals_made: int = 0
    total_earned_usd: float = 0.0
    status: str = "active"
    invite_link: str = ""


@dataclass
class TeamNode:
    """A node in the referral team tree."""
    user_id: str
    name: str
    level: int = 1          # 1 = direct, 2 = 2nd tier, etc.
    contribution_usd: float = 0.0
    own_referrals: int = 0
    earned_from_this_usd: float = 0.0


class ReferralSystemScreen:
    """
    Referral System Screen for the DreamCo platform.

    Shows a comprehensive view of a user's referral activity: enrolled
    programs, earnings, team network visualization, and hub leaderboard.

    Usage
    -----
        screen = ReferralSystemScreen(
            user_id="alice",
            user_name="Alice Johnson",
            invite_code="ALICE2025",
        )
        screen.add_program(ReferralProgram("wisely", "Wisely Pay Card", 25.0, 8, 200.0))
        print(screen.render())
    """

    SCREEN_NAME = "Referral System"
    ROUTE = "/referral"

    BASE_INVITE_URL = "https://dreamco.app/join/"

    def __init__(
        self,
        user_id: str,
        user_name: str = "Member",
        invite_code: str = "",
        total_referrals: int = 0,
    ) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.invite_code = invite_code or f"DC{str(user_id).upper()[:6]}"
        self.total_referrals = total_referrals
        self._programs: list[ReferralProgram] = []
        self._team: list[TeamNode] = []
        self._leaderboard: list[dict] = []

    @property
    def invite_link(self) -> str:
        return f"{self.BASE_INVITE_URL}{self.invite_code}"

    def add_program(self, program: ReferralProgram) -> None:
        self._programs.append(program)

    def add_team_member(self, node: TeamNode) -> None:
        self._team.append(node)

    def set_leaderboard(self, entries: list[dict]) -> None:
        """Set leaderboard entries: list of {rank, name, referrals, earned_usd}."""
        self._leaderboard = entries

    def total_earnings(self) -> float:
        return sum(p.total_earned_usd for p in self._programs)

    def total_referrals_made(self) -> int:
        return sum(p.referrals_made for p in self._programs)

    def direct_team_size(self) -> int:
        return sum(1 for t in self._team if t.level == 1)

    def render(self) -> str:
        """Return a plain-text demo rendering of the Referral System screen."""
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║          DREAMCO — REFERRAL SYSTEM                   ║",
            "╚══════════════════════════════════════════════════════╝",
            f"  {self.user_name}",
            "",
            "  YOUR INVITE LINK",
            f"  🔗 {self.invite_link}",
            f"  Code: {self.invite_code}",
            "",
            "  EARNINGS SUMMARY",
            f"  Total Earned:       ${self.total_earnings():,.2f}",
            f"  Total Referrals:    {self.total_referrals_made()}",
            f"  Direct Team Size:   {self.direct_team_size()}",
            "",
            "  REFERRAL PROGRAMS",
            f"  {'Program':<28} {'Referrals':>10} {'Per Ref':>9} {'Total Earned':>14}",
            "  " + "─" * 66,
        ]
        if not self._programs:
            lines.append("  No programs enrolled yet.")
        else:
            for p in self._programs:
                status_icon = "🟢" if p.status == "active" else "🔴"
                lines.append(
                    f"  {status_icon} {p.program_name:<26} {p.referrals_made:>10} "
                    f"${p.payout_per_referral_usd:>7.2f} ${p.total_earned_usd:>12,.2f}"
                )

        lines += [
            "",
            "  TEAM GROWTH TREE",
        ]
        direct = [t for t in self._team if t.level == 1]
        second = [t for t in self._team if t.level == 2]
        if not direct:
            lines.append("  No referrals yet. Share your invite link!")
        else:
            lines.append(f"  📍 {self.user_name} (You)")
            for node in direct:
                lines.append(
                    f"     └── {node.name:<22} Level 1  "
                    f"Sub-referrals: {node.own_referrals}  "
                    f"Earned you: ${node.earned_from_this_usd:.2f}"
                )
            if second:
                lines.append("         (2nd-tier members shown in app)")

        if self._leaderboard:
            lines += [
                "",
                "  HUB LEADERBOARD — TOP REFERRERS",
                f"  {'Rank':<5} {'Name':<22} {'Referrals':>10} {'Earned':>14}",
                "  " + "─" * 55,
            ]
            for entry in self._leaderboard[:5]:
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry["rank"], "  ")
                lines.append(
                    f"  {medal} #{entry['rank']:<3} {entry['name']:<22} "
                    f"{entry['referrals']:>10} ${entry['earned_usd']:>12,.2f}"
                )

        lines += [
            "",
            "  ACTIONS",
            "  [Copy Invite Link]  [Share on Social]  [View Programs]  [Team Tree]",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "invite_code": self.invite_code,
            "invite_link": self.invite_link,
            "total_earnings_usd": round(self.total_earnings(), 2),
            "total_referrals_made": self.total_referrals_made(),
            "direct_team_size": self.direct_team_size(),
            "programs": [
                {
                    "program_id": p.program_id,
                    "program_name": p.program_name,
                    "payout_per_referral_usd": p.payout_per_referral_usd,
                    "referrals_made": p.referrals_made,
                    "total_earned_usd": round(p.total_earned_usd, 2),
                    "status": p.status,
                    "invite_link": p.invite_link,
                }
                for p in self._programs
            ],
            "team": [
                {
                    "user_id": t.user_id,
                    "name": t.name,
                    "level": t.level,
                    "contribution_usd": t.contribution_usd,
                    "own_referrals": t.own_referrals,
                    "earned_from_this_usd": t.earned_from_this_usd,
                }
                for t in self._team
            ],
            "leaderboard": self._leaderboard,
        }

    @classmethod
    def demo(cls) -> "ReferralSystemScreen":
        """Return a pre-populated demo instance."""
        screen = cls(
            user_id="alice",
            user_name="Alice Johnson",
            invite_code="ALICE2025",
        )
        screen.add_program(ReferralProgram(
            "wisely", "Wisely Pay Card", 25.0, 8, 200.0, "active",
            "https://wisely.com/ref/ALICE2025",
        ))
        screen.add_program(ReferralProgram(
            "cashapp", "Cash App", 15.0, 12, 180.0, "active",
            "https://cash.app/ref/ALICE2025",
        ))
        screen.add_program(ReferralProgram(
            "robinhood", "Robinhood", 20.0, 5, 100.0, "active",
            "https://join.robinhood.com/alice2025",
        ))
        screen.add_program(ReferralProgram(
            "amazon", "Amazon Affiliate", 50.0, 22, 1_100.0, "active",
            "https://amzn.to/ALICE2025",
        ))
        screen.add_team_member(TeamNode("bob", "Bob Williams", 1, 2_500.0, 3, 37.50))
        screen.add_team_member(TeamNode("carol", "Carol Davis", 1, 2_000.0, 2, 30.00))
        screen.add_team_member(TeamNode("dave", "Dave Miller", 1, 1_000.0, 0, 15.00))
        screen.add_team_member(TeamNode("eve", "Eve Thompson", 2, 800.0, 1, 0.0))
        screen.set_leaderboard([
            {"rank": 1, "name": "Alice Johnson", "referrals": 47, "earned_usd": 1_580.0},
            {"rank": 2, "name": "Bob Williams", "referrals": 31, "earned_usd": 930.0},
            {"rank": 3, "name": "Carol Davis", "referrals": 28, "earned_usd": 840.0},
            {"rank": 4, "name": "Frank Lee", "referrals": 19, "earned_usd": 570.0},
            {"rank": 5, "name": "Grace Kim", "referrals": 14, "earned_usd": 420.0},
        ])
        return screen
