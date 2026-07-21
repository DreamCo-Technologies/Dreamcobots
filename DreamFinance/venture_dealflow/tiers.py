from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["deal sourcing automation", "due diligence screening", "portfolio monitoring"]),
    "elite": TierConfig("Elite", 2500.0, ["deal sourcing automation", "due diligence screening", "portfolio monitoring", "LP reporting", "co-investment network"]),
}
