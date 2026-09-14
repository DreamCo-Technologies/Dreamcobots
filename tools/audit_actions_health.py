#!/usr/bin/env python3
"""Build a deterministic, public-safe prospectus of every GitHub Actions workflow."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
OUT_JSON = ROOT / "config" / "generated" / "actions-health-report.json"
OUT_MD = ROOT / "reports" / "ACTIONS_HEALTH_REPORT.md"
PUBLIC_JSON = ROOT / "website" / "data" / "actions-health-report.json"
PACKAGE = json.loads((ROOT / "package.json").read_text())
SCRIPTS = set(PACKAGE.get("scripts", {}))

# MAX_MAJOR is the preferred baseline. MIN_MAJOR prevents genuinely obsolete
# releases from passing. A supported release below MAX_MAJOR is maintenance
# debt, not evidence that a workflow is broken.
MAX_MAJOR = {"actions/checkout": 7, "actions/setup-node": 7, "actions/setup-python": 7, "actions/upload-artifact": 6, "actions/configure-pages": 6, "actions/upload-pages-artifact": 5, "actions/deploy-pages": 5}
MIN_MAJOR = {"actions/checkout": 4, "actions/setup-node": 4, "actions/setup-python": 5, "actions/upload-artifact": 4, "actions/configure-pages": 5, "actions/upload-pages-artifact": 4, "actions/deploy-pages": 4}
USES_RE = re.compile(r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@v(\d+)")
NPM_RE = re.compile(r"npm\s+run\s+([A-Za-z0-9:_-]+)")
PATH_CMD_RE = re.compile(r"(?:python3|python|node|tsx|npx\s+tsx)\s+((?:tools|script|scripts|tests)/[^\s\'\"|&;]+)")
NAME_RE = re.compile(r"^name:\s*[\"']?(.+?)[\"']?\s*$", re.M)
STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*[\"']?(.+?)[\"']?\s*$", re.M)
TRIGGERS = [("manual", r"^\s+workflow_dispatch\s*:"), ("push", r"^\s+push\s*:"), ("pull request", r"^\s+pull_request(?:_target)?\s*:"), ("schedule", r"^\s+schedule\s*:"), ("issues", r"^\s+issues\s*:"), ("workflow completion", r"^\s+workflow_run\s*:")]

PURPOSE_RULES = [
    (("pages", "website", "site", "deploy"), "deployment", "Publish and verify the public Buddy experience", "Builds public assets, checks generated evidence, and prepares a governed deployment."),
    (("benchmark", "eval", "score", "leaderboard"), "benchmarks", "Measure Buddy capability with reproducible evidence", "Runs declared benchmark or evaluation commands and preserves their results."),
    (("security", "codeql", "secret", "dependency", "defense"), "security", "Reduce security, dependency, and credential risk", "Runs bounded security checks and reports findings without exposing secrets."),
    (("health", "doctor", "audit", "lint"), "repository health", "Keep the repository inspectable and maintainable", "Checks repository structure, policy, or code health and reports actionable failures."),
    (("test", "ci", "quality", "verify", "validation"), "verification", "Catch regressions before release", "Runs deterministic checks or tests and fails when required evidence does not pass."),
    (("sync", "catalog", "data", "registry", "inventory", "index", "map"), "evidence data", "Keep generated registries and dashboards current", "Regenerates or verifies machine-readable repository evidence used by Buddy and GitHub Pages."),
    (("build", "release", "package", "docker", "image"), "build and release", "Produce a reviewable software artifact", "Builds or packages a bounded artifact and retains the workflow run as evidence."),
    (("agent", "bot", "buddy", "automation"), "Buddy automation", "Operate one governed Buddy capability", "Runs a bounded Buddy automation with repository permissions and failure visibility."),
]


def infer_purpose(filename: str, display_name: str) -> tuple[str, str, str]:
    text = f"{filename} {display_name}".lower()
    for keywords, goal, purpose, happens in PURPOSE_RULES:
        if any(keyword in text for keyword in keywords):
            return goal, purpose, happens
    return "repository operations", f"Operate {display_name} as a bounded DreamCo repository workflow", "Executes the named workflow steps and records the GitHub Actions result."


def benchmark_commands(npm: list[str], refs: list[str]) -> list[str]:
    terms = ("test", "benchmark", "eval", "quality", "check", "audit", "verify")
    commands = [f"npm run {script}" for script in npm if any(term in script.lower() for term in terms)]
    commands.extend(ref for ref in refs if any(term in ref.lower() for term in terms))
    return sorted(set(commands))


def workflow_signature(item: dict) -> str | None:
    signature = {
        "triggers": item["triggers"],
        "actions": sorted(set(item["actions"])),
        "npm_scripts": item["npm_scripts"],
        "referenced_files": item["referenced_files"],
        "steps": [step.lower() for step in item["what_happens"]],
        "runner_jobs": item["controls"]["runner_jobs"],
    }
    if not signature["actions"] and not signature["npm_scripts"] and not signature["referenced_files"] and not signature["steps"]:
        return None
    return hashlib.sha256(json.dumps(signature, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]


def main() -> int:
    workflows = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    findings: list[dict] = []
    critical = 0
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        filename = path.name
        name_match = NAME_RE.search(text)
        display_name = name_match.group(1).strip() if name_match else filename.removesuffix(".yml").removesuffix(".yaml").replace("-", " ").title()
        goal, purpose, generic_happens = infer_purpose(filename, display_name)
        triggers = [name for name, pattern in TRIGGERS if re.search(pattern, text, re.M)]
        if not triggers and re.search(r"^on\s*:\s*$", text, re.M):
            triggers = ["declared"]
        errors: list[str] = []
        warnings: list[str] = []
        actions: list[str] = []
        upgrades: list[str] = []
        if "jobs:" not in text:
            errors.append("missing jobs section")
        if not triggers:
            errors.append("no recognizable trigger")
        for action, major_s in USES_RE.findall(text):
            major = int(major_s)
            actions.append(f"{action}@v{major}")
            preferred = MAX_MAJOR.get(action)
            minimum = MIN_MAJOR.get(action)
            if minimum is not None and major < minimum:
                errors.append(f"obsolete action major: {action}@v{major}; minimum supported major is v{minimum}")
            elif preferred is not None and major < preferred:
                upgrades.append(f"upgrade recommendation: {action}@v{major} -> v{preferred}")
        npm = sorted(set(NPM_RE.findall(text)))
        for script in npm:
            if script not in SCRIPTS:
                errors.append(f"missing npm script: {script}")
        refs = sorted({value.rstrip("),]") for value in PATH_CMD_RE.findall(text)})
        for ref in refs:
            if not (ROOT / ref).exists():
                errors.append(f"missing referenced file: {ref}")
        steps = [step.strip() for step in STEP_NAME_RE.findall(text)]
        controls = {
            "permissions_declared": bool(re.search(r"^permissions\s*:", text, re.M)),
            "concurrency_declared": bool(re.search(r"^concurrency\s*:", text, re.M)),
            "job_timeouts_declared": len(re.findall(r"^\s+timeout-minutes\s*:", text, re.M)),
            "runner_jobs": len(re.findall(r"^\s+runs-on\s*:", text, re.M)),
            "artifacts_declared": "actions/upload-artifact@" in text or "actions/upload-pages-artifact@" in text,
        }
        outputs = ["GitHub Actions run log"]
        if controls["artifacts_declared"]:
            outputs.append("declared downloadable or deployment artifact")
        if "actions/deploy-pages@" in text:
            outputs.append("GitHub Pages deployment")
        critical += len(errors)
        findings.append({
            "workflow": str(path.relative_to(ROOT)),
            "filename": filename,
            "display_name": display_name,
            "goal": goal,
            "purpose": purpose,
            "what_happens": steps or [generic_happens],
            "triggers": triggers,
            "errors": errors,
            "warnings": warnings,
            "actions": actions,
            "npm_scripts": npm,
            "referenced_files": refs,
            "benchmark_commands": benchmark_commands(npm, refs),
            "outputs": outputs,
            "controls": controls,
            "upgrades": ["Publish machine-readable evidence for every run.", "Keep external writes behind explicit authorization and bounded policy.", "Preserve failures and regressions instead of converting unknown states into passes."] + upgrades,
            "github_url": f"https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/{filename}",
            "static_status": "blocked" if errors else "static_checks_passed",
            "maintenance_status": "recommended_upgrade" if upgrades else "current_baseline",
            "runtime_status": "unknown_until_run_evidence_loaded",
            "possible_duplicate": False,
            "duplicate_candidate_group": None,
            "possible_duplicates": [],
        })

    groups: dict[str, list[dict]] = defaultdict(list)
    for item in findings:
        signature = workflow_signature(item)
        if signature:
            groups[signature].append(item)
    duplicate_groups = []
    for signature, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        paths = sorted(item["workflow"] for item in members)
        duplicate_groups.append({"id": signature, "workflows": paths, "review_status": "manual_review_required", "reason": "Matching triggers, actions, commands, referenced files, named steps, and runner-job count."})
        for item in members:
            item["possible_duplicate"] = True
            item["duplicate_candidate_group"] = signature
            item["possible_duplicates"] = [path for path in paths if path != item["workflow"]]

    warnings = sum(len(item["warnings"]) for item in findings)
    summary = {
        "workflows": len(findings),
        "static_passing_workflows": sum(item["static_status"] == "static_checks_passed" for item in findings),
        "static_failing_workflows": sum(item["static_status"] != "static_checks_passed" for item in findings),
        "runtime_passing_workflows": 0,
        "runtime_failing_workflows": 0,
        "runtime_unknown_workflows": len(findings),
        "possible_duplicate_groups": len(duplicate_groups),
        "possible_duplicate_workflows": sum(item["possible_duplicate"] for item in findings),
        "workflows_with_benchmark_commands": sum(bool(item["benchmark_commands"]) for item in findings),
        "goal_counts": dict(sorted(Counter(item["goal"] for item in findings).items())),
    }
    payload = {
        "schema": "dreamco.actions_health.v2",
        "workflow_count": len(workflows),
        "critical_error_count": critical,
        "warning_count": warnings,
        "operational_workflow_count": 0,
        "summary": summary,
        "duplicate_candidate_groups": duplicate_groups,
        "live_evidence_note": "Static checks do not prove runtime operation; successful GitHub Actions runs provide operational evidence.",
        "baseline": {"checkout": "actions/checkout@v7", "setup_node": "actions/setup-node@v7", "setup_python": "actions/setup-python@v7", "upload_artifact": "actions/upload-artifact@v6", "configure_pages": "actions/configure-pages@v6", "upload_pages_artifact": "actions/upload-pages-artifact@v5", "deploy_pages": "actions/deploy-pages@v5"},
        "supported_minimums": {key: f"{key}@v{value}" for key, value in MIN_MAJOR.items()},
        "findings": findings,
        "truth_boundary": "Static workflow health distinguishes supported action versions from upgrade recommendations. Duplicate candidates require manual review. Runtime success must be established by GitHub Actions execution evidence.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    PUBLIC_JSON.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_JSON.write_text(json.dumps(payload, separators=(",", ":")) + "\n")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# GitHub Actions Health Report", "", f"Workflows scanned: **{len(workflows)}**", f"Static passing: **{summary['static_passing_workflows']}**", f"Critical errors: **{critical}**", f"Possible duplicate groups: **{summary['possible_duplicate_groups']}**", "", "> Static analysis is not runtime proof. Possible duplicates require human review before consolidation.", ""]
    for item in findings:
        lines.extend([f"## {item['display_name']}", f"- Workflow: `{item['workflow']}`", f"- Goal: {item['goal']}", f"- Purpose: {item['purpose']}", f"- Static status: `{item['static_status']}`", f"- Runtime status: `{item['runtime_status']}`", f"- Possible duplicate: **{'yes' if item['possible_duplicate'] else 'no'}**"])
        lines.extend(f"- ❌ {error}" for error in item["errors"])
        if not item["errors"]:
            lines.append("- ✅ No static blockers found.")
        lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({"ok": critical == 0, "workflows": len(workflows), "critical_errors": critical, "warnings": warnings, "possible_duplicate_groups": len(duplicate_groups), "report": str(OUT_MD.relative_to(ROOT))}, indent=2))
    return 0 if critical == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
