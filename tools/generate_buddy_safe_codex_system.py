#!/usr/bin/env python3
"""Generate Buddy's safe local code-management system."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "buddy_safe_codex_system.json"
CODE_BOTS_PATH = ROOT / "config" / "buddy_safe_codex_code_bots.json"
MASTER_REGISTRY_PATH = ROOT / "config" / "master_bot_registry.json"
REPORT_PATH = ROOT / "reports" / "BUDDY_SAFE_CODEX_SYSTEM.md"

CODE_BOT_TERMS = [
    "code",
    "coding",
    "debug",
    "developer",
    "software",
    "library",
    "frontend",
    "backend",
    "deploy",
    "test",
    "repo",
    "pull request",
    "api",
    "webhook",
    "workflow",
    "devops",
    "ci",
    "build",
    "typescript",
    "python",
    "javascript",
    "react",
    "database",
    "docker",
    "kubernetes",
]


SAFE_CODEX_SYSTEM = {
    "schema": "dreamco.buddy_safe_codex_system.v1",
    "mission": "Make Buddy manage repository code like a safe local coding agent: detect problems, plan repairs, run local checks, prepare patches, and request approval before risky actions.",
    "default_mode": "local_first_dry_run_until_owner_approval",
    "operating_loop": [
        {
            "id": "observe",
            "label": "Observe",
            "goal": "Collect repo status, changed files, failing checks, logs, task failures, bot readiness gaps, and GitHub issue/PR context.",
            "local_tools": ["git status", "repository_steward", "local_import_audit", "registry_drift_detector", "bot_end_to_end_readiness"],
            "outputs": ["problem inventory", "risk labels", "affected files"],
        },
        {
            "id": "classify",
            "label": "Classify",
            "goal": "Route each problem to the right fix lane and decide whether it is safe for local repair.",
            "code_bot_council": "config/buddy_safe_codex_code_bots.json",
            "lanes": ["syntax", "types", "imports", "tests", "registry", "bot contract", "frontend", "backend", "workflow", "dependency", "security", "docs"],
            "outputs": ["root-cause guess", "repair lane", "approval need"],
        },
        {
            "id": "plan",
            "label": "Plan",
            "goal": "Create a small repair plan with expected files, commands, tests, rollback notes, and success criteria.",
            "outputs": ["patch plan", "test plan", "rollback plan"],
        },
        {
            "id": "repair",
            "label": "Repair",
            "goal": "Apply tightly scoped local fixes only inside the repository and never overwrite unrelated user work.",
            "outputs": ["local patch", "changed-file summary"],
        },
        {
            "id": "verify",
            "label": "Verify",
            "goal": "Run deterministic local checks and capture evidence before claiming the issue is fixed.",
            "required_gates": ["git diff --check", "json validation", "python compile where relevant", "TypeScript check", "production build when frontend/backend changed"],
            "outputs": ["test evidence", "remaining failures", "known warnings"],
        },
        {
            "id": "ship_packet",
            "label": "Ship Packet",
            "goal": "Prepare commit/PR/release notes with human-readable risks and approval gates.",
            "outputs": ["commit message", "PR body", "owner approval checklist"],
        },
        {
            "id": "learn",
            "label": "Learn",
            "goal": "Record only useful recurring failure patterns, fix recipes, and prevention checks.",
            "outputs": ["useful memory", "new lint/test idea", "bot readiness update"],
        },
    ],
    "approval_gates": [
        "pushing branches or opening pull requests",
        "merging or closing pull requests/issues",
        "installing dependencies",
        "running networked commands",
        "changing secrets or credentials",
        "deploying production",
        "running paid model calls",
        "modifying payment, legal, medical, finance, identity, or public-safety behavior",
        "deleting files or reverting user changes",
    ],
    "problem_lanes": {
        "syntax": {
            "signals": ["parser error", "compile error", "unexpected token", "invalid JSON"],
            "first_tools": ["python3 -m py_compile", "node --check", "python3 -m json.tool"],
            "safe_default": "fix locally and re-run parser check",
        },
        "types": {
            "signals": ["tsc error", "missing type", "type mismatch"],
            "first_tools": ["pnpm run check"],
            "safe_default": "minimal type-correct patch and re-run TypeScript",
        },
        "imports": {
            "signals": ["ModuleNotFoundError", "Cannot find module", "import path"],
            "first_tools": ["tools/local_import_audit.py", "rg import"],
            "safe_default": "fix path aliases, package exports, or local import guards",
        },
        "tests": {
            "signals": ["failing test", "assertion", "snapshot", "playwright"],
            "first_tools": ["targeted test", "fixture replay", "repository_steward"],
            "safe_default": "fix production code first; update tests only when expected behavior changed",
        },
        "registry": {
            "signals": ["drift", "missing bot", "duplicate slug", "catalog mismatch"],
            "first_tools": ["generate_master_bot_registry.py", "registry_drift_detector.py", "validate_bot_registry.py"],
            "safe_default": "regenerate structured outputs and validate",
        },
        "security": {
            "signals": ["secret", "injection", "unsafe eval", "auth bypass"],
            "first_tools": ["secret scan", "security-scan", "code review"],
            "safe_default": "stop, redact, add guardrail, and request owner review for sensitive fixes",
        },
        "workflow": {
            "signals": ["GitHub Actions failure", "CI", "workflow syntax", "permissions"],
            "first_tools": ["repository_steward", "gh logs when available"],
            "safe_default": "fix workflow in sandbox branch; avoid activating expensive schedules by default",
        },
    },
    "memory_policy": {
        "store_only": ["failure pattern", "root cause", "successful fix recipe", "test command", "affected subsystem"],
        "do_not_store": ["secrets", "private customer data", "raw tokens", "unneeded logs", "personal sensitive data"],
        "retention": "Keep compact recipes and discard noisy raw output after report generation.",
    },
    "local_first_model_policy": {
        "default": "Use deterministic local tools and repository context before any AI provider.",
        "optional_models": "External models may help summarize, compare fixes, or generate code, but only when configured and approved.",
        "cost_control": "Use cached reports and minimal context. Never run paid model calls for routine lint, JSON, TypeScript, or compile checks.",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def classify_code_bot(bot: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(bot.get(key, ""))
        for key in ("slug", "name", "displayName", "division", "category", "description")
    ).lower()
    capabilities = " ".join(str(item) for item in (bot.get("capabilities") or [])).lower()
    full_text = f"{text} {capabilities}"
    lanes = []
    lane_terms = {
        "frontend": ["frontend", "react", "vue", "angular", "svelte", "ui", "css", "tailwind"],
        "backend": ["backend", "api", "server", "express", "fastify", "database", "sql", "drizzle"],
        "testing": ["test", "testing", "qa", "playwright", "vitest", "pytest", "benchmark"],
        "debugging": ["debug", "error", "repair", "recovery", "incident"],
        "devops": ["deploy", "devops", "docker", "kubernetes", "github actions", "ci", "cloud"],
        "registry": ["registry", "catalog", "bot library", "monorepo", "index"],
        "ai_tooling": ["openai", "anthropic", "gemini", "ollama", "llm", "model", "prompt"],
        "game_3d": ["three", "unity", "godot", "phaser", "game", "3d", "webgl"],
        "security": ["security", "compliance", "secret", "auth", "audit"],
    }
    for lane, terms in lane_terms.items():
        if any(term in full_text for term in terms):
            lanes.append(lane)
    return lanes or ["general_code"]


def discover_code_bots(generated_at: str) -> dict[str, Any]:
    registry = read_json(MASTER_REGISTRY_PATH, {})
    bots = registry.get("bots") if isinstance(registry, dict) else []
    records = []
    for bot in bots if isinstance(bots, list) else []:
        if not isinstance(bot, dict):
            continue
        text = " ".join(
            str(bot.get(key, ""))
            for key in ("slug", "name", "displayName", "division", "category", "description")
        ).lower()
        if bot.get("division") != "DreamCodeLab" and not any(term in text for term in CODE_BOT_TERMS):
            continue
        records.append(
            {
                "slug": bot.get("slug") or bot.get("id"),
                "name": bot.get("name") or bot.get("displayName"),
                "division": bot.get("division"),
                "category": bot.get("category"),
                "status": bot.get("status"),
                "repoPath": bot.get("repoPath"),
                "profilePath": bot.get("profile_path"),
                "lanes": classify_code_bot(bot),
                "safe_codex_role": "optional specialist reviewer and repair planner for Buddy",
                "approval_required_before": [
                    "editing files outside its lane",
                    "installing dependencies",
                    "running networked checks",
                    "pushing, opening PRs, deploying, or spending money",
                ],
            }
        )
    records.sort(key=lambda item: (item.get("division") or "", item.get("name") or "", item.get("slug") or ""))
    by_lane: dict[str, list[str]] = {}
    for record in records:
        for lane in record["lanes"]:
            by_lane.setdefault(lane, []).append(record["slug"])
    return {
        "schema": "dreamco.buddy_safe_codex_code_bots.v1",
        "generated_at": generated_at,
        "mission": "Give Buddy a code-bot council for repository repair, debugging, tests, deployment prep, library expertise, and safe autonomous code management.",
        "policy": {
            "default": "Buddy remains the coordinator and final local judge; code bots advise by lane.",
            "local_first": True,
            "external_models_optional": True,
            "owner_approval_required_for_live_changes": True,
        },
        "total_code_bots": len(records),
        "lane_counts": {lane: len(slugs) for lane, slugs in sorted(by_lane.items())},
        "lanes": {lane: slugs[:75] for lane, slugs in sorted(by_lane.items())},
        "bots": records,
    }


def main() -> None:
    generated_at = utc_now()
    code_bots = discover_code_bots(generated_at)
    payload = SAFE_CODEX_SYSTEM | {"generated_at": generated_at}
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    CODE_BOTS_PATH.write_text(json.dumps(code_bots, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Buddy Safe Codex System",
        "",
        f"Generated: {generated_at}",
        "",
        "## Mission",
        "",
        payload["mission"],
        "",
        "## Operating Loop",
        "",
    ]
    for step in payload["operating_loop"]:
        lines.append(f"- {step['label']}: {step['goal']}")
    lines.extend(["", "## Approval Gates", ""])
    for gate in payload["approval_gates"]:
        lines.append(f"- {gate}")
    lines.extend(["", "## Local-First Policy", ""])
    lines.append(f"- Default: {payload['local_first_model_policy']['default']}")
    lines.append(f"- Optional models: {payload['local_first_model_policy']['optional_models']}")
    lines.append(f"- Cost control: {payload['local_first_model_policy']['cost_control']}")
    lines.extend(["", "## Code-Bot Council", ""])
    lines.append(f"- Total code bots connected: {code_bots['total_code_bots']}")
    for lane, count in code_bots["lane_counts"].items():
        lines.append(f"- {lane}: {count}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "config": str(CONFIG_PATH.relative_to(ROOT)), "code_bots": code_bots["total_code_bots"]}, indent=2))


if __name__ == "__main__":
    main()
