#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "buddy-fleet-quality-program.json"


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    competitor = data.get("competitor_discovery", {})
    parity = data.get("open_source_and_vibe_coding_parity", {})
    per_bot = data.get("per_bot_competition_program", {})
    workers = {w.get("slug") for w in data.get("quality_workers", [])}
    pipeline = {p.get("id") for p in data.get("release_pipeline", [])}

    if int(competitor.get("maximum_candidates_per_capability", 0)) < 30:
        errors.append("competitor target must support at least 30 candidates per capability")
    if int(per_bot.get("top_competitor_target", 0)) < 30:
        errors.append("every canonical bot must target top-30 competitor discovery where available")
    if per_bot.get("enabled") is not True:
        errors.append("per-bot competition program must be enabled")
    if parity.get("enabled") is not True:
        errors.append("open-source/vibe-coding parity must be enabled")

    required_checks = {"license compatibility", "security and dependency scan", "sandbox execution", "same-fixture benchmark", "regression tests after adoption"}
    if not required_checks.issubset(set(parity.get("required_checks", []))):
        errors.append("open-source parity required checks are incomplete")

    required_workers = {"competitive-intel", "competitive-benchmark", "open-source-scout", "open-source-benchmark", "vibe-coding-parity", "improvement-engine"}
    missing_workers = sorted(required_workers - workers)
    if missing_workers:
        errors.append(f"missing quality workers: {', '.join(missing_workers)}")

    required_pipeline = {"open_source_parity", "competitor_baseline", "measured_gap_parallel_sprint"}
    missing_pipeline = sorted(required_pipeline - pipeline)
    if missing_pipeline:
        errors.append(f"missing release gates: {', '.join(missing_pipeline)}")

    required_outputs = {"competitor/substitute roster", "open-source parity results", "vibe-coding parity results", "builder gap assignments", "retest evidence"}
    if not required_outputs.issubset(set(per_bot.get("required_outputs", []))):
        errors.append("per-bot required competition outputs are incomplete")

    report = {
        "ok": not errors,
        "competitor_target": competitor.get("maximum_candidates_per_capability"),
        "per_bot_target": per_bot.get("top_competitor_target"),
        "open_source_parity": parity.get("enabled"),
        "quality_workers": len(workers),
        "release_gates": len(pipeline),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
