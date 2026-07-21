from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["basic ROI simulation", "3 scenarios"]),
    "pro": TierConfig("Pro", 49.0, ["unlimited scenarios", "churn impact", "CLV modeling", "reports"]),
    "enterprise": TierConfig("Enterprise", 199.0, ["all features", "multi-program comparison", "cohort analysis", "API access"]),
}
