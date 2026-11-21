"""Authorization-gated reverse engineering study records for Buddy.

This records observations only. It does not invoke REA or inspect targets.
"""
from urllib.parse import urlparse

def study_record(target, authorization, findings, benchmark):
    if authorization is not True:
        raise PermissionError("explicit authorization to inspect the target required")
    if not isinstance(findings, list) or not findings:
        raise ValueError("evidence-backed findings required")
    if any(not isinstance(f, dict) or not all(f.get(k) for k in ("claim", "evidence", "limitations")) for f in findings):
        raise ValueError("every finding needs claim, evidence, limitations")
    if not isinstance(benchmark, dict) or not all(k in benchmark for k in
            ("suite", "baseline", "metric", "measurement", "cost", "safety")):
        raise ValueError("benchmark provenance and measurements required")
    return {"target": target, "authorized": True, "findings": findings,
            "benchmark": benchmark, "status": "research_only_not_training_approved",
            "training_approved": False, "mastery_verified": False}
