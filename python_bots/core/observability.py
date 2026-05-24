from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Observability:
    logger_name: str = "dreamco"
    _cost_usd: float = 0.0
    _metrics: Dict[str, float] = field(default_factory=dict)
    _events: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(self.logger_name)

    def track(self, event: str, **fields: Any) -> None:
        payload = {"event": event, "ts": time.time(), **fields}
        self._events.append(payload)
        self.logger.info(json.dumps(payload, sort_keys=True))

    def add_cost(self, amount_usd: float) -> None:
        self._cost_usd += float(max(amount_usd, 0.0))

    def incr(self, metric: str, value: float = 1.0) -> None:
        self._metrics[metric] = self._metrics.get(metric, 0.0) + value

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "cost_usd": round(self._cost_usd, 6),
            "metrics": dict(self._metrics),
            "events": len(self._events),
        }
