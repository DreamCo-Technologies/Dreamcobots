# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class APICall:
    endpoint: str
    division_id: str
    response_time_ms: float
    status_code: int
    timestamp: str

class APIMetrics:
    def __init__(self):
        self._calls: list = []

    def record_call(self, endpoint, division_id, response_time_ms, status_code) -> APICall:
        call = APICall(
            endpoint=endpoint,
            division_id=division_id,
            response_time_ms=response_time_ms,
            status_code=status_code,
            timestamp=datetime.utcnow().isoformat(),
        )
        self._calls.append(call)
        return call

    def get_avg_response_time(self, endpoint: str = None) -> float:
        calls = self._calls if endpoint is None else [c for c in self._calls if c.endpoint == endpoint]
        if not calls:
            return 0.0
        return sum(c.response_time_ms for c in calls) / len(calls)

    def get_error_rate(self, endpoint: str = None) -> float:
        calls = self._calls if endpoint is None else [c for c in self._calls if c.endpoint == endpoint]
        if not calls:
            return 0.0
        errors = sum(1 for c in calls if c.status_code >= 400)
        return (errors / len(calls)) * 100

    def get_top_endpoints(self, n: int = 5) -> list:
        counts = {}
        for c in self._calls:
            counts[c.endpoint] = counts.get(c.endpoint, 0) + 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

    def get_division_api_usage(self, division_id: str) -> dict:
        calls = [c for c in self._calls if c.division_id == division_id]
        if not calls:
            return {"division_id": division_id, "total_calls": 0, "avg_response_time_ms": 0.0, "error_rate": 0.0}
        errors = sum(1 for c in calls if c.status_code >= 400)
        return {
            "division_id": division_id,
            "total_calls": len(calls),
            "avg_response_time_ms": sum(c.response_time_ms for c in calls) / len(calls),
            "error_rate": (errors / len(calls)) * 100,
        }

    def get_utilization_report(self) -> dict:
        return {
            "total_calls": len(self._calls),
            "avg_response_time_ms": self.get_avg_response_time(),
            "error_rate": self.get_error_rate(),
            "top_endpoints": self.get_top_endpoints(),
            "sla_compliance": self.get_sla_compliance(),
        }

    def get_sla_compliance(self, threshold_ms: float = 500.0) -> float:
        if not self._calls:
            return 100.0
        within = sum(1 for c in self._calls if c.response_time_ms <= threshold_ms)
        return (within / len(self._calls)) * 100
