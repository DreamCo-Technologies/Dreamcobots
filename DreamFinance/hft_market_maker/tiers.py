from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "elite": TierConfig("Elite", 2500.0, ["market making algorithms", "spread optimization engine", "latency arbitrage detection"]),
}
