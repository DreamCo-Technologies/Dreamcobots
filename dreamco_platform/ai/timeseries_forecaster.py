from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Sequence
import math

class TSModel(str, Enum):
    ARIMA = 'ARIMA'
    EXPONENTIAL_SMOOTHING = 'Exponential Smoothing'
    HOLT_WINTERS = 'Holt-Winters'

@dataclass
class Forecast:
    values: List[float]
    lower_band: List[float]
    upper_band: List[float]
    anomalies: List[int]

@dataclass
class FittedModel:
    model_type: str
    level: float
    trend: float
    seasonality: List[float]
    residual_std: float


class TSForecaster:
    def fit(self, historical_data: Sequence[float]) -> FittedModel:
        if len(historical_data) < 3:
            raise ValueError('historical_data must contain at least 3 points')
        level = historical_data[0]
        trend = historical_data[1] - historical_data[0]
        alpha, beta = 0.5, 0.3
        residuals: List[float] = []
        for value in historical_data[1:]:
            prev_level = level
            level = alpha * value + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
            residuals.append(value - (prev_level + trend))
        seasonality = self._seasonality(historical_data)
        std = math.sqrt(sum(r * r for r in residuals) / max(len(residuals), 1))
        model_type = TSModel.HOLT_WINTERS.value if len(historical_data) >= 12 else TSModel.EXPONENTIAL_SMOOTHING.value
        return FittedModel(model_type=model_type, level=level, trend=trend, seasonality=seasonality, residual_std=std)

    def predict(self, model: FittedModel, periods: int = 30) -> Forecast:
        values, lower, upper = [], [], []
        for step in range(1, periods + 1):
            seasonal = model.seasonality[(step - 1) % len(model.seasonality)] if model.seasonality else 0.0
            forecast = model.level + model.trend * step + seasonal
            margin = 1.96 * model.residual_std * math.sqrt(step)
            values.append(round(forecast, 3))
            lower.append(round(forecast - margin, 3))
            upper.append(round(forecast + margin, 3))
        anomalies = [idx for idx, value in enumerate(values) if value < lower[idx] or value > upper[idx]]
        return Forecast(values=values, lower_band=lower, upper_band=upper, anomalies=anomalies)

    def _seasonality(self, data: Sequence[float], period: int = 7) -> List[float]:
        if len(data) < period * 2:
            return [0.0]
        averages = [sum(data[i::period]) / len(data[i::period]) for i in range(period)]
        baseline = sum(data) / len(data)
        return [avg - baseline for avg in averages]



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
