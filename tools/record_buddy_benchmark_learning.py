#!/usr/bin/env python3
"""Convert a deterministic Buddy benchmark result into learning evidence.

This tool is deliberately offline and deterministic. It never executes model
output, changes source code, or stores credentials. It records a benchmark
outcome so a later remediation/retest can be compared with the original gap.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from buddy.learning.action_failure_learning import normalize_signature


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default="")
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    data = json.loads(args.result.read_text(encoding="utf-8"))
    records = []
    for item in data.get("results", []):
        failures = item.get("failures", [])
        evidence_text = "|".join(failures) or "benchmark_passed"
        capability = item.get("task_id", "unknown")
        records.append({
            "capability_id": capability,
            "benchmark_id": data.get("benchmark_id", item.get("benchmark_id")),
            "task_id": item.get("task_id"),
            "score": item.get("score", 0.0),
            "threshold": item.get("threshold", 0.0),
            "passed": bool(item.get("passed")),
            "external_dependency": not str(item.get("model_route", "")).startswith("free-first/local"),
            "failure_signature": normalize_signature(evidence_text),
            "failures": failures,
            "remediation": item.get("remediation", []),
            "model_route": item.get("model_route", ""),
            "commit": args.commit,
            "run_id": args.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    payload = {
        "schema": "dreamco.buddy.benchmark_learning_evidence.v1",
        "source": str(args.result),
        "result_digest": hashlib.sha256(args.result.read_bytes()).hexdigest(),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "records": len(records), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
