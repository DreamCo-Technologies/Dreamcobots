from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 99.0, ["penny stock screener", "volume spike detection"]),
    "enterprise": TierConfig("Enterprise", 299.0, ["penny stock screener", "volume spike detection", "SEC filing alerts", "real-time scanning"]),
}
