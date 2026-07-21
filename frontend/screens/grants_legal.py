"""GrantsLegalScreen — government grants and legal settlement opportunities."""


class GrantsLegalScreen:
    SCREEN_ID = "grants_legal"

    def __init__(self, grants=None, legal_payouts=None):
        self.grants = grants or []
        self.legal_payouts = legal_payouts or []

    def render(self) -> str:
        lines = [
            "=== DreamCo — Grants & Legal Payouts ===",
            f"Available Grants: {len(self.grants)}",
            f"Legal Opportunities: {len(self.legal_payouts)}",
        ]
        for g in self.grants[:2]:
            lines.append(f"  [Grant] {g.get('name', '?')} — ${g.get('amount', 0):,.2f}")
        for lp in self.legal_payouts[:2]:
            lines.append(f"  [Legal] {lp.get('claimType', '?')} — ${lp.get('amount', 0):,.2f}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "grants": self.grants,
            "legal_payouts": self.legal_payouts,
        }

    @classmethod
    def demo(cls) -> "GrantsLegalScreen":
        return cls(
            grants=[
                {"name": "SBIR Small Business Grant", "amount": 50000.0},
                {"name": "USDA Rural Development", "amount": 25000.0},
            ],
            legal_payouts=[
                {"claimType": "Data Breach Settlement", "amount": 125.0},
                {"claimType": "Consumer Class Action", "amount": 75.0},
            ],
        )
