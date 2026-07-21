from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 499.0, ["anomaly pattern recognition", "dark pool print alerts"]),
    "elite": TierConfig("Elite", 2500.0, ["anomaly pattern recognition", "dark pool print alerts", "unusual options activity", "real-time feeds"]),
}
