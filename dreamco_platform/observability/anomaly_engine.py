from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Deque, Dict, Iterable, List


@dataclass
class AnomalyEvent:
    metric: str
    value: float
    baseline: float
    z_score: float
    severity: str


class StreamingWindow:
    def __init__(self, size: int = 30) -> None:
        self.size = size
        self.values: Deque[float] = deque(maxlen=size)

    def append(self, value: float) -> None:
        self.values.append(value)

    def snapshot(self) -> List[float]:
        return list(self.values)


class AnomalyDetector:
    def __init__(self, window_size: int = 30) -> None:
        self.windows: Dict[str, StreamingWindow] = {}
        self.window_size = window_size

    def observe(self, metric: str, value: float) -> AnomalyEvent | None:
        window = self.windows.setdefault(metric, StreamingWindow(self.window_size))
        baseline = mean(window.values) if window.values else value
        z = self._z_score(window.snapshot(), value)
        event = self._classify(metric, window.snapshot(), value, baseline, z)
        window.append(value)
        return event

    def _z_score(self, values: Iterable[float], current: float) -> float:
        values = list(values)
        if len(values) < 2:
            return 0.0
        sigma = pstdev(values) or 1.0
        return (current - mean(values)) / sigma

    def _classify(self, metric: str, values: List[float], current: float, baseline: float, z: float) -> AnomalyEvent | None:
        if not values:
            return None
        q1, q3 = self._quartiles(values)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        lower = q1 - 1.5 * iqr
        if abs(z) >= 2.5 or current > upper or current < lower:
            severity = 'critical' if abs(z) >= 4 else 'warning'
            return AnomalyEvent(metric=metric, value=current, baseline=baseline, z_score=round(z, 3), severity=severity)
        return None

    def _quartiles(self, values: List[float]) -> tuple[float, float]:
        ordered = sorted(values)
        mid = len(ordered) // 2
        lower = ordered[:mid] or ordered
        upper = ordered[mid:] or ordered
        return lower[len(lower) // 2], upper[len(upper) // 2]
