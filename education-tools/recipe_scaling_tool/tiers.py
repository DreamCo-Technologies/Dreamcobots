from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["10 recipes/month", "basic scaling", "unit conversion"]),
    "pro": TierConfig("Pro", 14.0, ["unlimited recipes", "nutritional info", "shopping list export"]),
    "enterprise": TierConfig("Enterprise", 49.0, ["all features", "batch cooking planner", "allergen tracking", "API access"]),
}
