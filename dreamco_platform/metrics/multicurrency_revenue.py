from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List


@dataclass
class CurrencyRevenue:
    amount: float
    currency_code: str
    usd_equivalent: float
    exchange_rate_date: datetime


class ExchangeRateCache:
    DEFAULT_RATES = {'USD': 1.0, 'EUR': 1.08, 'GBP': 1.25, 'JPY': 0.0067, 'CAD': 0.74, 'AUD': 0.66}

    def __init__(self) -> None:
        self.rates = dict(self.DEFAULT_RATES)
        self.refreshed_at = datetime.utcnow()

    def refresh(self) -> None:
        self.refreshed_at = datetime.utcnow()

    def get_rate(self, currency_code: str) -> float:
        if datetime.utcnow() - self.refreshed_at > timedelta(hours=1):
            self.refresh()
        return self.rates.get(currency_code.upper(), 1.0)


class MultiCurrencyLedger:
    def __init__(self, rates: ExchangeRateCache | None = None) -> None:
        self.rates = rates or ExchangeRateCache()
        self.entries: List[CurrencyRevenue] = []

    def add(self, amount: float, currency_code: str, when: datetime | None = None) -> CurrencyRevenue:
        when = when or datetime.utcnow()
        usd = amount * self.rates.get_rate(currency_code)
        entry = CurrencyRevenue(amount, currency_code.upper(), round(usd, 2), when)
        self.entries.append(entry)
        return entry

    def aggregate_usd(self) -> float:
        return round(sum(entry.usd_equivalent for entry in self.entries), 2)

    def by_currency(self) -> Dict[str, float]:
        totals: Dict[str, float] = defaultdict(float)
        for entry in self.entries:
            totals[entry.currency_code] += entry.amount
        return dict(totals)

    def by_period(self, fmt: str = '%Y-%m') -> Dict[str, float]:
        totals: Dict[str, float] = defaultdict(float)
        for entry in self.entries:
            totals[entry.exchange_rate_date.strftime(fmt)] += entry.usd_equivalent
        return dict(totals)
