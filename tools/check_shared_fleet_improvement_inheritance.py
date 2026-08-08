#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "shared-fleet-improvement-inheritance.json"

REQUIRED_DOMAINS = {
    "routing","memory","audio analysis","benchmarking","testing","security","privacy","queueing","concurrency",
    "observability","performance optimization","builder strategy","open-source parity","competitor benchmarking"
}


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    domains = set(data.get("shared_improvement_domains", []))
    rules = data.get("inheritance_rules", [])
    ext = data.get("extension_model", {})
    retest = data.get("fleet_retest", {})

    if data.get("default_policy") != "inherit_verified_shared_improvements":
        errors.append("shared improvement inheritance must be default")
    missing = sorted(REQUIRED_DOMAINS - domains)
    if missing:
        errors.append(f"missing shared domains: {', '.join(missing)}")
    if len(rules) < 10:
        errors.append("inheritance rules are incomplete")
    if "bot-specific implementation as last resort" not in ext.get("preferred_order", []):
        errors.append("bot-specific code must remain last resort")
    if retest.get("enabled") is not True:
        errors.append("fleet retest must be enabled")
    if int(retest.get("maximum_parallel_lanes", 0)) < 2:
        errors.append("fleet retest must support parallel execution")
    if data.get("truth_rule") is None:
        errors.append("truth rule is required")

    report = {
        "ok": not errors,
        "shared_domains": len(domains),
        "inheritance_rules": len(rules),
        "parallel_retest_lanes": retest.get("maximum_parallel_lanes"),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
