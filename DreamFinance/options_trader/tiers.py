from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 299.0, ["options chain scanner", "iron condor automation"]),
    "enterprise": TierConfig("Enterprise", 599.0, ["options chain scanner", "iron condor automation", "spread strategy builder", "Greeks dashboard"]),
}
