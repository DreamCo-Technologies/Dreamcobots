from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 199.0, ["currency pair correlation", "technical signal engine"]),
    "enterprise": TierConfig("Enterprise", 499.0, ["currency pair correlation", "technical signal engine", "economic calendar integration", "multi-broker execution"]),
}
