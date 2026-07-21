from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["cash position forecasting", "liquidity gap analysis", "FX exposure management"]),
    "elite": TierConfig("Elite", 2500.0, ["cash position forecasting", "liquidity gap analysis", "FX exposure management", "investment policy monitoring"]),
}
