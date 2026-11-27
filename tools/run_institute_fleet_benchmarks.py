"""Bounded, fail-closed head-to-head evaluation across the canonical 65 MasterBots.

This orchestrator only evaluates already-built release candidates. Missing
weights, adapters, fixtures or baseline rights evidence are BLOCKED, never
converted to zero-score passes. It does not train or download models.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.benchmark_vs_baselines import run_benchmark

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "masterbot-65-registry.json"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_masterbots(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    bots = registry.get("divisions", [])
    if registry.get("canonical_count") != 65 or len(bots) != 65:
        raise ValueError("competitive fleet runner requires the canonical 65-MasterBot registry")
    ids = [bot.get("id") for bot in bots]
    names = [bot.get("name") for bot in bots]
    if len(set(ids)) != 65 or len(set(names)) != 65 or any(not name for name in names):
        raise ValueError("MasterBot registry IDs and names must be unique and complete")
    return bots


def build_fleet_plan(registry_path: Path, candidate_root: Path,
                     fixture_root: Path, adapter_root: Path) -> list[dict[str, Any]]:
    bots = load_masterbots(registry_path)
    plan = []
    for bot in bots:
        key = slug(bot["name"])
        plan.append({
            "masterbot_id": bot["id"],
            "division_id": bot["name"],
            "candidate_manifest": candidate_root / key / "release-candidate.json",
            "checkpoint_adapter": adapter_root / key / "adapter.json",
            "fixtures": fixture_root / key / "fixtures.json",
        })
    return plan


def run_fleet(registry_path: Path, candidate_root: Path, fixture_root: Path,
              adapter_root: Path, baseline_registry: Path, output_path: Path,
              max_candidates: int = 65, repeats: int = 3, timeout: float = 10.0) -> dict[str, Any]:
    if not 1 <= max_candidates <= 65:
        raise ValueError("max_candidates must be between 1 and 65")
    plan = build_fleet_plan(registry_path, candidate_root, fixture_root, adapter_root)[:max_candidates]
    results = []
    for item in plan:
        missing = [key for key in ("candidate_manifest", "checkpoint_adapter", "fixtures")
                   if not item[key].is_file()]
        if missing:
            results.append({
                "masterbot_id": item["masterbot_id"],
                "division_id": item["division_id"],
                "status": "BLOCKED",
                "reason": "missing required local evidence: " + ", ".join(missing),
            })
            continue
        try:
            adapter = json.loads(item["checkpoint_adapter"].read_text(encoding="utf-8"))
            if adapter.get("schema") != "dreamco.institute.model_adapter.v1":
                raise ValueError("unsupported model adapter manifest schema")
            checkpoint = Path(adapter.get("checkpoint_path", ""))
            tokenizer = Path(adapter.get("tokenizer_path", ""))
            if not checkpoint.is_absolute():
                checkpoint = item["checkpoint_adapter"].parent / checkpoint
            if not tokenizer.is_absolute():
                tokenizer = item["checkpoint_adapter"].parent / tokenizer
            report = run_benchmark(
                item["candidate_manifest"], checkpoint, tokenizer, adapter.get("command"),
                baseline_registry, item["fixtures"], item["division_id"], repeats, timeout,
            )
            results.append({
                "masterbot_id": item["masterbot_id"],
                "division_id": item["division_id"],
                "status": "EVALUATED",
                "candidate_model_id": report["candidate"]["model_id"],
                "baseline_count": len(report["baselines"]),
                "candidate_metrics": {
                    "contract_pass_rate": report["candidate"]["contract_pass_rate"],
                    "task_exact_match_rate": report["candidate"]["task_exact_match_rate"],
                    "routing_accuracy": report["candidate"]["routing_accuracy"],
                    "deterministic_repeat_rate": report["candidate"]["deterministic_repeat_rate"],
                    "adapter_round_trip_p50_ms": report["candidate"]["adapter_round_trip_p50_ms"],
                    "adapter_round_trip_p95_ms": report["candidate"]["adapter_round_trip_p95_ms"],
                },
                "report": report,
            })
        except (OSError, ValueError, PermissionError, KeyError, TypeError, json.JSONDecodeError) as exc:
            results.append({
                "masterbot_id": item["masterbot_id"],
                "division_id": item["division_id"],
                "status": "BLOCKED",
                "reason": f"{type(exc).__name__}: {exc}",
            })

    evaluated = sum(item["status"] == "EVALUATED" for item in results)
    blocked = sum(item["status"] == "BLOCKED" for item in results)
    report = {
        "schema": "dreamco.institute.competitive_fleet_report.v1",
        "canonical_registry_count": 65,
        "candidates_requested": len(plan),
        "candidates_evaluated": evaluated,
        "candidates_blocked": blocked,
        "fleet_status": "COMPLETE" if evaluated == 65 else ("PARTIAL" if evaluated else "BLOCKED"),
        "results": results,
        "training_performed": False,
        "weights_modified": False,
        "runner_initiated_network_calls": False,
        "adapter_network_usage": "NOT_MEASURED_REQUIRES_LOCAL_ADAPTER_REVIEW",
        "adapter_paid_compute_usage": "NOT_MEASURED_REQUIRES_EXPLICIT_APPROVAL_AND_ADAPTER_REVIEW",
        "production_release_performed": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--candidate-root", type=Path, default=Path.home() / "DreamCo-models" / "release-candidates")
    parser.add_argument("--fixture-root", type=Path, default=Path.home() / "DreamCo-benchmark-fixtures")
    parser.add_argument("--adapter-root", type=Path, default=Path.home() / "DreamCo-model-adapters")
    parser.add_argument("--baseline-registry", type=Path, default=ROOT / "config" / "institute-competitive-baselines.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "institute-competitive-fleet.json")
    parser.add_argument("--max-candidates", type=int, default=65)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    report = run_fleet(args.registry, args.candidate_root, args.fixture_root,
                       args.adapter_root, args.baseline_registry, args.output,
                       args.max_candidates, args.repeats, args.timeout)
    print(json.dumps({key: report[key] for key in (
        "canonical_registry_count", "candidates_requested", "candidates_evaluated",
        "candidates_blocked", "fleet_status")}, indent=2))
    return 0 if report["candidates_blocked"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
