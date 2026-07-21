from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 99.0, ["multi-exchange execution", "DCA strategy engine"]),
    "enterprise": TierConfig("Enterprise", 299.0, ["multi-exchange execution", "DCA strategy engine", "grid trading automation", "arbitrage scanning"]),
}
