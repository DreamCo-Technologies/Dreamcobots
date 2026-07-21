from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 99.0, ["LP position management", "impermanent loss calculator"]),
    "enterprise": TierConfig("Enterprise", 299.0, ["LP position management", "impermanent loss calculator", "auto-harvest scheduling", "gas optimization"]),
}
