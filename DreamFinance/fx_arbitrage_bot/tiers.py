from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["triangular arbitrage detection", "cross-rate discrepancy scanning"]),
    "elite": TierConfig("Elite", 1500.0, ["triangular arbitrage detection", "cross-rate discrepancy scanning", "latency-optimized execution", "multi-venue routing"]),
}
