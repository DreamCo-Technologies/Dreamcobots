#!/usr/bin/env python3
"""Build a conservative adoption map for shared fleet improvements.

This scanner does not claim runtime adoption from names alone. It inventories likely bot
sources and records evidence/unknown status so builders can migrate duplicate local
implementations into canonical shared infrastructure and then verify them.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "shared-fleet-improvement-inheritance.json"
OUT = ROOT / "config" / "generated" / "shared-fleet-improvement-adoption-map.json"

BOT_ROOT_HINTS = ("bots", "BuddyAI", "dreamco_platform", "backend", "server")
BOT_NAME_HINTS = ("bot", "agent", "assistant", "worker", "specialist")
SHARED_HINTS = {
    "routing": ("route", "router", "routing"),
    "memory": ("memory", "retrieval", "vector"),
    "testing": ("test", "verify", "validation", "benchmark"),
    "audio analysis": ("audio", "voice", "speech", "music"),
    "security": ("security", "auth", "permission", "guardrail"),
    "queueing": ("queue", "scheduler", "job"),
    "observability": ("metric", "telemetry", "logging", "trace"),
    "performance optimization": ("performance", "cache", "optimiz"),
    "builder strategy": ("builder", "codegen", "repair", "fix"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def likely_bot_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if not rel.parts or rel.parts[0] not in BOT_ROOT_HINTS:
        return False
    name = path.stem.lower()
    return any(h in name for h in BOT_NAME_HINTS) and path.suffix.lower() in {".py", ".js", ".ts", ".tsx", ".json"}


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    candidates = []
    duplicate_signals: dict[str, list[str]] = defaultdict(list)

    for path in ROOT.rglob("*"):
        if not path.is_file() or not likely_bot_file(path):
            continue
        rel = str(path.relative_to(ROOT))
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        domains = [domain for domain, hints in SHARED_HINTS.items() if any(h in text for h in hints)]
        candidates.append({
            "candidate_id": rel,
            "path": rel,
            "content_hash": sha(path),
            "shared_domains_detected": domains,
            "adoption_status": "unknown_requires_runtime_verification",
            "evidence": ["repository source discovered"],
            "required_next_step": "resolve canonical bot identity/runtime route, compare shared dependency usage, migrate duplicates if found, then run bot and fleet benchmarks"
        })
        duplicate_signals[path.name.lower()].append(rel)

    duplicate_candidates = [
        {"filename": name, "paths": paths, "status": "review_required_not_proof_of_duplicate"}
        for name, paths in sorted(duplicate_signals.items()) if len(paths) > 1
    ]

    out = {
        "schema": "dreamco.shared_fleet_improvement_adoption_map.v1",
        "policy": str(POLICY.relative_to(ROOT)),
        "default_policy": policy.get("default_policy"),
        "truth_boundary": "Static repository discovery is inventory evidence only; verified inheritance requires runtime/dependency evidence and passing benchmarks.",
        "candidate_bot_sources": candidates,
        "candidate_count": len(candidates),
        "possible_duplicate_filename_groups": duplicate_candidates,
        "shared_domains": policy.get("shared_improvement_domains", []),
        "migration_workflow": policy.get("promotion_pipeline", []),
        "retest_policy": policy.get("fleet_retest", {})
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "candidates": len(candidates), "possible_duplicate_groups": len(duplicate_candidates), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
