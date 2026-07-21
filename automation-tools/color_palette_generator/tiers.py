from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["5 palettes/month", "basic color schemes"]),
    "pro": TierConfig("Pro", 19.0, ["unlimited palettes", "brand color analysis", "export PNG/SVG"]),
    "enterprise": TierConfig("Enterprise", 79.0, ["all features", "AI color matching", "team workspaces", "API access"]),
}
