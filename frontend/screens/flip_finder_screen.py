"""
DreamCo Money OS — Flip Finder Screen

FlutterFlow-style screen for discovering local high-profit resale flips.
"""

from datetime import datetime


class FlipFinderScreen:
    """
    Map and list view of nearby buy-low / sell-high flip opportunities.

    Fields
    ------
    location         : User's current location or manually entered city.
    budget           : Maximum buy price per item.
    flips            : Ranked list of flip opportunities from flipBot.
    selected_category: Active category filter.
    selected_source  : Active source/platform filter.
    min_profit_pct   : Minimum profit % filter.
    map_view         : Whether map view is active.
    last_updated     : ISO timestamp.
    """

    SCREEN_NAME = "FlipFinderScreen"
    ROUTE = "/flips"

    def __init__(
        self,
        location: str = "New York",
        budget: float = 200.0,
        flips: list = None,
        selected_category: str = "all",
        selected_source: str = "all",
        min_profit_pct: float = 30.0,
        map_view: bool = False,
    ):
        self.location = location
        self.budget = budget
        self.flips = flips or []
        self.selected_category = selected_category
        self.selected_source = selected_source
        self.min_profit_pct = min_profit_pct
        self.map_view = map_view
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        top_flip = max(self.flips, key=lambda f: f.get("profitPct", 0), default=None)
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "search_bar": {
                    "location": self.location,
                    "budget": f"${self.budget:.0f}",
                    "placeholder": "Enter city or zip code",
                },
                "filter_row": {
                    "category": self.selected_category,
                    "source": self.selected_source,
                    "min_profit_pct": f"{self.min_profit_pct:.0f}%+",
                },
                "view_toggle": {"map_view": self.map_view},
                "top_flip_banner": top_flip or {},
                "flips_list": {
                    "count": len(self.flips),
                    "items": self.flips,
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "location": self.location,
            "budget": self.budget,
            "flips": self.flips,
            "selected_category": self.selected_category,
            "selected_source": self.selected_source,
            "min_profit_pct": self.min_profit_pct,
            "map_view": self.map_view,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "FlipFinderScreen":
        return cls(
            location="Los Angeles",
            budget=300.0,
            flips=[
                {"id": "FLIP-10001", "name": "Vintage Console", "source": "facebook_marketplace",
                 "category": "electronics", "buyPrice": 25, "estimatedSellPrice": 120,
                 "profit": 95, "profitPct": 380.0, "condition": "good"},
                {"id": "FLIP-10002", "name": "Refurb Laptop", "source": "craigslist",
                 "category": "electronics", "buyPrice": 80, "estimatedSellPrice": 250,
                 "profit": 170, "profitPct": 212.5, "condition": "like_new"},
                {"id": "FLIP-10003", "name": "Antique Chair", "source": "offerup",
                 "category": "furniture", "buyPrice": 15, "estimatedSellPrice": 75,
                 "profit": 60, "profitPct": 400.0, "condition": "fair"},
            ],
            selected_category="electronics",
            min_profit_pct=50.0,
        )
