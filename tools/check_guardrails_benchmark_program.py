#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "buddy-guardrails-benchmark-program.json"

REQUIRED_GUARDRAIL_PHRASES = [
    "production-ready",
    "duplicate",
    "external writes",
    "paid actions",
    "user-owned",
    "silent private-app scraping",
    "local-first",
    "high-impact",
    "never fabricate",
    "never guarantee",
    "unlicensed real person's voice or likeness",
    "current-trend",
    "untrusted repositories",
    "secrets",
    "rollback",
    "thousands-of-tasks",
    "phone/background execution",
    "battery-drain",
    "cannot complete a task autonomously",
    "transparent that it is AI",
    "personality adaptation",
    "commercial media",
    "music analysis",
    "current-hit benchmarking",
    "Hollywood/career systems",
    "game and NPC systems",
    "builder bots must compare issue requirements",
    "issues and benchmark gaps close only",
    "regressions",
]

REQUIRED_BENCHMARK_DOMAINS = [
    "correctness","reliability","latency","concurrency","battery_efficiency","cost_efficiency","security","privacy","permissions",
    "data_portability","offline_behavior","accessibility","time_to_goal","human_step_reduction","autonomy","rollback","recovery",
    "observability","deduplication","integration_quality","routing_accuracy","task_completion","model_quality","freshness","evidence_quality",
    "uncertainty_calibration","personality_consistency","natural_conversation","sales_quality","lead_quality","business_value","creator_quality",
    "music_quality","audio_analysis_quality","beat_fit","lyric_quality","acting_quality","video_quality","game_quality","npc_quality",
    "learning_quality","device_integration","collection_vault_quality","enterprise_readiness","production_readiness"
]


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    guardrails = data.get("global_guardrails", [])
    joined = "\n".join(guardrails).lower()
    domains = set(data.get("benchmark_domains", []))

    if data.get("canonical") is not True:
        errors.append("guardrail program must be canonical")
    if len(guardrails) < 40:
        errors.append(f"expected at least 40 consolidated guardrails, found {len(guardrails)}")
    for phrase in REQUIRED_GUARDRAIL_PHRASES:
        if phrase.lower() not in joined:
            errors.append(f"missing guardrail coverage: {phrase}")
    for domain in REQUIRED_BENCHMARK_DOMAINS:
        if domain not in domains:
            errors.append(f"missing benchmark domain: {domain}")

    parallel = data.get("parallel_builder_team", {})
    if parallel.get("enabled") is not True:
        errors.append("parallel builder team must be enabled")
    if int(parallel.get("maximum_parallel_lanes", 0)) < 2:
        errors.append("parallel benchmark repair requires multiple lanes")
    if int(parallel.get("maximum_parallel_changes_per_owner", 99)) != 1:
        errors.append("canonical owner must allow only one concurrent change")
    if len(parallel.get("assignment_rules", [])) < 10:
        errors.append("parallel builder assignment rules are incomplete")
    if len(data.get("benchmark_method_rules", [])) < 8:
        errors.append("benchmark methodology is incomplete")
    if len(data.get("issue_and_gap_lifecycle", [])) < 10:
        errors.append("issue/gap lifecycle is incomplete")
    if len(data.get("close_conditions", [])) < 8:
        errors.append("close conditions are incomplete")

    report = {
        "ok": not errors,
        "version": data.get("version"),
        "guardrails": len(guardrails),
        "benchmark_domains": len(domains),
        "parallel_lanes": parallel.get("maximum_parallel_lanes"),
        "assignment_rules": len(parallel.get("assignment_rules", [])),
        "benchmark_method_rules": len(data.get("benchmark_method_rules", [])),
        "lifecycle_steps": len(data.get("issue_and_gap_lifecycle", [])),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
