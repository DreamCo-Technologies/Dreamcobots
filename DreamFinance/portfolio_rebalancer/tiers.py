from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 299.0, ["drift threshold monitoring", "tax-aware rebalancing"]),
    "enterprise": TierConfig("Enterprise", 599.0, ["drift threshold monitoring", "tax-aware rebalancing", "multi-account coordination", "wash sale prevention"]),
}
