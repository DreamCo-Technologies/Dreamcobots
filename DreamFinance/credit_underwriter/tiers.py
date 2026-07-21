from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 999.0, ["credit scoring models", "default probability estimation", "fraud pattern detection"]),
    "elite": TierConfig("Elite", 2500.0, ["credit scoring models", "default probability estimation", "fraud pattern detection", "real-time decisioning"]),
}
