from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["basic audit", "5S scoring"]),
    "pro": TierConfig("Pro", 29.0, ["basic audit", "5S scoring", "detailed reports", "trend analysis"]),
    "enterprise": TierConfig("Enterprise", 99.0, ["all features", "multi-location", "custom templates"]),
}
