from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class RevenueForecast:
    point_estimate: float
    confidence_interval_90: Tuple[float, float]
    scenario_best: float
    scenario_worst: float


class RevenueForecaster:
    def forecast(self, records: Iterable[dict], horizon_days: int = 30) -> RevenueForecast:
        history = list(records)
        arima = self._arima(history)
        prophet = self._prophet_like(history, horizon_days)
        linear = self._linear_regression(history, horizon_days)
        point = (arima + prophet + linear) / 3
        spread = max(point * 0.12, 1.0)
        return RevenueForecast(round(point, 2), (round(point - spread, 2), round(point + spread, 2)), round(point * 1.15, 2), round(point * 0.82, 2))

    def _arima(self, history: List[dict]) -> float:
        if len(history) < 2:
            return history[0]['historical_revenue'] if history else 0.0
        diffs = [history[index]['historical_revenue'] - history[index - 1]['historical_revenue'] for index in range(1, len(history))]
        return history[-1]['historical_revenue'] + sum(diffs[-3:]) / max(1, min(len(diffs), 3))

    def _prophet_like(self, history: List[dict], horizon_days: int) -> float:
        if not history:
            return 0.0
        last = history[-1]
        growth = last.get('new_bots_added', 0) * 180 - last.get('churn_rate', 0) * last['historical_revenue']
        seasonality = (horizon_days / 30) * last.get('active_bots', 0) * 12
        return last['historical_revenue'] + growth + seasonality

    def _linear_regression(self, history: List[dict], horizon_days: int) -> float:
        if not history:
            return 0.0
        last = history[-1]
        tier_bonus = sum(last.get('tier_distribution', {}).values()) * 25
        return last['historical_revenue'] + last.get('active_bots', 0) * 20 + tier_bonus - last.get('churn_rate', 0) * 1000 + horizon_days * 10
