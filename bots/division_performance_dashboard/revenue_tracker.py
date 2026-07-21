# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class DivisionRevenue:
    division_id: str
    division_name: str
    revenue_usd: float
    expenses_usd: float
    month: str
    year: int

class RevenueTracker:
    def __init__(self):
        self._records: list = []

    def record_revenue(self, division_id, division_name, revenue_usd, expenses_usd, month, year) -> DivisionRevenue:
        rec = DivisionRevenue(division_id, division_name, revenue_usd, expenses_usd, month, year)
        self._records.append(rec)
        return rec

    def get_total_revenue(self, year: int = None) -> float:
        records = self._records if year is None else [r for r in self._records if r.year == year]
        return sum(r.revenue_usd for r in records)

    def get_division_revenue(self, division_id: str) -> list:
        return [r for r in self._records if r.division_id == division_id]

    def get_profit(self, division_id: str = None) -> float:
        if division_id:
            records = [r for r in self._records if r.division_id == division_id]
        else:
            records = self._records
        return sum(r.revenue_usd - r.expenses_usd for r in records)

    def get_top_divisions(self, n: int = 5) -> list:
        totals = {}
        for r in self._records:
            totals[r.division_id] = totals.get(r.division_id, 0) + r.revenue_usd
        return sorted(totals.items(), key=lambda x: x[1], reverse=True)[:n]

    def get_revenue_by_month(self, year: int) -> dict:
        result = {}
        for r in [rec for rec in self._records if rec.year == year]:
            result[r.month] = result.get(r.month, 0) + r.revenue_usd
        return result

    def list_divisions(self) -> list:
        return list({r.division_id for r in self._records})

    def get_summary(self) -> dict:
        return {
            "total_revenue": self.get_total_revenue(),
            "total_profit": self.get_profit(),
            "divisions": len(self.list_divisions()),
            "records": len(self._records),
            "top_divisions": self.get_top_divisions(),
        }
