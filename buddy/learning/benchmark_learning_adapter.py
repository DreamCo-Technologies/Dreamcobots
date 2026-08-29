"""Convert verified benchmark outcomes into continuous-learning events."""
from __future__ import annotations

from typing import Any


def benchmark_to_event(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize one benchmark result for the learning controller/history.

    No benchmark answer key is generated here; held-out evaluation remains outside
    the training path.
    """
    passed = bool(result.get("passed", False))
    verified = bool(result.get("verified", False))
    return {
        "event_id": str(result.get("event_id") or result.get("benchmark_id") or "unknown"),
        "event_type": "benchmark",
        "capability": str(result.get("capability") or result.get("division") or "unknown"),
        "success": passed,
        "verified": verified,
        "regression_passed": bool(result.get("regression_passed", False)),
        "safety_passed": bool(result.get("safety_passed", False)),
        "native_success": bool(result.get("native_success", False)),
        "external_assistance": bool(result.get("external_assistance", False)),
    }
