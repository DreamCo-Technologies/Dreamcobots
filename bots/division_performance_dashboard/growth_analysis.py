# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from dataclasses import dataclass
from typing import Optional
import math

@dataclass
class GrowthMetric:
    period: str
    value: float
    previous_value: float
    growth_rate: float
    growth_type: str  # "mom" / "yoy" / "cagr"

class GrowthAnalysis:
    def calculate_mom_growth(self, current: float, previous: float) -> float:
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100

    def calculate_yoy_growth(self, current: float, previous: float) -> float:
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100

    def calculate_cagr(self, initial: float, final: float, years: int) -> float:
        if initial <= 0 or years <= 0:
            return 0.0
        return ((final / initial) ** (1 / years) - 1) * 100

    def analyze_division(self, division_id: str, revenue_data: list) -> dict:
        if len(revenue_data) < 2:
            return {"division_id": division_id, "mom_growth": 0.0, "trend": "stable", "records": len(revenue_data)}
        values = [r.revenue_usd if hasattr(r, 'revenue_usd') else r for r in revenue_data]
        mom = self.calculate_mom_growth(values[-1], values[-2])
        return {
            "division_id": division_id,
            "mom_growth": mom,
            "trend": self.get_growth_trend(values),
            "records": len(revenue_data),
            "latest_revenue": values[-1],
        }

    def get_growth_trend(self, values: list) -> str:
        if len(values) < 2:
            return "stable"
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
        decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
        ratio = len(values) - 1
        if increases / ratio >= 0.6:
            return "growing"
        elif decreases / ratio >= 0.6:
            return "declining"
        return "stable"

    def project_revenue(self, current: float, growth_rate: float, periods: int) -> list:
        result = []
        value = current
        rate = growth_rate / 100
        for _ in range(periods):
            value = value * (1 + rate)
            result.append(round(value, 2))
        return result

    def benchmark_growth(self, division_id: str, industry_avg: float, actual_growth: float) -> dict:
        diff = actual_growth - industry_avg
        return {
            "division_id": division_id,
            "actual_growth": actual_growth,
            "industry_avg": industry_avg,
            "outperformance": diff,
            "status": "outperforming" if diff > 0 else ("underperforming" if diff < 0 else "at_benchmark"),
        }
