from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["5 meetings/month", "basic scheduling"]),
    "pro": TierConfig("Pro", 24.0, ["unlimited meetings", "timezone support", "conflict detection", "reminders"]),
    "enterprise": TierConfig("Enterprise", 89.0, ["all features", "calendar sync", "analytics", "API access"]),
}
