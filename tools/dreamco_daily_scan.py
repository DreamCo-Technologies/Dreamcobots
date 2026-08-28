#!/usr/bin/env python3
"""Deterministic repository scan used by the DreamCo Actions control plane.

The scanner is intentionally dependency-light so it can run on GitHub Actions and
locally. It reports evidence and gaps; it never claims a capability is verified
without a corresponding artifact.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "daily-scan"
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build"}


def files_matching(*suffixes: str) -> list[str]:
    found = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or any(part in SKIP for part in p.parts):
            continue
        if p.suffix.lower() in suffixes:
            found.append(p.relative_to(ROOT).as_posix())
    return sorted(found)


def contains_any(names: list[str], terms: tuple[str, ...]) -> list[str]:
    return [n for n in names if any(t in n.lower() for t in terms)]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    all_files = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not any(part in SKIP for part in p.parts):
            all_files.append(p.relative_to(ROOT).as_posix())

    workflows = [n for n in all_files if n.startswith(".github/workflows/") and n.endswith((".yml", ".yaml"))]
    python = files_matching(".py")
    js = files_matching(".js", ".mjs", ".cjs", ".ts", ".tsx")
    tests = [n for n in all_files if any(x in n.lower() for x in ("test", "spec", "benchmark"))]
    docs = [n for n in all_files if n.lower().endswith((".md", ".mdx"))]
    capability_docs = contains_any(docs, ("capability", "genome", "experiment"))
    benchmark_files = contains_any(all_files, ("benchmark", "eval", "evaluation"))
    learning_files = contains_any(all_files, ("learning", "distill", "rl", "grpo", "reason"))
    actions_files = contains_any(all_files, ("action", "workflow", "control-tower"))

    package_json = ROOT / "package.json"
    requirements = ROOT / "requirements.txt"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots"),
        "counts": {
            "files": len(all_files),
            "workflows": len(workflows),
            "python_files": len(python),
            "js_ts_files": len(js),
            "tests_and_benchmarks": len(tests),
            "docs": len(docs),
        },
        "signals": {
            "capability_genome_docs": capability_docs,
            "benchmark_artifacts": benchmark_files,
            "learning_or_reasoning_artifacts": learning_files,
            "actions_or_control_plane_artifacts": actions_files,
            "package_json": package_json.exists(),
            "requirements_txt": requirements.exists(),
        },
        "workflow_files": workflows,
        "capability_docs": capability_docs,
        "benchmark_files_sample": benchmark_files[:100],
        "learning_files_sample": learning_files[:100],
        "production_gaps": [],
    }

    if not workflows:
        report["production_gaps"].append("No GitHub Actions workflow files detected")
    if not tests:
        report["production_gaps"].append("No test/benchmark files detected")
    if not capability_docs:
        report["production_gaps"].append("Capability Genome evidence is missing")
    if not benchmark_files:
        report["production_gaps"].append("Benchmark/evaluation evidence is missing")
    if not (package_json.exists() or requirements.exists()):
        report["production_gaps"].append("No primary dependency manifest detected")

    report["status"] = "needs-attention" if report["production_gaps"] else "evidence-present"

    (OUT / "daily-scan.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# DreamCo Daily Production Scan",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Commit: `{report['commit']}`",
        f"Status: **{report['status']}**",
        "",
        "## Inventory",
        "",
    ]
    for k, v in report["counts"].items():
        lines.append(f"- {k}: **{v}**")
    lines += ["", "## Production gaps", ""]
    if report["production_gaps"]:
        lines.extend(f"- 🔴 {g}" for g in report["production_gaps"])
    else:
        lines.append("- 🟢 No structural gaps detected by this deterministic scan.")
    lines += ["", "## Evidence signals", ""]
    for k, v in report["signals"].items():
        lines.append(f"- {'🟢' if v else '🟡'} {k}: `{v}`")
    (OUT / "daily-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
