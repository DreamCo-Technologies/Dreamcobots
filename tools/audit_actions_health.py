#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
OUT_JSON = ROOT / "config" / "generated" / "actions-health-report.json"
OUT_MD = ROOT / "reports" / "ACTIONS_HEALTH_REPORT.md"
PUBLIC_JSON = ROOT / "website" / "data" / "actions-health-report.json"
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
SCRIPTS = set(PACKAGE.get("scripts", {}))

MAX_MAJOR = {
    "actions/checkout": 7,
    "actions/setup-node": 6,
    "actions/setup-python": 6,
    "actions/upload-artifact": 6,
    "actions/configure-pages": 6,
    "actions/upload-pages-artifact": 5,
    "actions/deploy-pages": 5,
}

USES_RE = re.compile(r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@v(\d+)")
NPM_RE = re.compile(r"npm\s+run\s+([A-Za-z0-9:_-]+)")
PATH_CMD_RE = re.compile(r"(?:python3|python|node|tsx|npx\s+tsx)\s+((?:tools|script|scripts|tests)/[^\s'\"|&;]+)")
NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)

WORKFLOW_PURPOSES = {
    "actions-failure-sweep.yml": "Find recent failed runs, group repeated failures, and prepare repair evidence.",
    "actions-failure-watch.yml": "Watch completed workflow runs and open a bounded failure investigation when needed.",
    "actions-health.yml": "Audit workflow syntax, action versions, script references, and stale repository paths.",
    "buddy-actions-test-lab.yml": "Run Buddy's governed test laboratory and preserve reviewable debug evidence.",
    "builder-issue-reconciler.yml": "Compare builder issues with current repository evidence and keep unresolved gaps visible.",
    "business-data-trade-readiness.yml": "Verify consent, ownership, licensing, and deletion controls for data products.",
    "code-trust-gate.yml": "Block unreviewed code from promotion when tests, evidence, or trust controls fail.",
    "codeql.yml": "Scan supported source code for security vulnerabilities with GitHub CodeQL.",
    "dependency-review.yml": "Review dependency changes for known risk before a pull request is merged.",
    "deploy-buddy-pages.yml": "Validate and deploy the static Buddy experience to GitHub Pages.",
    "dreamco-control-center.yml": "Coordinate repository health, registry checks, and control-center evidence.",
    "dreamco-live-dashboard.yml": "Build dashboard evidence across registered DreamCo modules and workflows.",
    "dreamco-platform-evolution.yml": "Measure platform gaps and prepare bounded improvement proposals.",
    "engineering-gap-closure.yml": "Turn verified engineering gaps into prioritized, testable repair work.",
    "full-system-certification.yml": "Run the broad release-candidate certification suite across the repository.",
    "government-transparency-refresh.yml": "Refresh public-government resource catalogs with provenance checks.",
    "open-source-evolution.yml": "Evaluate open-source opportunities without promoting unreviewed code.",
    "parallel-benchmark-gap-builders.yml": "Run independent benchmark lanes and collect evidence for remaining gaps.",
    "repository-test-matrix.yml": "Exercise the repository's language, generator, policy, and site test matrix.",
    "run-everything-now.yml": "Provide an owner-triggered, bounded entry point for the full verification stack.",
    "self-working-system.yml": "Schedule local-first maintenance checks and stop at guarded external actions.",
}

WORKFLOW_UPGRADES = {
    "actions-failure-sweep.yml": ["Fingerprint repeated failures by workflow, job, and failing step.", "Link each repair proposal to the exact run logs and commit SHA.", "Track recurrence so fixed failures can be proven closed."],
    "actions-failure-watch.yml": ["Deduplicate alerts from the same root cause.", "Add a cooldown so noisy failures do not create repeated work.", "Escalate only after the log and affected path are captured."],
    "actions-health.yml": ["Publish the generated health catalog to the Actions dashboard.", "Flag unpinned or unexpectedly new action majors.", "Compare every referenced command with package scripts and repository files."],
    "buddy-actions-test-lab.yml": ["Split contract, integration, and browser evidence into named artifacts.", "Add a retry only for explicitly classified flaky infrastructure failures.", "Record the exact dependency lock hash with every test result."],
    "builder-issue-reconciler.yml": ["Attach repository evidence before changing an issue state.", "Group duplicate goals without deleting unique requirements.", "Require a passing test reference before marking build work complete."],
    "business-data-trade-readiness.yml": ["Verify consent and resale rights per source record.", "Exercise deletion and export requests with synthetic fixtures.", "Block packages that lack provenance or retention limits."],
    "code-trust-gate.yml": ["Require clean-install type checking and production build evidence.", "Publish change-impact coverage for every edited executable file.", "Keep protected actions behind explicit owner approval."],
    "codeql.yml": ["Scan every supported language present in the repository.", "Upload actionable locations and affected paths.", "Measure unresolved high-severity findings before release."],
    "dependency-review.yml": ["Require GitHub Dependency Graph before treating this check as operational.", "Fail on newly introduced critical vulnerabilities.", "Document an owner-reviewed exception path with expiration dates."],
    "deploy-buddy-pages.yml": ["Run link, JavaScript, and mobile layout checks before deployment.", "Publish the Actions and benchmark catalogs in the offline shell.", "Add a post-deploy smoke test against the Pages URL."],
    "dreamco-control-center.yml": ["Summarize failed gates by owner and affected system.", "Link dashboard states to generated repository evidence.", "Prevent unknown states from being displayed as healthy."],
    "dreamco-live-dashboard.yml": ["Replace hard-coded module assumptions with generated registry mappings.", "Expose evidence age and last successful run per module.", "Separate repository-ready status from live-provider readiness."],
    "dreamco-platform-evolution.yml": ["Rank proposals by user value, risk, cost, and evidence gap.", "Create changes only on review branches.", "Require rollback evidence before promotion."],
    "engineering-gap-closure.yml": ["Assign each gap a reproducible fixture and acceptance gate.", "Cap parallel work to the available runner budget.", "Close gaps only when the relevant regression test passes."],
    "full-system-certification.yml": ["Partition fast required gates from longer evidence suites.", "Publish a machine-readable release certificate.", "Block certification when generated artifacts drift from source."],
    "government-transparency-refresh.yml": ["Use official sources and record retrieval dates.", "Detect stale, moved, or withdrawn programs.", "Keep eligibility language informational and source-linked."],
    "open-source-evolution.yml": ["Verify licenses and provenance before sandboxing a project.", "Benchmark in an isolated environment with fixed resource limits.", "Require human review before generated changes reach a protected branch."],
    "parallel-benchmark-gap-builders.yml": ["Give each lane an independent timeout and artifact.", "Compare results only on identical fixtures and versions.", "Stop lanes whose cost or failure threshold exceeds policy."],
    "repository-test-matrix.yml": ["Test from a clean dependency install on supported runtimes.", "Map each failed suite to the files and contracts it protects.", "Publish coverage gaps alongside pass counts."],
    "run-everything-now.yml": ["Show the estimated runner cost before dispatch.", "Allow owners to select safe test groups instead of always running all jobs.", "Require explicit inputs for any networked or external-write lane."],
    "self-working-system.yml": ["Keep scheduled work read-only or sandboxed by default.", "Pause automatically after repeated failures or budget limits.", "Require fresh approval for every outside write, payment, or outreach action."],
}

TRIGGER_PATTERNS = {
    "manual": r"^\s*workflow_dispatch\s*:",
    "push": r"^\s*push\s*:",
    "pull request": r"^\s*pull_request(?:_target)?\s*:",
    "schedule": r"^\s*schedule\s*:",
    "issues": r"^\s*issues\s*:",
    "workflow completion": r"^\s*workflow_run\s*:",
}


def main() -> int:
    workflows = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    findings = []
    critical = 0
    warnings = 0

    for path in workflows:
        text = path.read_text(encoding="utf-8")
        filename = path.name
        display_name_match = NAME_RE.search(text)
        triggers = [label for label, pattern in TRIGGER_PATTERNS.items() if re.search(pattern, text, re.MULTILINE)]
        npm_scripts = sorted(set(NPM_RE.findall(text)))
        referenced_files = sorted({value.rstrip("),]") for value in PATH_CMD_RE.findall(text)})
        item = {
            "workflow": str(path.relative_to(ROOT)),
            "filename": filename,
            "display_name": display_name_match.group(1).strip('"\'') if display_name_match else path.stem.replace("-", " ").title(),
            "purpose": WORKFLOW_PURPOSES.get(filename, "Run a governed repository workflow and collect reviewable evidence."),
            "triggers": triggers,
            "errors": [],
            "warnings": [],
            "actions": [],
            "npm_scripts": npm_scripts,
            "referenced_files": referenced_files,
            "controls": {
                "permissions_declared": bool(re.search(r"^permissions\s*:", text, re.MULTILINE)),
                "concurrency_declared": bool(re.search(r"^concurrency\s*:", text, re.MULTILINE)),
                "job_timeouts_declared": len(re.findall(r"^\s+timeout-minutes\s*:", text, re.MULTILINE)),
                "runner_jobs": len(re.findall(r"^\s+runs-on\s*:", text, re.MULTILINE)),
                "artifacts_declared": "actions/upload-artifact@" in text or "actions/upload-pages-artifact@" in text,
            },
            "upgrades": WORKFLOW_UPGRADES.get(filename, [
                "Add a deterministic repository fixture.",
                "Publish reviewable evidence for every failure.",
                "Require owner approval before external writes.",
            ]),
            "github_url": f"https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/{filename}",
        }
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
        for script in npm_scripts:
            if script not in SCRIPTS:
                item["errors"].append(f"missing npm script: {script}")
        for clean in referenced_files:
            if not (ROOT / clean).exists():
                item["errors"].append(f"missing referenced file: {clean}")
        if re.search(r"(?<![A-Za-z0-9_-])bots/", text) and not (ROOT / "bots").exists():
            item["warnings"].append("references missing legacy bots/ path")
        if "seed-bots" in text or "seed-buddy-bot" in text:
            item["warnings"].append("uses seed-file proxy; prefer current canonical fleet/generated registries")
        if "actions/checkout@v4" in text or "actions/setup-node@v4" in text or "actions/setup-python@v5" in text:
            item["warnings"].append("valid older action major; standardize to current DreamCo baseline when editing")
        critical += len(item["errors"])
        warnings += len(item["warnings"])
        item["static_status"] = "blocked" if item["errors"] else ("review" if item["warnings"] else "static_checks_passed")
        findings.append(item)

    payload = {
        "schema": "dreamco.actions_health.v1",
        "workflow_count": len(workflows),
        "critical_error_count": critical,
        "warning_count": warnings,
        "operational_workflow_count": 0,
        "live_evidence_note": "The browser refreshes public GitHub run data when available. Static checks alone never prove a workflow is operational.",
        "baseline": {
            "checkout": "actions/checkout@v7",
            "setup_node": "actions/setup-node@v6",
            "setup_python": "actions/setup-python@v6",
            "upload_artifact": "actions/upload-artifact@v6",
            "configure_pages": "actions/configure-pages@v6",
            "upload_pages_artifact": "actions/upload-pages-artifact@v5",
            "deploy_pages": "actions/deploy-pages@v5"
        },
        "findings": findings,
        "truth_boundary": "Static workflow health catches missing/invalid references and stale architecture signals; a workflow is operational only after a GitHub Actions run succeeds."
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    PUBLIC_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

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
