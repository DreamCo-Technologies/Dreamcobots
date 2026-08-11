#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
OUT_JSON = ROOT / "config" / "generated" / "actions-health-report.json"
OUT_MD = ROOT / "reports" / "ACTIONS_HEALTH_REPORT.md"
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
SCRIPTS = set(PACKAGE.get("scripts", {}))

MAX_MAJOR = {
    "actions/checkout": 6,
    "actions/setup-node": 6,
    "actions/setup-python": 6,
    "actions/upload-artifact": 7,
    "actions/configure-pages": 6,
    "actions/upload-pages-artifact": 5,
    "actions/deploy-pages": 5,
}

USES_RE = re.compile(r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@v(\d+)")
NPM_RE = re.compile(r"npm\s+run\s+([A-Za-z0-9:_-]+)")
PATH_CMD_RE = re.compile(r"(?:python3|python|node|tsx|npx\s+tsx)\s+((?:tools|script|scripts|tests)/[^\s'\"|&;]+)")


def main() -> int:
    workflows = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    findings = []
    critical = 0
    warnings = 0

    for path in workflows:
        text = path.read_text(encoding="utf-8")
        item = {"workflow": str(path.relative_to(ROOT)), "errors": [], "warnings": [], "actions": []}
        if "jobs:" not in text:
            item["errors"].append("missing jobs section")
        if "workflow_dispatch:" not in text and "push:" not in text and "pull_request:" not in text and "schedule:" not in text and "issues:" not in text:
            item["errors"].append("no recognizable trigger")
        for action, major_text in USES_RE.findall(text):
            major = int(major_text)
            item["actions"].append(f"{action}@v{major}")
            allowed = MAX_MAJOR.get(action)
            if allowed is not None and major > allowed:
                item["errors"].append(f"unsupported or unverified action major: {action}@v{major}; expected <= v{allowed}")
        for script in NPM_RE.findall(text):
            if script not in SCRIPTS:
                item["errors"].append(f"missing npm script: {script}")
        for rel in PATH_CMD_RE.findall(text):
            clean = rel.rstrip("),]")
            if not (ROOT / clean).exists():
                item["errors"].append(f"missing referenced file: {clean}")
        if "bots/" in text and (ROOT / "App_bots").exists():
            item["warnings"].append("references legacy bots/ path; verify against canonical App_bots fleet")
        if "seed-bots" in text or "seed-buddy-bot" in text:
            item["warnings"].append("uses seed-file proxy; prefer current canonical fleet/generated registries")
        if "actions/checkout@v4" in text or "actions/setup-node@v4" in text or "actions/setup-python@v5" in text:
            item["warnings"].append("valid older action major; standardize to current DreamCo baseline when editing")
        critical += len(item["errors"])
        warnings += len(item["warnings"])
        findings.append(item)

    payload = {
        "schema": "dreamco.actions_health.v1",
        "workflow_count": len(workflows),
        "critical_error_count": critical,
        "warning_count": warnings,
        "baseline": {
            "checkout": "actions/checkout@v6",
            "setup_node": "actions/setup-node@v6",
            "setup_python": "actions/setup-python@v6",
            "upload_artifact": "actions/upload-artifact@v7",
            "configure_pages": "actions/configure-pages@v6",
            "upload_pages_artifact": "actions/upload-pages-artifact@v5",
            "deploy_pages": "actions/deploy-pages@v5"
        },
        "findings": findings,
        "truth_boundary": "Static workflow health catches missing/invalid references and stale architecture signals; a workflow is operational only after a GitHub Actions run succeeds."
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = ["# GitHub Actions Health Report", "", f"Workflows scanned: **{len(workflows)}**", f"Critical errors: **{critical}**", f"Warnings: **{warnings}**", ""]
    for item in findings:
        lines.append(f"## {item['workflow']}")
        if not item["errors"] and not item["warnings"]:
            lines.append("- ✅ No static problems found.")
        for value in item["errors"]:
            lines.append(f"- ❌ {value}")
        for value in item["warnings"]:
            lines.append(f"- ⚠️ {value}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"ok": critical == 0, "workflows": len(workflows), "critical_errors": critical, "warnings": warnings, "report": str(OUT_MD.relative_to(ROOT))}, indent=2))
    return 0 if critical == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
