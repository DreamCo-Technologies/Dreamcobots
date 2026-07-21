from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["compound lookup", "basic property screening"]),
    "pro": TierConfig("Pro", 199.0, ["ADMET prediction", "target docking score", "lead optimization hints"]),
    "enterprise": TierConfig("Enterprise", 999.0, ["all features", "multi-target screening", "patent check", "API access"]),
}
