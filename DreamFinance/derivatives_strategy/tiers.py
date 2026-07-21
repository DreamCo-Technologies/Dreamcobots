from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["options pricing models", "Greeks calculation engine"]),
    "elite": TierConfig("Elite", 1500.0, ["options pricing models", "Greeks calculation engine", "volatility surface modeling", "portfolio-level Greeks"]),
}
