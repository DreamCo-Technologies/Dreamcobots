#!/usr/bin/env python3
"""Fail-closed execution gate for the 500-model benchmark program.

This is deliberately a readiness recorder, not a benchmark implementation.
It never downloads weights, contacts model providers, starts training, or
manufactures scores. Replace this gate only with an evidence-producing runner
that enforces the approved model/data/compute and private-holdout policies.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "website/data/benchmark-execution-status.json"
VALID_MODES = {"quick", "standard", "maximum"}


def build_status(mode: str) -> dict:
    if mode not in VALID_MODES:
        raise ValueError(f"unsupported benchmark mode: {mode}")
    return {
        "schema": "dreamco.benchmark_execution_status.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED_RUNNER_NOT_IMPLEMENTED",
        "mode": mode,
        "execution_started": False,
        "provider_calls": 0,
        "training_jobs": 0,
        "verified_results": 0,
        "paid_calls_enabled": False,
        "reason": "The dedicated evidence-producing 500-model runner has not been implemented.",
        "required_before_execution": [
            "approved model and dataset revisions with training/evaluation rights",
            "isolated private holdouts and frozen benchmark fixtures",
            "provider permissions and explicit paid-call approval where applicable",
            "per-model execution receipts with exact compute/time/resource usage",
            "independent quality, safety, privacy, latency, throughput, memory and cost evidence",
        ],
        "truth_boundary": "Catalog rows and readiness checks are not benchmark executions or training evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="standard")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    status = build_status(args.mode)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
