"""
Dreamcobots Revenue Growth Bot — tier-aware revenue analytics and pricing optimization.

Usage
-----
    from revenue_growth_bot import RevenueGrowthBot
    from tiers import Tier

    bot = RevenueGrowthBot(tier=Tier.FREE)
    result = bot.analyze_revenue({"sales": [100, 200, 150]})
    print(result)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_revenue_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_revenue_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_revenue_tiers)
REVENUE_FEATURES = _revenue_tiers.REVENUE_FEATURES
PRODUCT_LIMITS = _revenue_tiers.PRODUCT_LIMITS
get_revenue_tier_info = _revenue_tiers.get_revenue_tier_info


class RevenueGrowthBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class RevenueGrowthBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class RevenueGrowthBot:
    """
    Tier-aware revenue analytics and pricing optimization bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability and request limits.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._products: list[dict] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def analyze_revenue(self, data: dict) -> dict:
        """
        Analyze revenue data and return key metrics.

        Parameters
        ----------
        data : dict
            Revenue data containing sales figures, periods, etc.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        sales = data.get("sales", [])
        total = sum(sales) if sales else 0.0
        avg = total / len(sales) if sales else 0.0
        metrics = {
            "total_revenue": total,
            "average_revenue": round(avg, 2),
            "periods": len(sales),
            "trend": "up" if len(sales) >= 2 and sales[-1] > sales[0] else "flat",
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            metrics["growth_rate_pct"] = (
                round(((sales[-1] - sales[0]) / sales[0]) * 100, 2)
                if len(sales) >= 2 and sales[0] != 0
                else 0.0
            )
        return {
            "metrics": metrics,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def optimize_pricing(self, product: dict) -> dict:
        """
        Suggest an optimized price for a product.  Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        product : dict
            Product details including current price, cost, and demand data.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier == Tier.FREE:
            raise RevenueGrowthBotTierError(
                "Pricing optimization requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        current_price = product.get("current_price", 0)
        suggested_price = round(current_price * 1.15, 2)
        return {
            "product_name": product.get("name", "Unknown"),
            "current_price": current_price,
            "suggested_price": suggested_price,
            "estimated_revenue_lift_pct": 12.5,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def forecast_revenue(self, period_months: int = 3) -> dict:
        """
        Forecast revenue for upcoming months.  Requires ENTERPRISE tier.

        Parameters
        ----------
        period_months : int
            Number of months to forecast.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier != Tier.ENTERPRISE:
            raise RevenueGrowthBotTierError(
                "Revenue forecasting is only available on the ENTERPRISE tier."
            )
        self._request_count += 1
        forecasts = [
            {"month": i + 1, "predicted_revenue": 10_000 * (1.05 ** i)}
            for i in range(period_months)
        ]
        return {
            "period_months": period_months,
            "forecasts": forecasts,
            "model": "AI pricing engine (mock)",
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_revenue_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        product_limit = (
            "Unlimited"
            if info["product_limit"] is None
            else str(info["product_limit"])
        )
        lines = [
            f"=== {info['name']} Revenue Growth Bot Tier ===",
            f"Price         : ${info['price_usd_monthly']:.2f}/month",
            f"Requests      : {limit}/month",
            f"Product limit : {product_limit}",
            f"Support       : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["revenue_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(REVENUE_FEATURES[self.tier.value])
        new_feats = [f for f in REVENUE_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing RevenueGrowthBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise RevenueGrowthBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = RevenueGrowthBot(tier=Tier.FREE)
    bot.describe_tier()
    result = bot.analyze_revenue({"sales": [1000, 1200, 1100, 1400]})
    print(result)
