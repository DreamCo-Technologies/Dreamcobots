"""Utilities for cash reserve sizing for runway planning."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, Iterable, List, Tuple


@dataclass
class Record:
    name: str
    value: float
    weight: float = 1.0
    tags: List[str] = field(default_factory=list)


class CashReserveAgent:
    """Functional helper class for cash reserve sizing for runway planning."""

    def __init__(self) -> None:
        self.records: List[Record] = []

    def add(self, name: str, value: float, weight: float = 1.0, tags: Iterable[str] = ()) -> Record:
        record = Record(name=name, value=float(value), weight=max(0.0, float(weight)), tags=list(tags))
        self.records.append(record)
        return record

    def target_reserve(self, *args, **kwargs) -> Dict[str, float | str | List[str]]:
        working = list(self.records)
        if args and isinstance(args[0], Iterable) and not isinstance(args[0], (str, bytes, dict)):
            working = [item if isinstance(item, Record) else Record(str(item.get("name", "item")), float(item.get("value", 0.0)), float(item.get("weight", 1.0)), list(item.get("tags", []))) for item in args[0]]
        if not working:
            return {"status": "empty", "score": 0.0, "count": 0}
        total_weight = sum(max(item.weight, 0.0001) for item in working)
        weighted_value = sum(item.value * max(item.weight, 0.0001) for item in working) / total_weight
        strongest = max(working, key=lambda item: item.value * max(item.weight, 0.0001))
        return {
            "status": "ok",
            "score": round(weighted_value, 3),
            "count": len(working),
            "strongest": strongest.name,
        }

    def runway_months(self, limit: int = 5) -> List[Dict[str, float | str | List[str]]]:
        ranked = sorted(self.records, key=lambda item: (item.value * max(item.weight, 0.0001), item.name), reverse=True)
        return [
            {
                "name": item.name,
                "score": round(item.value, 3),
                "weight": round(item.weight, 3),
                "tags": list(item.tags),
            }
            for item in ranked[:limit]
        ]

    def reserve_actions(self) -> Dict[str, float | int]:
        if not self.records:
            return {"count": 0, "mean": 0.0, "weighted_mean": 0.0, "spread": 0.0}
        weights = [max(record.weight, 0.0001) for record in self.records]
        values = [record.value for record in self.records]
        weighted_mean = sum(value * weight for value, weight in zip(values, weights)) / sum(weights)
        spread = max(values) - min(values)
        return {
            "count": len(self.records),
            "mean": round(mean(values), 3),
            "weighted_mean": round(weighted_mean, 3),
            "spread": round(spread, 3),
        }

    def ingest(self, rows: Iterable[Dict[str, object]]) -> int:
        added = 0
        for row in rows:
            self.add(
                str(row.get("name", f"item-{added + 1}")),
                float(row.get("value", 0.0)),
                float(row.get("weight", 1.0)),
                row.get("tags", ()),
            )
            added += 1
        return added


def demo() -> Tuple[Dict[str, float | str | List[str]], List[Dict[str, float | str | List[str]]], Dict[str, float | int]]:
    engine = CashReserveAgent()
    engine.add("baseline", 0.5, 1.0, ["stable"])
    engine.add("growth", 0.8, 1.3, ["priority"])
    engine.add("risk", 0.3, 0.7, ["watch"])
    return engine.target_reserve(), engine.runway_months(), engine.reserve_actions()
