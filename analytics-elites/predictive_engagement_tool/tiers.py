from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["engagement score", "basic segmentation"]),
    "pro": TierConfig("Pro", 59.0, ["churn prediction", "re-engagement campaigns", "cohort analysis"]),
    "enterprise": TierConfig("Enterprise", 249.0, ["all features", "real-time scoring", "A/B test integration", "API access"]),
}
