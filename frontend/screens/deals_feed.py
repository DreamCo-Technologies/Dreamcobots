"""DealsFeedScreen — browsable feed of ranked deals."""


class DealsFeedScreen:
    SCREEN_ID = "deals_feed"

    def __init__(self, deals=None, category=None, sort_by="rank_score"):
        self.deals = deals or []
        self.category = category
        self.sort_by = sort_by

    def render(self) -> str:
        filtered = [d for d in self.deals if not self.category or d.get("category") == self.category]
        lines = [
            "=== DreamCo — Deals Feed ===",
            f"Category: {self.category or 'All'}",
            f"Total Deals: {len(filtered)}",
        ]
        for d in filtered[:5]:
            lines.append(f"  [{d.get('rank_score', 0)}/100] {d.get('name', '?')} — ${d.get('profit', 0):.2f}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "deals": self.deals,
            "category": self.category,
            "sort_by": self.sort_by,
        }

    @classmethod
    def demo(cls) -> "DealsFeedScreen":
        return cls(
            deals=[
                {"name": "iPad Air", "category": "electronics", "profit": 60.0, "rank_score": 85},
                {"name": "KitchenAid Mixer", "category": "appliances", "profit": 45.0, "rank_score": 72},
                {"name": "Lego Set", "category": "toys", "profit": 22.0, "rank_score": 55},
            ],
        )
