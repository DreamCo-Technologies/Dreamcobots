#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
OUT_JSON = ROOT / "config" / "generated" / "actions-consistency-report.json"
OUT_MD = ROOT / "reports" / "ACTIONS_CONSISTENCY_REPORT.md"

BASELINE = {
    "checkout": "actions/checkout@v6",
    "setup_node": "actions/setup-node@v6",
    "setup_python": "actions/setup-python@v6",
}


def inspect(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    warnings: list[str] = []
    errors: list[str] = []

    if "jobs:" not in text:
        errors.append("missing jobs section")
    if "permissions:" not in text:
        warnings.append("missing explicit permissions block")
    if "concurrency:" not in text:
        warnings.append("missing top-level concurrency control")
    if "timeout-minutes:" not in text:
        warnings.append("no job timeout found")
    if "workflow_dispatch:" not in text:
        warnings.append("no manual workflow_dispatch trigger")
    if "actions/checkout@" in text and BASELINE["checkout"] not in text:
        warnings.append(f"checkout is not standardized on {BASELINE['checkout']}")
    if "actions/setup-node@" in text and BASELINE["setup_node"] not in text:
        warnings.append(f"setup-node is not standardized on {BASELINE['setup_node']}")
    if "actions/setup-python@" in text and BASELINE["setup_python"] not in text:
        warnings.append(f"setup-python is not standardized on {BASELINE['setup_python']}")
    if "GITHUB_STEP_SUMMARY" not in text:
        warnings.append("workflow does not explain itself in the GitHub job summary")
    if re.search(r"npm\s+(install|i)\b", text) and "npm ci" not in text:
        warnings.append("uses npm install instead of deterministic npm ci")
    if "pull_request_target:" in text and "contents: write" in text:
        warnings.append("pull_request_target with write permission requires manual security review")
    if "npm audit fix --force" in text:
        errors.append("forbidden force dependency repair")
    if "git push" in text and "pull_request:" not in text and "workflow_dispatch:" not in text:
        warnings.append("workflow can push but has no explicit review/manual trigger")

    return {
        "workflow": str(path.relative_to(ROOT)),
        "errors": errors,
        "warnings": warnings,
        "consistent": not errors and not warnings,
    }


def main() -> int:
    paths = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    rows = [inspect(path) for path in paths]
    critical = sum(len(row["errors"]) for row in rows)
    warnings = sum(len(row["warnings"]) for row in rows)
    payload = {
        "schema": "dreamco.actions_consistency.v1",
        "workflow_count": len(rows),
        "critical_error_count": critical,
        "warning_count": warnings,
        "fully_consistent_count": sum(1 for row in rows if row["consistent"]),
        "baseline": BASELINE,
        "required_patterns": [
            "least-privilege permissions",
            "bounded concurrency",
            "job timeout",
            "manual workflow dispatch when operationally useful",
            "current DreamCo action versions",
            "plain-English GITHUB_STEP_SUMMARY",
            "deterministic installs",
            "no forced dependency repair",
        ],
        "findings": rows,
        "truth_boundary": "Consistency is a maintenance quality signal. A warning does not mean the workflow is broken, and a clean static report does not replace a successful runtime execution.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GitHub Actions Consistency Report",
        "",
        f"Workflows: **{len(rows)}**",
        f"Critical consistency errors: **{critical}**",
        f"Warnings: **{warnings}**",
        f"Fully consistent: **{payload['fully_consistent_count']}**",
        "",
    ]
    for row in rows:
        if not row["errors"] and not row["warnings"]:
            continue
        lines.append(f"## {row['workflow']}")
        lines.extend(f"- ❌ {item}" for item in row["errors"])
        lines.extend(f"- ⚠️ {item}" for item in row["warnings"])
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": critical == 0, "workflows": len(rows), "critical": critical, "warnings": warnings}, indent=2))
    return 0 if critical == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
