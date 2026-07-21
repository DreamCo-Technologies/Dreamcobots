"""
DreamCo Money OS — Grants & Legal Screen

FlutterFlow-style screen for discovering legal class-action payouts and
government/private grant opportunities.
"""

from datetime import datetime


class GrantsLegalScreen:
    """
    Dashboard for legal payouts and grant applications.

    Fields
    ------
    legal_payouts    : Active class-action / legal settlement opportunities.
    grants           : Available grant opportunities.
    applied_items    : List of items user has applied for.
    total_potential  : Sum of potential payouts/grants.
    filter_type      : 'all' | 'legal' | 'grant'.
    sort_by          : 'deadline' | 'amount' | 'roi'.
    last_updated     : ISO timestamp.
    """

    SCREEN_NAME = "GrantsLegalScreen"
    ROUTE = "/grants-legal"

    def __init__(
        self,
        legal_payouts: list = None,
        grants: list = None,
        applied_items: list = None,
        filter_type: str = "all",
        sort_by: str = "deadline",
    ):
        self.legal_payouts = legal_payouts or []
        self.grants = grants or []
        self.applied_items = applied_items or []
        all_items = self.legal_payouts + self.grants
        self.total_potential = round(sum(i.get("amount", 0) for i in all_items), 2)
        self.filter_type = filter_type
        self.sort_by = sort_by
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "total_potential_card": {
                    "value": f"${self.total_potential:,.2f}",
                    "label": "Total Potential Payouts",
                    "color": "green",
                },
                "filter_tabs": {
                    "options": ["all", "legal", "grant"],
                    "active": self.filter_type,
                },
                "sort_bar": {"sort_by": self.sort_by},
                "legal_section": {
                    "title": "⚖️ Legal Payouts",
                    "count": len(self.legal_payouts),
                    "items": self.legal_payouts,
                },
                "grants_section": {
                    "title": "💰 Grant Opportunities",
                    "count": len(self.grants),
                    "items": self.grants,
                },
                "applied_section": {
                    "title": "✅ Applied",
                    "count": len(self.applied_items),
                    "items": self.applied_items,
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "legal_payouts": self.legal_payouts,
            "grants": self.grants,
            "applied_items": self.applied_items,
            "total_potential": self.total_potential,
            "filter_type": self.filter_type,
            "sort_by": self.sort_by,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "GrantsLegalScreen":
        return cls(
            legal_payouts=[
                {"id": "LP-001", "case_name": "Consumer Data Breach Settlement",
                 "amount": 125.00, "deadline": "2025-08-31", "status": "open",
                 "payout_type": "class_action"},
                {"id": "LP-002", "case_name": "Auto Loan Overcharge Settlement",
                 "amount": 350.00, "deadline": "2025-09-15", "status": "open",
                 "payout_type": "settlement"},
            ],
            grants=[
                {"id": "GR-001", "name": "Small Business Innovation Grant",
                 "amount": 5_000.00, "deadline": "2025-10-01", "category": "business",
                 "application_cost": 0, "status": "open"},
                {"id": "GR-002", "name": "Community Development Block Grant",
                 "amount": 10_000.00, "deadline": "2025-11-30", "category": "community",
                 "application_cost": 25, "status": "open"},
            ],
            applied_items=[
                {"id": "LP-001", "case_name": "Consumer Data Breach Settlement", "status": "applied"},
            ],
            filter_type="all",
            sort_by="deadline",
        )
