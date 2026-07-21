"""Mining Bot — tier-aware cryptocurrency mining management."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.mining_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class MiningBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class MiningBot:
    """Tier-aware cryptocurrency mining management bot."""

    COIN_LIMITS = {
        Tier.FREE: ["BTC"],
        Tier.PRO: ["BTC", "ETH", "LTC", "RVN", "ERG"],
        Tier.ENTERPRISE: ["BTC", "ETH", "LTC", "RVN", "ERG", "FLUX", "KAS", "XMR", "DOGE", "ZEC"],
    }

    COIN_DATA = {
        "BTC": {"name": "Bitcoin", "algorithm": "SHA-256", "hashrate_th": 120.5, "daily_revenue_usd": 8.42, "power_w": 3250, "network_difficulty": "Very High", "price_usd": 65000},
        "ETH": {"name": "Ethereum", "algorithm": "Ethash", "hashrate_mh": 95.0, "daily_revenue_usd": 4.21, "power_w": 220, "network_difficulty": "High", "price_usd": 3500},
        "LTC": {"name": "Litecoin", "algorithm": "Scrypt", "hashrate_mh": 1000.0, "daily_revenue_usd": 1.85, "power_w": 1500, "network_difficulty": "Medium", "price_usd": 85},
        "RVN": {"name": "Ravencoin", "algorithm": "KawPoW", "hashrate_mh": 25.0, "daily_revenue_usd": 1.12, "power_w": 180, "network_difficulty": "Low", "price_usd": 0.025},
        "ERG": {"name": "Ergo", "algorithm": "Autolykos2", "hashrate_mh": 200.0, "daily_revenue_usd": 2.35, "power_w": 200, "network_difficulty": "Medium", "price_usd": 1.85},
        "FLUX": {"name": "Flux", "algorithm": "ZelHash", "hashrate_ksol": 50.0, "daily_revenue_usd": 1.60, "power_w": 190, "network_difficulty": "Low", "price_usd": 0.65},
        "KAS": {"name": "Kaspa", "algorithm": "kHeavyHash", "hashrate_th": 5.0, "daily_revenue_usd": 3.20, "power_w": 2400, "network_difficulty": "Medium", "price_usd": 0.12},
        "XMR": {"name": "Monero", "algorithm": "RandomX", "hashrate_kh": 14.0, "daily_revenue_usd": 0.95, "power_w": 90, "network_difficulty": "Medium", "price_usd": 175},
        "DOGE": {"name": "Dogecoin", "algorithm": "Scrypt", "hashrate_mh": 1200.0, "daily_revenue_usd": 1.45, "power_w": 1500, "network_difficulty": "Medium", "price_usd": 0.12},
        "ZEC": {"name": "Zcash", "algorithm": "Equihash", "hashrate_ksol": 500.0, "daily_revenue_usd": 1.10, "power_w": 1400, "network_difficulty": "Medium", "price_usd": 28},
    }

    EXCHANGES = ["Binance", "Coinbase", "Kraken", "KuCoin", "Bybit"]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._current_coin = "BTC"
        self._auto_withdraw_threshold: float = None
        self._earnings: float = 0.0

    def scan_coins(self) -> list:
        """Return list of mineable coins with profitability data."""
        allowed = self.COIN_LIMITS[self.tier]
        return [
            {
                "coin": symbol,
                **data,
                "available_on_tier": symbol in allowed,
            }
            for symbol, data in self.COIN_DATA.items()
            if symbol in allowed
        ]

    def get_current_coin(self) -> str:
        """Return the coin currently being mined."""
        return self._current_coin

    def switch_coin(self, coin: str) -> dict:
        """Switch to mining a different coin."""
        allowed = self.COIN_LIMITS[self.tier]
        coin_upper = coin.upper()
        if coin_upper not in allowed:
            raise MiningBotTierError(
                f"Coin '{coin_upper}' not available on {self.config.name} tier. "
                f"Allowed: {allowed}. Upgrade to mine more coins."
            )
        if coin_upper not in self.COIN_DATA:
            raise ValueError(f"Unknown coin: {coin_upper}")
        self._current_coin = coin_upper
        return {
            "switched_to": coin_upper,
            "coin_data": self.COIN_DATA[coin_upper],
            "message": f"Now mining {coin_upper} ({self.COIN_DATA[coin_upper]['name']})",
            "tier": self.tier.value,
        }

    def track_profitability(self) -> dict:
        """Return current profitability metrics."""
        coin_data = self.COIN_DATA[self._current_coin]
        daily = coin_data["daily_revenue_usd"]
        electricity_cost = coin_data.get("power_w", 200) * 24 / 1000 * 0.10
        net_daily = daily - electricity_cost

        result = {
            "current_coin": self._current_coin,
            "daily_gross_usd": round(daily, 2),
            "electricity_cost_usd": round(electricity_cost, 2),
            "net_daily_usd": round(net_daily, 2),
            "monthly_net_usd": round(net_daily * 30, 2),
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            best = max(
                (c for c in self.COIN_LIMITS[self.tier]),
                key=lambda c: self.COIN_DATA[c]["daily_revenue_usd"]
            )
            result["most_profitable_coin"] = best
            result["profit_tracking_enabled"] = True
        if self.tier == Tier.ENTERPRISE:
            result["portfolio_optimization"] = {coin: self.COIN_DATA[coin]["daily_revenue_usd"] for coin in self.COIN_LIMITS[self.tier]}
        return result

    def auto_withdraw(self, threshold: float) -> dict:
        """Set up auto-withdrawal (PRO+ only)."""
        if self.tier == Tier.FREE:
            raise MiningBotTierError("Auto-withdraw is not available on the FREE tier. Upgrade to PRO or ENTERPRISE.")
        self._auto_withdraw_threshold = threshold
        return {
            "auto_withdraw_enabled": True,
            "threshold_usd": threshold,
            "current_coin": self._current_coin,
            "message": f"Auto-withdraw set: will withdraw when earnings reach ${threshold:.2f}",
            "tier": self.tier.value,
        }

    def multi_exchange_route(self, amount: float) -> dict:
        """Calculate optimal multi-exchange routing (ENTERPRISE only)."""
        if self.tier != Tier.ENTERPRISE:
            raise MiningBotTierError("Multi-exchange routing is only available on ENTERPRISE tier.")
        splits = [round(amount / len(self.EXCHANGES), 2) for _ in self.EXCHANGES]
        splits[-1] = round(amount - sum(splits[:-1]), 2)
        return {
            "total_amount_usd": amount,
            "routing": [{"exchange": ex, "amount_usd": sp} for ex, sp in zip(self.EXCHANGES, splits)],
            "estimated_fees_usd": round(amount * 0.001, 2),
            "net_received_usd": round(amount * 0.999, 2),
            "tier": self.tier.value,
        }

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Mining Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
