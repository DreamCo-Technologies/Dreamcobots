#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "system-speed-accuracy-benchmarks.json"
OUT = ROOT / "config" / "generated" / "system-speed-accuracy-benchmarks.json"
REPORT = ROOT / "reports" / "SYSTEM_SPEED_ACCURACY_BENCHMARKS.md"


def run(command: list[str], timeout: int) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter() - started
        return {
            "command": command,
            "exit_code": proc.returncode,
            "duration_seconds": round(elapsed, 3),
            "stdout_tail": proc.stdout[-3000:],
            "stderr_tail": proc.stderr[-3000:],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        return {
            "command": command,
            "exit_code": None,
            "duration_seconds": round(elapsed, 3),
            "stdout_tail": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-3000:] if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def main() -> int:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    speed_rows = []
    accuracy_rows = []
    blockers = []

    for bench in cfg["speed_benchmarks"]:
        budget = int(bench["hard_budget_seconds"])
        result = run(list(bench["command"]), budget + 30)
        passed = result["exit_code"] == 0 and not result["timed_out"] and result["duration_seconds"] <= budget
        row = {
            "id": bench["id"],
            "budget_seconds": budget,
            "duration_seconds": result["duration_seconds"],
            "exit_code": result["exit_code"],
            "timed_out": result["timed_out"],
            "passed": passed,
            "output_tail": (result["stderr_tail"] or result["stdout_tail"])[-1500:],
        }
        speed_rows.append(row)
        if not passed:
            blockers.append(f"speed:{bench['id']}")

    for bench in cfg["accuracy_benchmarks"]:
        result = run(list(bench["command"]), 1800)
        score = 1.0 if result["exit_code"] == 0 and not result["timed_out"] else 0.0
        minimum = float(bench["minimum"])
        passed = score >= minimum
        row = {
            "id": bench["id"],
            "metric": bench["metric"],
            "minimum": minimum,
            "score": score,
            "duration_seconds": result["duration_seconds"],
            "exit_code": result["exit_code"],
            "passed": passed,
            "output_tail": (result["stderr_tail"] or result["stdout_tail"])[-1500:],
        }
        accuracy_rows.append(row)
        if not passed:
            blockers.append(f"accuracy:{bench['id']}")

    payload = {
        "schema": "dreamco.system_speed_accuracy_benchmarks.generated.v1",
        "speed": speed_rows,
        "accuracy": accuracy_rows,
        "speed_passed": sum(1 for r in speed_rows if r["passed"]),
        "speed_total": len(speed_rows),
        "accuracy_passed": sum(1 for r in accuracy_rows if r["passed"]),
        "accuracy_total": len(accuracy_rows),
        "release_blockers": blockers,
        "ok": not blockers,
        "truth_boundary": cfg["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# System Speed & Accuracy Benchmarks",
        "",
        f"- Speed passed: **{payload['speed_passed']}/{payload['speed_total']}**",
        f"- Accuracy passed: **{payload['accuracy_passed']}/{payload['accuracy_total']}**",
        f"- Release blockers: **{len(blockers)}**",
        "",
        "## Speed",
        "",
        "| Check | Seconds | Budget | Result |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in speed_rows:
        lines.append(f"| {row['id']} | {row['duration_seconds']} | {row['budget_seconds']} | {'PASS' if row['passed'] else 'FAIL'} |")
    lines += ["", "## Accuracy", "", "| Check | Score | Minimum | Result |", "| --- | ---: | ---: | --- |"]
    for row in accuracy_rows:
        lines.append(f"| {row['id']} | {row['score']:.3f} | {row['minimum']:.3f} | {'PASS' if row['passed'] else 'FAIL'} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"ok": not blockers, "speed": f"{payload['speed_passed']}/{payload['speed_total']}", "accuracy": f"{payload['accuracy_passed']}/{payload['accuracy_total']}", "blockers": blockers}, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
