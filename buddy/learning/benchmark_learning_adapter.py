"""Convert verified benchmark outcomes into continuous-learning events."""
from __future__ import annotations

from typing import Any


def benchmark_to_event(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize one benchmark result for the learning controller/history.

    No benchmark answer key is generated here; held-out evaluation remains outside
    the training path.
    """
    flags = {}
    for name in ("passed", "verified", "regression_passed", "safety_passed", "native_success", "external_assistance"):
        value = result.get(name, False)
        if type(value) is not bool:
            raise ValueError(f"{name} must be a boolean")
        flags[name] = value
    return {
        "event_id": str(result.get("event_id") or result.get("benchmark_id") or "unknown"),
        "event_type": "benchmark",
        "capability": str(result.get("capability") or result.get("division") or "unknown"),
        "success": flags["passed"],
        "verified": flags["verified"],
        "regression_passed": flags["regression_passed"],
        "safety_passed": flags["safety_passed"],
        "native_success": flags["native_success"],
        "external_assistance": flags["external_assistance"],
    }
