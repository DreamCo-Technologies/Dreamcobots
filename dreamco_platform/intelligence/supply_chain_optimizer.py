"""Supply chain planning helpers for inventory and routing trade-offs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class SupplierQuote:
    supplier: str
    unit_cost: float
    capacity: int
    lead_time_days: int
    reliability: float


class SupplyChainOptimizer:
    def rank_suppliers(self, quotes: Iterable[SupplierQuote], demand: int) -> List[Dict[str, float | str]]:
        ranked = []
        for quote in quotes:
            fill_rate = min(1.0, quote.capacity / max(demand, 1))
            service_score = quote.reliability * 0.5 + fill_rate * 0.3 + (1 / max(quote.lead_time_days, 1)) * 0.2
            total_score = service_score / max(quote.unit_cost, 0.01)
            ranked.append({
                "supplier": quote.supplier,
                "fill_rate": round(fill_rate, 3),
                "service_score": round(service_score, 3),
                "value_score": round(total_score, 3),
            })
        return sorted(ranked, key=lambda item: item["value_score"], reverse=True)

    def allocate_orders(self, quotes: Iterable[SupplierQuote], demand: int) -> List[Dict[str, float | int | str]]:
        remaining = demand
        allocations: List[Dict[str, float | int | str]] = []
        for entry in self.rank_suppliers(quotes, demand):
            quote = next(q for q in quotes if q.supplier == entry["supplier"])
            quantity = min(quote.capacity, remaining)
            if quantity <= 0:
                continue
            remaining -= quantity
            allocations.append({
                "supplier": quote.supplier,
                "quantity": quantity,
                "expected_cost": round(quantity * quote.unit_cost, 2),
                "lead_time_days": quote.lead_time_days,
            })
            if remaining == 0:
                break
        if remaining > 0:
            allocations.append({"supplier": "unfilled", "quantity": remaining, "expected_cost": 0.0, "lead_time_days": 0})
        return allocations

    def reorder_point(self, daily_demand: float, lead_time_days: int, safety_stock: int, variability: float = 0.1) -> int:
        cycle_stock = daily_demand * lead_time_days
        buffer = safety_stock + round(cycle_stock * variability)
        return int(round(cycle_stock + buffer))

    def logistics_risk(self, allocations: Iterable[Dict[str, float | int | str]]) -> Dict[str, float]:
        items = list(allocations)
        if not items:
            return {"cost_exposure": 0.0, "delay_risk": 0.0}
        total_cost = sum(float(item["expected_cost"]) for item in items)
        total_quantity = sum(int(item["quantity"]) for item in items)
        delay_risk = sum(int(item["quantity"]) * int(item["lead_time_days"]) for item in items if item["supplier"] != "unfilled")
        return {
            "cost_exposure": round(total_cost, 2),
            "delay_risk": round(delay_risk / max(total_quantity, 1), 2),
        }


def scenario_report(quotes: Iterable[SupplierQuote], demand: int) -> Dict[str, object]:
    optimizer = SupplyChainOptimizer()
    allocations = optimizer.allocate_orders(list(quotes), demand)
    return {
        "allocations": allocations,
        "risk": optimizer.logistics_risk(allocations),
    }
