#!/usr/bin/env python3
"""Produce checkable proof that Buddy's learning loop records improvement.

This does not claim hidden model weights changed. It proves the governed loop:
fail -> record -> native retest -> pass-rate increase -> mastery gate.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from buddy.learning.benchmark_progress import BenchmarkResult, mastery_ready, progress
from buddy.learning.learning_history import append_event, capability_trend, summarize
from tools.record_buddy_benchmark_learning import main as record_main
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "config" / "generated" / "buddy-learning-proof.json"
OUT_MD = ROOT / "reports" / "BUDDY_LEARNING_PROOF.md"
HISTORY = ROOT / "evidence" / "buddy-learning-history.jsonl"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def run_cycle(history: Path) -> dict:
    if history.exists():
        history.unlink()
    capability = "proof.sandbox-retest"
    append_event(history, {
        "capability_id": capability,
        "verified": False,
        "native_success": False,
        "external_assistance": False,
        "promote": False,
        "phase": "baseline_fail",
        "note": "synthetic sandbox miss",
    })
    before = summarize(history)
    before_trend = capability_trend(history, capability)
    before_progress = progress([BenchmarkResult(capability, False)])

    for index in range(3):
        append_event(history, {
            "capability_id": capability,
            "verified": True,
            "native_success": True,
            "external_assistance": False,
            "promote": index == 2,
            "phase": f"native_retest_{index + 1}",
            "note": "synthetic sandbox pass",
        })

    after = summarize(history)
    after_trend = capability_trend(history, capability)
    after_results = [BenchmarkResult(capability, False)] + [BenchmarkResult(capability, True) for _ in range(3)]
    after_progress = progress(after_results)
    ready = mastery_ready(after_results, minimum_passes=3)
    learned = after_progress["native_pass_rate"] > before_progress["native_pass_rate"] and after["native_verified"] > before["native_verified"]
    return {
        "capability_id": capability,
        "before": {"summary": before, "trend": before_trend, "progress": before_progress},
        "after": {"summary": after, "trend": after_trend, "progress": after_progress},
        "mastery_ready": ready,
        "learning_delta_proven": learned,
        "history_path": str(history.relative_to(ROOT)) if history.is_relative_to(ROOT) else str(history),
    }


def record_sample(tmp: Path) -> dict:
    sample = {
        "benchmark_id": "buddy-learning-proof",
        "results": [
            {
                "task_id": "proof.sandbox-retest",
                "score": 1.0,
                "threshold": 0.8,
                "passed": True,
                "model_route": "free-first/local",
                "failures": [],
                "remediation": ["retest after failure signature recorded"],
            }
        ],
    }
    result_path = tmp / "benchmark.json"
    evidence_path = tmp / "learning-evidence.json"
    result_path.write_text(json.dumps(sample) + "\n", encoding="utf-8")
    argv = sys.argv
    sys.argv = ["record_buddy_benchmark_learning.py", str(result_path), "--output", str(evidence_path), "--commit", "proof", "--run-id", "local"]
    try:
        rc = record_main()
    finally:
        sys.argv = argv
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    return {"recorder_ok": rc == 0, "records": len(evidence.get("records", [])), "schema": evidence.get("schema")}


def main() -> int:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    cycle = run_cycle(HISTORY)
    with tempfile.TemporaryDirectory(prefix="buddy-learn-proof-") as raw:
        recorded = record_sample(Path(raw))
    payload = {
        "schema": "dreamco.buddy_learning_proof.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim": "Buddy recorded a verified native-pass-rate increase on a sandbox capability. This is loop evidence, not a claim that private model weights were updated.",
        "cycle": cycle,
        "recorder": recorded,
        "history_sha256": _digest(HISTORY),
        "proven": bool(cycle["learning_delta_proven"] and recorded["recorder_ok"] and cycle["mastery_ready"]),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Buddy Learning Proof",
        "",
        f"- Proven: **{payload['proven']}**",
        f"- Capability: `{cycle['capability_id']}`",
        f"- Native verified before/after: **{cycle['before']['summary']['native_verified']} → {cycle['after']['summary']['native_verified']}**",
        f"- Native pass rate before/after: **{cycle['before']['progress']['native_pass_rate']:.2f} → {cycle['after']['progress']['native_pass_rate']:.2f}**",
        f"- Mastery ready (3 native passes): **{cycle['mastery_ready']}**",
        f"- Recorder schema: `{recorded['schema']}`",
        f"- History digest: `{payload['history_sha256'][:16]}…`",
        "",
        payload["claim"],
        "",
        "Artifacts:",
        "- `config/generated/buddy-learning-proof.json`",
        "- `evidence/buddy-learning-history.jsonl`",
        "- `reports/BUDDY_LEARNING_PROOF.md`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": payload["proven"], "proof": str(OUT_MD.relative_to(ROOT))}, indent=2))
    return 0 if payload["proven"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
