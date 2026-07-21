from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 299.0, ["tax-loss harvesting engine", "capital gains deferral"]),
    "enterprise": TierConfig("Enterprise", 599.0, ["tax-loss harvesting engine", "capital gains deferral", "wash sale monitoring", "multi-account optimization"]),
}
