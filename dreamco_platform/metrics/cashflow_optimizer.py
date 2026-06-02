"""Cashflow forecasting and working-capital optimization tools."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class CashEvent:
    period: str
    inflow: float
    outflow: float
    confidence: float = 1.0


class CashflowOptimizer:
    def rolling_balance(self, opening_cash: float, events: Iterable[CashEvent]) -> List[Dict[str, float | str]]:
        balance = opening_cash
        timeline: List[Dict[str, float | str]] = []
        for event in events:
            balance += event.inflow - event.outflow
            timeline.append({
                "period": event.period,
                "net": round(event.inflow - event.outflow, 2),
                "balance": round(balance, 2),
                "confidence": round(event.confidence, 3),
            })
        return timeline

    def optimize_payment_timing(self, events: Iterable[CashEvent], minimum_balance: float) -> Dict[str, object]:
        shifted: List[str] = []
        cash = 0.0
        adjusted = []
        for event in events:
            outflow = event.outflow
            if cash + event.inflow - outflow < minimum_balance and outflow > 0:
                reduction = min(outflow * 0.3, minimum_balance - (cash + event.inflow - outflow))
                outflow -= max(0.0, reduction)
                shifted.append(event.period)
            cash += event.inflow - outflow
            adjusted.append(CashEvent(event.period, event.inflow, outflow, event.confidence))
        return {"shifted_periods": shifted, "projection": self.rolling_balance(0.0, adjusted)}

    def financing_need(self, opening_cash: float, events: Iterable[CashEvent]) -> float:
        minimum = opening_cash
        balance = opening_cash
        for event in events:
            balance += event.inflow - event.outflow
            minimum = min(minimum, balance)
        return round(abs(minimum) if minimum < 0 else 0.0, 2)

    def scenario_band(self, opening_cash: float, events: Iterable[CashEvent]) -> Dict[str, float]:
        events = list(events)
        best = self.rolling_balance(opening_cash, [CashEvent(e.period, e.inflow * (1 + (1 - e.confidence) * 0.2), e.outflow * 0.95, e.confidence) for e in events])
        worst = self.rolling_balance(opening_cash, [CashEvent(e.period, e.inflow * (1 - (1 - e.confidence) * 0.4), e.outflow * 1.1, e.confidence) for e in events])
        return {
            "best_end_balance": best[-1]["balance"] if best else opening_cash,
            "worst_end_balance": worst[-1]["balance"] if worst else opening_cash,
        }


def summarize_cash(opening_cash: float, events: Iterable[CashEvent]) -> Dict[str, object]:
    optimizer = CashflowOptimizer()
    events = list(events)
    return {
        "timeline": optimizer.rolling_balance(opening_cash, events),
        "financing_need": optimizer.financing_need(opening_cash, events),
        "band": optimizer.scenario_band(opening_cash, events),
    }
