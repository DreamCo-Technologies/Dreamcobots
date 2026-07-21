from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 299.0, ["strategy backtesting engine"]),
    "enterprise": TierConfig("Enterprise", 999.0, ["strategy backtesting engine", "risk-adjusted position sizing"]),
    "elite": TierConfig("Elite", 2500.0, ["high-frequency order execution", "strategy backtesting engine", "risk-adjusted position sizing", "co-location support"]),
}
