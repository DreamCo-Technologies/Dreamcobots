"""Forecasting Tools Bot — tier-aware revenue forecasting, seasonality, and scenario planning."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config
from bots.forecasting_tools_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class ForecastingToolsBot:
    """Tier-aware revenue forecasting and scenario planning bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="ForecastingToolsBot")

    def forecast_revenue(self, historical_data: list, periods: int = 12) -> dict:
        if self.tier == Tier.FREE:
            periods = min(periods, 3)

        if not historical_data or len(historical_data) < 2:
            raise ValueError("historical_data must contain at least 2 data points")

        growth_rates = [
            (historical_data[i] - historical_data[i - 1]) / historical_data[i - 1]
            for i in range(1, len(historical_data))
            if historical_data[i - 1] != 0
        ]
        avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0

        last_value = historical_data[-1]
        forecast = []
        for _ in range(periods):
            last_value = last_value * (1 + avg_growth_rate)
            forecast.append(round(last_value, 2))

        confidence_interval = None
        if self.tier != Tier.FREE and forecast:
            std_dev = (sum((r - avg_growth_rate) ** 2 for r in growth_rates) / len(growth_rates)) ** 0.5 if growth_rates else 0.0
            margin = historical_data[-1] * std_dev * 1.96
            confidence_interval = {
                "lower": [round(v - margin, 2) for v in forecast],
                "upper": [round(v + margin, 2) for v in forecast],
            }

        return {
            "forecast": forecast,
            "periods": periods,
            "method": "linear_trend",
            "growth_rate": round(avg_growth_rate * 100, 4),
            "confidence_interval": confidence_interval,
            "tier_used": self.tier.value,
        }

    def calculate_growth_rate(self, historical_values: list) -> dict:
        if not historical_values or len(historical_values) < 2:
            raise ValueError("historical_values must contain at least 2 data points")

        period_growth_rates = []
        for i in range(1, len(historical_values)):
            prev = historical_values[i - 1]
            curr = historical_values[i]
            rate = ((curr - prev) / prev * 100) if prev != 0 else 0.0
            period_growth_rates.append(round(rate, 4))

        avg_growth_rate = sum(period_growth_rates) / len(period_growth_rates)

        first = historical_values[0]
        last = historical_values[-1]
        n = len(historical_values) - 1
        cagr = ((last / first) ** (1 / n) - 1) * 100 if first != 0 and n > 0 else 0.0

        total_growth_pct = ((last - first) / first * 100) if first != 0 else 0.0

        return {
            "cagr": round(cagr, 4),
            "period_growth_rates": period_growth_rates,
            "avg_growth_rate": round(avg_growth_rate, 4),
            "total_growth_pct": round(total_growth_pct, 4),
            "tier_used": self.tier.value,
        }

    def detect_seasonality(self, data_points: list) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Seasonality detection requires PRO or ENTERPRISE tier")
        if len(data_points) < 4:
            raise ValueError("At least 4 data points are required for seasonality detection")

        # Split into quarters (groups of equal size where possible)
        n = len(data_points)
        quarter_size = max(1, n // 4)
        quarters = [data_points[i * quarter_size: (i + 1) * quarter_size] for i in range(4)]
        # Include any remainder in the last quarter
        remainder = data_points[4 * quarter_size:]
        if remainder:
            quarters[3] = quarters[3] + remainder

        quarter_avgs = [sum(q) / len(q) if q else 0 for q in quarters]
        overall_avg = sum(data_points) / len(data_points) if data_points else 1
        seasonal_indices = [round(avg / overall_avg, 4) if overall_avg != 0 else 1.0 for avg in quarter_avgs]

        max_idx = max(seasonal_indices)
        min_idx = min(seasonal_indices)
        has_seasonality = (max_idx / min_idx) > 1.2 if min_idx != 0 else False
        pattern = "quarterly" if has_seasonality else "none"

        return {
            "seasonal_indices": seasonal_indices,
            "has_seasonality": has_seasonality,
            "pattern": pattern,
            "tier_used": self.tier.value,
        }

    def build_scenario(self, base_forecast: list, assumptions: dict) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Scenario planning requires PRO or ENTERPRISE tier")
        if not base_forecast:
            raise ValueError("base_forecast must be a non-empty list")

        optimistic_growth = assumptions.get("optimistic_growth_pct", 20) / 100
        pessimistic_decline = assumptions.get("pessimistic_decline_pct", 15) / 100

        optimistic = [round(v * (1 + optimistic_growth), 2) for v in base_forecast]
        pessimistic = [round(v * (1 - pessimistic_decline), 2) for v in base_forecast]

        return {
            "base": base_forecast,
            "optimistic": optimistic,
            "pessimistic": pessimistic,
            "tier_used": self.tier.value,
        }

    def run(self):
        return self.flow.run_pipeline(
            raw_data={"domain": "forecasting"},
            learning_method="supervised",
        )
