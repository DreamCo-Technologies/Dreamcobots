#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
SUBBOT_REGISTRY = ROOT / "config" / "dreamco-must-have-subbot-team.json"
OUT = ROOT / "website" / "data" / "actions-control-center.json"
REPORT = ROOT / "reports" / "ACTIONS_CONTROL_CENTER.md"
REPO = "DreamCo-Technologies/Dreamcobots"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def workflow_name(text: str, fallback: str) -> str:
    match = re.search(r"(?m)^name:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip('"\'') if match else fallback


def triggers(text: str) -> list[str]:
    values = []
    for trigger in ["workflow_dispatch", "push", "pull_request", "schedule", "issues", "workflow_run"]:
        if re.search(rf"(?m)^\s{{0,4}}{re.escape(trigger)}\s*:", text):
            values.append(trigger)
    return values


def permissions(text: str) -> list[str]:
    found = []
    block = re.search(r"(?ms)^permissions:\s*\n((?:\s{2,}.+\n?)+)", text)
    if block:
        for key, value in re.findall(r"(?m)^\s+([a-z-]+):\s*([^#\n]+)", block.group(1)):
            found.append(f"{key}:{value.strip()}")
    inline = re.search(r"(?m)^permissions:\s*\{([^}]+)\}", text)
    if inline:
        for part in inline.group(1).split(","):
            found.append(part.strip())
    return found or ["default/read-limited"]


def purpose_for(name: str, filename: str) -> tuple[str, str, str]:
    key = f"{name} {filename}".lower()
    rules = [
        (("actions health",), "Reliability", "Scans every workflow for broken references, invalid action versions, missing scripts, and stale architecture assumptions.", "Use this first when the Actions page looks broadly broken."),
        (("codeql",), "Security", "Runs static security analysis against supported source languages and records code-scanning evidence.", "Use it to catch security weaknesses before release."),
        (("dependency review",), "Supply chain", "Reviews dependency changes and falls back to a locked install plus high-severity package audit when GitHub Dependency Graph is unavailable.", "Use it to keep third-party packages from becoming a silent release risk."),
        (("code trust",), "Release safety", "Combines change-impact checks, repository verification, supply-chain auditing, and a release-quality receipt.", "Use it as a serious engineering gate before trusted releases."),
        (("repository test",), "Testing", "Runs the governed repository test matrix, rebuilds derived evidence, and stops at the first actionable root-cause failure.", "Use it for normal engineering confidence after repository changes."),
        (("full system certification",), "Certification", "Runs the broad operational certification pipeline across fleet recovery, connections, sandboxes, benchmarks, security, and production smoke tests.", "Use it when you need the strongest available repository evidence, not for every small change."),
        (("master bot consolidation",), "Bot architecture", "Builds reversible specialist-to-master merge proposals without deleting capabilities or guessing usage.", "Use it to simplify the visible fleet while keeping specialist knowledge recoverable."),
        (("buddy actions test lab",), "Buddy testing", "Lets you choose quick, Buddy, API, resource, fleet, or full verification suites and preserves debugging evidence.", "Use this as the easiest manual test lab for Buddy."),
        (("control center",), "Owner operations", "Provides one manual owner entry point for common DreamCo checks without requiring command-line knowledge.", "Use this when you want a plain-language button instead of remembering scripts."),
        (("live dashboard",), "Owner visibility", "Builds a compact status run for Buddy, fleet, resources, website, Actions, or the whole quick system.", "Use it for a current operational snapshot."),
        (("deploy buddy", "pages"), "Deployment", "Builds the public Buddy site, runs deployment preflight checks, uploads the website artifact, and deploys GitHub Pages.", "Use it to publish only after the preflight is green."),
        (("engineering gap",), "Engineering improvement", "Turns measured platform gaps into parallel owner lanes and verifies proposed closure work.", "Use it to convert architecture gaps into bounded engineering work."),
        (("parallel benchmark",), "Benchmarking", "Plans non-overlapping benchmark-gap lanes and runs them in parallel under guardrails.", "Use it when many measured gaps can be worked independently."),
        (("open source evolution",), "Open-source intelligence", "Discovers public open-source AI metadata, checks model/dependency knowledge, and prepares parity evidence without auto-adopting code.", "Use it to learn from the ecosystem without bypassing license/security review."),
        (("platform evolution",), "Platform strategy", "Refreshes universal task coverage, note-to-code backlog, platform parity benchmarks, and bot curricula.", "Use it to measure how DreamCo is evolving as a platform."),
        (("business data trade",), "Business readiness", "Builds revenue-readiness, business curriculum, manufacturer-marketplace, and system-progress evidence.", "Use it to evaluate business-facing readiness without claiming live revenue."),
        (("government transparency",), "Public-sector intelligence", "Refreshes public fiscal evidence and government transparency benchmarks from approved public sources.", "Use it for source-backed public-sector analysis."),
        (("self working",), "Local autonomy", "Verifies local-first repository operation, generator registries, safe self-repair, and checkpoint evidence.", "Use it to test whether Buddy can keep useful work moving without pretending it has unlimited autonomy."),
        (("run everything",), "Maximum verification", "Runs the broadest configured repair/benchmark/status pass, preserves failures, and opens repair evidence when blockers remain.", "Use it deliberately; it is expensive and intentionally surfaces every failure."),
        (("failure watch",), "Incident response", "Watches workflow failures and prepares a focused repair handoff instead of leaving red runs unexplained.", "Use it to make Actions failures actionable for non-developers."),
        (("builder issue",), "Engineering workflow", "Reconciles builder issues against current repository evidence so stale tasks can be updated or closed safely.", "Use it to keep the engineering backlog synchronized with the code."),
    ]
    for needles, category, purpose, owner in rules:
        if any(needle in key for needle in needles):
            return category, purpose, owner
    if "test" in key or "verify" in key or "check" in key:
        return "Verification", "Runs repository-defined checks and preserves evidence for review.", "Use it when the named area changed or needs confidence."
    if "deploy" in key:
        return "Deployment", "Prepares or verifies a deployment workflow.", "Use it only after its prerequisite checks are green."
    return "Operations", "Automates a bounded DreamCo repository operation defined by this workflow.", "Open the details before running it; the page shows its triggers and permissions."


def evidence_for(text: str) -> list[str]:
    paths = sorted(set(re.findall(r"(?:reports|config/generated|tmp|website/data)/[A-Za-z0-9_./*${}-]+", text)))
    return paths[:10]


def likely_failures(text: str) -> list[str]:
    failures = []
    if "npm ci" in text:
        failures.append("lockfile/dependency install mismatch")
    if "npm audit" in text:
        failures.append("high-severity dependency vulnerability")
    if "python3" in text or "python " in text:
        failures.append("missing Python file/module or failing Python assertion")
    if "npx tsx" in text or "node --import tsx" in text:
        failures.append("TypeScript/runtime contract failure")
    if "github/codeql-action" in text:
        failures.append("CodeQL initialization or analysis failure")
    if "dependency-review-action" in text:
        failures.append("GitHub Dependency Graph unavailable or dependency policy failure")
    if "deploy-pages" in text:
        failures.append("Pages configuration, build, or deployment failure")
    return failures[:6] or ["workflow-specific command returned a non-zero result"]


def safety(text: str, perms: list[str]) -> tuple[str, str]:
    joined = " ".join(perms).lower()
    writes = any(":write" in item.replace(" ", "") for item in perms)
    if "pages:write" in joined or "contents: write" in joined or "issues: write" in joined:
        writes = True
    if writes:
        return "review", "This workflow has at least one write permission. Read its details before running it manually."
    if "npm audit" in text or "codeql" in text.lower():
        return "safe-check", "Read-only repository/security verification; it may fail the run but should not change production data."
    return "safe-check", "Designed as a read-only or repository-evidence check unless a later approved deployment/action step says otherwise."


def build_workflows() -> list[dict]:
    result = []
    for path in sorted(list(WORKFLOW_DIR.glob("*.yml")) + list(WORKFLOW_DIR.glob("*.yaml"))):
        text = read(path)
        name = workflow_name(text, path.stem)
        category, purpose, owner = purpose_for(name, path.name)
        perms = permissions(text)
        safety_level, safety_note = safety(text, perms)
        result.append({
            "name": name,
            "file": path.name,
            "category": category,
            "purpose": purpose,
            "owner_explanation": owner,
            "user_explanation": "This is internal DreamCo automation. Users benefit from the reliability or feature evidence it produces; users do not need to understand YAML to use Buddy.",
            "investor_explanation": "This workflow is part of DreamCo's evidence layer: repeatable engineering, security, release, or operating controls that reduce key-person dependency.",
            "engineer_explanation": "Open the workflow file for exact jobs/steps. The control center summarizes triggers, permissions, evidence outputs, and common failure classes so the implementation is easier to audit and adapt.",
            "triggers": triggers(text),
            "manual_run_supported": "workflow_dispatch" in text,
            "permissions": perms,
            "safety_level": safety_level,
            "safety_note": safety_note,
            "evidence_outputs": evidence_for(text),
            "likely_failures": likely_failures(text),
            "workflow_url": f"https://github.com/{REPO}/actions/workflows/{path.name}",
            "source_url": f"https://github.com/{REPO}/blob/main/.github/workflows/{path.name}",
        })
    return result


def main() -> int:
    subbots = json.loads(read(SUBBOT_REGISTRY))
    workflows = build_workflows()
    payload = {
        "schema": "dreamco.actions_control_center.v1",
        "title": "DreamCo Actions Control Center",
        "plain_english_mission": "Make DreamCo operable by an owner without engineering training while remaining transparent, testable, and adaptable for professional developers.",
        "audiences": {
            "owner": "See what each action does, what to press, what can break, and what evidence proves it worked.",
            "user": "Understand that Buddy is backed by repeatable checks, privacy controls, and visible operating boundaries.",
            "investor": "See operating discipline, release controls, reusable architecture, and evidence instead of unsupported readiness claims.",
            "engineer": "Get a fast repository runbook with direct workflow/source links, triggers, permissions, outputs, and failure classes."
        },
        "design_principles": [
            "One obvious owner entry point; many specialized workflows behind it.",
            "Every red run should identify a first actionable root cause.",
            "Every generated status distinguishes repository evidence from live production evidence.",
            "Master bots orchestrate; specialist roles remain reusable; temporary sub-bot teams prevent permanent-bot sprawl.",
            "No user-data connector is considered ready without authorization, provenance, export/delete controls, and purpose limits.",
            "Developers should be able to replace an adapter, model, storage layer, or deployment target without rewriting Buddy's core intent/routing model."
        ],
        "workflow_count": len(workflows),
        "workflows": workflows,
        "must_have_subbot_count": len(subbots["bots"]),
        "must_have_subbots": subbots["bots"],
        "subbot_architecture": {
            "architecture": subbots["architecture"],
            "spawn_rule": subbots["spawn_rule"],
            "merge_rule": subbots["merge_rule"],
            "data_rule": subbots["data_rule"]
        },
        "prospectus": {
            "owner": ["plain-language operations", "one-click links to manual workflows", "evidence-first status", "repair-first failure handling"],
            "users": ["personalization with control", "portable user data", "read-only-first connections", "searchable multimodal memory", "approval-gated external actions"],
            "investors": ["1,051-profile governed fleet baseline", "45-division product architecture", "master/sub-bot consolidation strategy", "repeatable CI and release evidence", "adapter-oriented platform design"],
            "developers": ["typed shared runtimes", "data-driven registries", "deterministic generators", "testable policies", "portable adapters", "direct evidence and source links"]
        },
        "truth_boundary": "This page explains repository automation and generated evidence. A green repository workflow does not by itself prove every external provider, deployment, payment flow, or user-data connector is live."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# DreamCo Actions Control Center",
        "",
        f"- Workflows explained: **{len(workflows)}**",
        f"- Must-have sub-bot blueprints: **{len(subbots['bots'])}**",
        "",
        "Every workflow entry includes a plain-English owner explanation, user/investor/engineer context, triggers, permissions, evidence outputs, likely failure classes, and direct GitHub links.",
        "",
        "## Workflows",
        "",
    ]
    for row in workflows:
        lines += [f"### {row['name']}", f"- Category: {row['category']}", f"- Purpose: {row['purpose']}", f"- Manual run: {row['manual_run_supported']}", f"- Safety: {row['safety_level']} — {row['safety_note']}", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "workflows": len(workflows), "subbots": len(subbots["bots"]), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
