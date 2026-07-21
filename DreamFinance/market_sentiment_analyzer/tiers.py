from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "pro": TierConfig("Pro", 199.0, ["news sentiment NLP", "social media pulse tracking"]),
    "enterprise": TierConfig("Enterprise", 499.0, ["news sentiment NLP", "social media pulse tracking", "SEC filing analysis", "priority support"]),
}
