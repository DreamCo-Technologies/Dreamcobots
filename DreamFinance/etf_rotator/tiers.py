from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 199.0, ["sector momentum scoring", "factor tilt optimization"]),
    "enterprise": TierConfig("Enterprise", 499.0, ["sector momentum scoring", "factor tilt optimization", "rebalancing signal generation", "advanced analytics"]),
}
