from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["PHQ-2 screening", "basic risk indicator"]),
    "pro": TierConfig("Pro", 39.0, ["PHQ-9 screening", "GAD-7 screening", "detailed risk report", "resource referrals"]),
    "enterprise": TierConfig("Enterprise", 149.0, ["all features", "custom questionnaires", "EHR integration", "analytics dashboard"]),
}
