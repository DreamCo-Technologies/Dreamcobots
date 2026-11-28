#!/usr/bin/env python3
"""Offline CLI for DreamCo's evidence-first 10-pillar evaluation utilities."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from tools.dreamco_10pillar_extensions import (
    audit_buyer_readiness,
    build_regression_issue_draft,
    distill_verified_repair,
    evaluate_swarm_handoff,
    propose_upgrade_101,
    update_curriculum_state,
)
from tools.leaderboard_math import pareto_frontier, update_glicko2
from tools.plan_500_model_shards import build_plan


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def run(command: str, payload: dict[str, Any]) -> Any:
    if command == "glicko2":
        return update_glicko2(
            payload["rating"], payload["rd"], payload["volatility"], payload.get("opponents", [])
        )
    if command == "pareto":
        return {"frontier": pareto_frontier(payload.get("records", []))}
    if command == "curriculum":
        return update_curriculum_state(
            payload.get("state", {}),
            scope_type=payload["scope_type"],
            scope_id=payload["scope_id"],
            pass_rate=payload["pass_rate"],
            difficulty=payload.get("difficulty", 1.0),
            interval_days=payload.get("interval_days", 1),
            evidence_split=payload.get("evidence_split", "practice"),
        )
    if command == "distill":
        signatures = [tuple(row) for row in payload.get("existing_signatures", [])]
        return {"drills": distill_verified_repair(
            payload["evidence"], existing_signatures=signatures,
            similarity_threshold=payload.get("similarity_threshold", 0.90),
        )}
    if command == "swarm":
        return evaluate_swarm_handoff(**payload)
    if command == "regression":
        return build_regression_issue_draft(
            model_id=payload["model_id"],
            baseline_score=payload["baseline_score"],
            current_score=payload["current_score"],
            baseline_sha256=payload["baseline_sha256"],
            current_sha256=payload["current_sha256"],
            reproduction_command=payload["reproduction_command"],
            threshold=payload.get("threshold", 0.005),
        )
    if command == "buyer-readiness":
        return audit_buyer_readiness(
            fp16_score=payload["fp16_score"],
            q8_score=payload["q8_score"],
            q4_score=payload["q4_score"],
            isolation_receipt=payload.get("isolation_receipt"),
            hmac_key=os.environ.get("DREAMCO_ISOLATION_HMAC_KEY", ""),
            key_id=os.environ.get("DREAMCO_ISOLATION_HMAC_KEY_ID", ""),
            max_q8_drift=payload.get("max_q8_drift", 0.02),
            max_q4_drift=payload.get("max_q4_drift", 0.03),
        )
    if command == "upgrade-101":
        return propose_upgrade_101(
            payload.get("telemetry", []),
            minimum_observations=payload.get("minimum_observations", 3),
        )
    if command == "plan-500":
        return build_plan(payload)
    raise ValueError(f"unsupported command: {command}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("glicko2", "pareto", "curriculum", "distill", "swarm",
                 "regression", "buyer-readiness", "upgrade-101", "plan-500"),
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.command, _read(args.input))
    _write(args.output, result)
    status = result.get("status", "COMPLETED") if isinstance(result, dict) else "COMPLETED"
    print(json.dumps({"command": args.command, "status": status, "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
