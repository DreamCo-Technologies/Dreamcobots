#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "github-platform-parity-benchmark.json"
OUT_JSON = ROOT / "config" / "generated" / "github-platform-parity-benchmark.json"
OUT_MD = ROOT / "reports" / "GITHUB_PLATFORM_PARITY_BENCHMARK.md"


def exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def score_capability(row: dict) -> dict:
    required_all = row.get("evidence_all", [])
    required_any = row.get("evidence_any", [])
    all_present = [path for path in required_all if exists(path)]
    any_present = [path for path in required_any if exists(path)]
    missing_all = [path for path in required_all if not exists(path)]

    if required_all and not missing_all and (not required_any or any_present):
        status = "repository_evidence_present"
    elif not required_all and required_any and any_present:
        status = "repository_evidence_present"
    elif all_present or any_present:
        status = "partial_repository_evidence"
    else:
        status = "gap_no_repository_evidence"

    if status == "repository_evidence_present":
        next_step = "Run/maintain executable tests and runtime evidence; improve user simplicity and feature depth where GitHub remains stronger."
    elif status == "partial_repository_evidence":
        next_step = "Complete the missing local owner/implementation, add sandbox and regression tests, then record runtime evidence."
    else:
        next_step = "Create a local-first implementation owner, API/UI contract, sandbox tests, migration/rollback plan and runtime proof."

    return {
        **row,
        "status": status,
        "evidence_present": sorted(set(all_present + any_present)),
        "evidence_missing": missing_all,
        "runtime_evidence_required": True,
        "gap_builder_plan": {
            "priority": "high" if status != "repository_evidence_present" else "continuous_improvement",
            "next_step": next_step,
            "acceptance": [
                "canonical owner exists",
                "simple owner-facing UX or CLI exists",
                "sandbox/negative tests exist",
                "offline/local behavior exists where practical",
                "security/permission boundaries are explicit",
                "focused executable verification passes",
                "before/after benchmark evidence recorded",
            ],
        },
    }


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    rows = [score_capability(row) for row in cfg["capabilities"]]
    counts = Counter(row["status"] for row in rows)
    by_category = defaultdict(lambda: Counter())
    for row in rows:
        by_category[row["category"]][row["status"]] += 1

    payload = {
        "schema": "dreamco.github_platform_parity_benchmark.generated.v1",
        "source_program": str(CONFIG.relative_to(ROOT)),
        "capability_count": len(rows),
        "status_counts": dict(counts),
        "categories": {key: dict(value) for key, value in sorted(by_category.items())},
        "parity_complete": False,
        "parity_complete_reason": "Repository file evidence alone cannot prove full GitHub capability parity; runtime depth, hosted-scale features and current GitHub feature changes must be continuously benchmarked.",
        "capabilities": rows,
        "gap_builder_rules": cfg["gap_builder_rules"],
        "truth_boundary": cfg["truth_rule"],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GitHub Platform Parity Benchmark",
        "",
        f"Capabilities tracked: **{len(rows)}**",
        f"Repository evidence present: **{counts.get('repository_evidence_present', 0)}**",
        f"Partial evidence: **{counts.get('partial_repository_evidence', 0)}**",
        f"No repository evidence: **{counts.get('gap_no_repository_evidence', 0)}**",
        "",
        "> Repository evidence is not the same as full runtime parity. Every capability still needs executable proof and ongoing comparison against current GitHub behavior.",
        "",
        "| Capability | Category | GitHub reference feature | DreamCo status | Local goal |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['id']}` | {row['category']} | {row['github_feature']} | {row['status']} | {row['local_goal']} |")

    gaps = [row for row in rows if row["status"] != "repository_evidence_present"]
    lines += ["", "## Builder gaps", ""]
    if not gaps:
        lines.append("- No file-evidence gaps detected. Runtime/depth benchmarking is still required.")
    for row in gaps:
        lines.append(f"- **{row['id']}** — {row['gap_builder_plan']['next_step']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "capabilities": len(rows),
        "status_counts": dict(counts),
        "json": str(OUT_JSON.relative_to(ROOT)),
        "report": str(OUT_MD.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
