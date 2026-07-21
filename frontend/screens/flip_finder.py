"""FlipFinderScreen — local resale flip opportunities."""


class FlipFinderScreen:
    SCREEN_ID = "flip_finder"

    def __init__(self, flips=None, city="Local", min_profit=20.0):
        self.flips = flips or []
        self.city = city
        self.min_profit = min_profit

    def render(self) -> str:
        lines = [
            "=== DreamCo — Flip Finder ===",
            f"City: {self.city}",
            f"Min Profit: ${self.min_profit:.2f}",
            f"Flips Found: {len(self.flips)}",
        ]
        for flip in self.flips[:3]:
            lines.append(
                f"  • {flip.get('name', '?')} — Buy ${flip.get('buyPrice', 0):.2f} → Sell ${flip.get('sellPrice', 0):.2f} = ${flip.get('profit', 0):.2f}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "flips": self.flips,
            "city": self.city,
            "min_profit": self.min_profit,
        }

    @classmethod
    def demo(cls) -> "FlipFinderScreen":
        return cls(
            flips=[
                {"name": "PS4 Console", "buyPrice": 80.0, "sellPrice": 150.0, "profit": 70.0},
                {"name": "IKEA Shelf", "buyPrice": 15.0, "sellPrice": 55.0, "profit": 40.0},
            ],
            city="Atlanta",
            min_profit=20.0,
        )
