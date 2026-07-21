from dataclasses import dataclass, field


@dataclass
class TierConfig:
    name: str
    price_usd_monthly: float
    features: list = field(default_factory=list)


TIERS = {
    "free": TierConfig("Free", 0.0, ["moving average signals", "3 symbols/month"]),
    "pro": TierConfig("Pro", 99.0, ["RSI signals", "MACD", "backtesting", "10 symbols"]),
    "enterprise": TierConfig("Enterprise", 499.0, ["all indicators", "unlimited symbols", "live trading hooks", "portfolio analytics"]),
}
