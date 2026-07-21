from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 499.0, ["risk profiling questionnaires", "goal-based portfolio construction", "automatic rebalancing"]),
    "elite": TierConfig("Elite", 2500.0, ["risk profiling questionnaires", "goal-based portfolio construction", "automatic rebalancing", "tax-loss harvesting", "dedicated support"]),
}
