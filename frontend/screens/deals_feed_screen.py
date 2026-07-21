"""
DreamCo Money OS — Deals Feed Screen

FlutterFlow-style screen showing live price drops, coupons, and penny deals.
"""

from datetime import datetime


class DealsFeedScreen:
    """
    Live feed of deals from all bots: price drops, coupons, and penny items.

    Fields
    ------
    deals            : List of deal objects from dealBot.
    penny_items      : List of penny deal objects from pennyBot.
    coupons          : List of active coupon objects from couponBot.
    selected_store   : Currently active store filter.
    selected_category: Currently active category filter.
    sort_by          : Sort mode ('savings' | 'cashback' | 'score').
    last_updated     : ISO timestamp of last refresh.
    """

    SCREEN_NAME = "DealsFeedScreen"
    ROUTE = "/deals"

    def __init__(
        self,
        deals: list = None,
        penny_items: list = None,
        coupons: list = None,
        selected_store: str = "all",
        selected_category: str = "all",
        sort_by: str = "savings",
    ):
        self.deals = deals or []
        self.penny_items = penny_items or []
        self.coupons = coupons or []
        self.selected_store = selected_store
        self.selected_category = selected_category
        self.sort_by = sort_by
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        """Return the screen's UI data model."""
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "filter_bar": {
                    "store": self.selected_store,
                    "category": self.selected_category,
                    "sort_by": self.sort_by,
                },
                "deals_section": {
                    "title": "🔥 Hot Deals",
                    "count": len(self.deals),
                    "items": self.deals,
                },
                "penny_section": {
                    "title": "🪙 Penny Deals",
                    "count": len(self.penny_items),
                    "items": self.penny_items,
                },
                "coupon_section": {
                    "title": "✂️ Stack Coupons",
                    "count": len(self.coupons),
                    "items": self.coupons,
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "deals": self.deals,
            "penny_items": self.penny_items,
            "coupons": self.coupons,
            "selected_store": self.selected_store,
            "selected_category": self.selected_category,
            "sort_by": self.sort_by,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "DealsFeedScreen":
        return cls(
            deals=[
                {"id": "DEAL-AMZ-001", "title": "Electronics Deal #1 at amazon", "store": "amazon",
                 "originalPrice": 199.99, "salePrice": 89.99, "savings": 110.00, "savingsPct": 55.0,
                 "couponCode": "SAVE5001", "cashbackPct": 8},
                {"id": "DEAL-WAL-002", "title": "Appliances Deal #2 at walmart", "store": "walmart",
                 "originalPrice": 299.99, "salePrice": 149.99, "savings": 150.00, "savingsPct": 50.0,
                 "couponCode": "SAVE5002", "cashbackPct": 4},
            ],
            penny_items=[
                {"id": "PENNY-DG-001", "name": "Clearance Shampoo", "store": "dollar_general",
                 "clearancePrice": 0.01, "resaleValue": 8.00, "profit": 7.99},
            ],
            coupons=[
                {"code": "AMZ5001", "discount": 15, "discountType": "pct", "source": "honey", "stackable": True},
            ],
            selected_store="all",
            selected_category="electronics",
        )
