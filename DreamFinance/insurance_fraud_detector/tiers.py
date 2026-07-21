from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["claim anomaly scoring", "network fraud analysis", "document verification AI"]),
    "elite": TierConfig("Elite", 2500.0, ["claim anomaly scoring", "network fraud analysis", "document verification AI", "real-time alerts"]),
}
