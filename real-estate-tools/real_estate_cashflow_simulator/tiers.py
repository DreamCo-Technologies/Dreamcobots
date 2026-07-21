from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["single property cashflow", "basic metrics"]),
    "pro": TierConfig("Pro", 34.0, ["multi-property portfolio", "IRR calculation", "amortization schedule"]),
    "enterprise": TierConfig("Enterprise", 129.0, ["all features", "multi-entity analysis", "tax projection", "API access"]),
}
