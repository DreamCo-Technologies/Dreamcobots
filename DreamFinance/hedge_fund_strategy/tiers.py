from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["long/short equity strategies", "factor exposure analysis"]),
    "elite": TierConfig("Elite", 2500.0, ["long/short equity strategies", "event-driven alpha signals", "factor exposure analysis", "portfolio construction"]),
}
