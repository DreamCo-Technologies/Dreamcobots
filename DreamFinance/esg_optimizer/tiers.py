from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "enterprise": TierConfig("Enterprise", 499.0, ["ESG scoring framework", "carbon footprint tracking", "impact measurement dashboard"]),
    "elite": TierConfig("Elite", 2500.0, ["ESG scoring framework", "carbon footprint tracking", "impact measurement dashboard", "third-party ESG data feeds"]),
}
