#!/usr/bin/env python3
"""Generate local-first end-to-end readiness records for every structured bot."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOTS_DIR = ROOT / "bots"
MASTER_REGISTRY = ROOT / "config" / "master_bot_registry.json"
APP_BOTS_DIR = ROOT / "App_bots"
ORIGINAL_BOTS_DIR = ROOT / "original-bots"
MODEL_REGISTRY = ROOT / "config" / "buddy_user_model_choice_registry.json"
OUTPUT_DIR = ROOT / "config" / "generated" / "bot_end_to_end_readiness"
DIVISION_DIR = OUTPUT_DIR / "divisions"
OUTPUT_INDEX = OUTPUT_DIR / "index.json"
OUTPUT_REPORT = ROOT / "reports" / "BOT_END_TO_END_READINESS.md"
SLUG_RE = re.compile(r"[^a-z0-9]+")


LOCAL_FIRST_STAGES = [
    {
        "id": "intake",
        "label": "Task Intake",
        "required_output": "structured task brief with user goal, inputs, constraints, and approval level",
        "local_method": "Use bot profile, existing capabilities, local forms, local files, and deterministic templates.",
    },
    {
        "id": "plan",
        "label": "Build Plan",
        "required_output": "step-by-step workflow, needed files, test plan, and expected deliverables",
        "local_method": "Generate a rule-based plan from the bot division, category, description, and capabilities.",
    },
    {
        "id": "execute_sandbox",
        "label": "Sandbox Execution",
        "required_output": "local prototype, report, checklist, script output, or simulated workflow result",
        "local_method": "Run only local code, local fixtures, mock data, and no-key fallbacks unless the owner approves live integrations.",
    },
    {
        "id": "validate",
        "label": "Validation",
        "required_output": "syntax check, unit/smoke test, data-quality review, safety review, and failure notes",
        "local_method": "Prefer existing tests, Python compilation, TypeScript checks, JSON validation, and deterministic fixture replay.",
    },
    {
        "id": "package",
        "label": "Client Package",
        "required_output": "dashboard summary, prospectus page, export packet, and next approved action",
        "local_method": "Create local Markdown/JSON/HTML artifacts first; publish, email, charge, or submit only after approval.",
    },
]

APPROVAL_GATES = [
    "paid model calls",
    "live web scraping beyond allowed/public use",
    "sending email, SMS, calls, social posts, bids, or proposals",
    "collecting private or sensitive data",
    "using real voice, face, likeness, or private biography details",
    "collecting, moving, refunding, or reconciling money",
    "legal, medical, financial, employment, tenant, credit, or eligibility decisions",
    "production deploys, app-store submissions, marketplace listings, or domain purchases",
]

CATEGORY_REQUIREMENTS = {
    "coding": ["repo scan", "code generation", "local test", "debug packet", "pull request plan"],
    "coding-library": ["library usage guide", "starter scaffold", "API examples", "sandbox test", "performance check"],
    "dreamco-system": ["status check", "local operation plan", "dashboard card", "error handling", "operator runbook"],
    "system": ["coordination plan", "health check", "task queue", "dashboard status", "handoff report"],
    "leads": ["ICP brief", "mock lead list", "qualification rubric", "follow-up draft", "approval gate"],
    "outreach": ["message drafts", "sequence simulator", "opt-out checklist", "deliverability notes", "approval gate"],
    "intelligence": ["research packet", "scoring rubric", "evidence log", "comparison table", "recommendation"],
    "pipeline": ["stage map", "deal board schema", "reminder plan", "risk notes", "dashboard metrics"],
    "finance": ["scenario model", "risk note", "ledger export", "approval gate", "audit trail"],
    "payments": ["checkout readiness", "webhook sandbox", "receipt policy", "reconciliation checklist", "alert plan"],
    "education": ["lesson objective", "activity plan", "quiz/rubric", "accessibility check", "teacher notes"],
    "game": ["game design doc", "first playable slice", "save/load plan", "playtest checklist", "export plan"],
    "simulation": ["scenario spec", "variables", "deterministic engine", "replay log", "analysis report"],
    "legal": ["document checklist", "risk summary", "deadline log", "review gate", "client-safe draft"],
    "health": ["wellness note", "privacy-safe log", "risk disclaimer", "review gate", "resource packet"],
    "real-estate": ["property brief", "cash-flow model", "comparable checklist", "offer gate", "investor packet"],
    "marketing": ["campaign brief", "SEO checklist", "content calendar", "mock analytics", "approval gate"],
    "content": ["story brief", "asset rights check", "draft packet", "review checklist", "publish gate"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: Any) -> str:
    return SLUG_RE.sub("-", str(value or "item").lower()).strip("-") or "item"


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def discover_profiles() -> list[tuple[Path, dict[str, Any], str]]:
    profiles: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(BOTS_DIR.rglob("bot_profile.json")):
        payload = read_json(path, {})
        if isinstance(payload, dict):
            profiles.append((path, payload, "bots_profile"))
    return profiles


def discover_master_registry() -> list[tuple[Path, dict[str, Any], str]]:
    payload = read_json(MASTER_REGISTRY, {})
    bots = payload.get("bots") if isinstance(payload, dict) else []
    if not isinstance(bots, list):
        return []
    records = []
    for bot in bots:
        if not isinstance(bot, dict):
            continue
        profile_path = ROOT / str(bot.get("profile_path") or bot.get("repoPath") or MASTER_REGISTRY.relative_to(ROOT))
        records.append(
            (
                profile_path,
                {
                    "slug": bot.get("slug") or bot.get("id"),
                    "displayName": bot.get("name") or bot.get("displayName"),
                    "division": bot.get("division"),
                    "category": bot.get("category"),
                    "tier": bot.get("tier"),
                    "status": bot.get("status"),
                    "description": bot.get("description"),
                    "capabilities": bot.get("capabilities"),
                    "revenueModel": (bot.get("monetization") or {}).get("revenue_model") if isinstance(bot.get("monetization"), dict) else bot.get("revenueModel"),
                    "targetUsers": bot.get("targetUsers"),
                    "repoPath": bot.get("repoPath"),
                    "dashboard_url": bot.get("dashboard_url"),
                    "prospectus_url": bot.get("prospectus_url"),
                },
                "master_bot_registry",
            )
        )
    return records


def discover_app_division_systems() -> list[tuple[Path, dict[str, Any], str]]:
    records = []
    if not APP_BOTS_DIR.exists():
        return records
    for path in sorted(APP_BOTS_DIR.glob("*.json")):
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        name = payload.get("name") or path.stem
        records.append(
            (
                path,
                {
                    "slug": slugify(path.stem),
                    "displayName": f"{name} Division System",
                    "division": path.stem,
                    "category": "division-system",
                    "tier": payload.get("tier") or "system",
                    "status": payload.get("status") or "active",
                    "description": payload.get("mission") or payload.get("description") or f"{path.stem} division operating system.",
                    "capabilities": payload.get("capabilities") or payload.get("systems") or [],
                },
                "division_json_system",
            )
        )
    return records


def discover_code_only_original_bots() -> list[tuple[Path, dict[str, Any], str]]:
    records = []
    if not ORIGINAL_BOTS_DIR.exists():
        return records
    for path in sorted(ORIGINAL_BOTS_DIR.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        stem = path.stem
        if "bot" not in stem.lower() and "orchestrator" not in stem.lower() and "agent" not in stem.lower():
            continue
        slug = slugify(path.relative_to(ORIGINAL_BOTS_DIR).with_suffix("").as_posix())
        display = stem.replace("_", " ").replace("-", " ").title()
        records.append(
            (
                path,
                {
                    "slug": f"original-{slug}",
                    "displayName": f"Original {display}",
                    "division": "OriginalRecoveredSystems",
                    "category": "recovered-code-bot",
                    "tier": "archive",
                    "status": "reference",
                    "description": f"Recovered original code-only bot or orchestrator from {path.relative_to(ROOT)}.",
                    "capabilities": ["local code reference", "recovery candidate", "needs promotion tests"],
                },
                "original_code_only",
            )
        )
    return records


def discover_all_sources() -> list[tuple[Path, dict[str, Any], str]]:
    merged: dict[str, tuple[Path, dict[str, Any], str]] = {}
    source_priority = {
        "bots_profile": 4,
        "master_bot_registry": 3,
        "division_json_system": 2,
        "original_code_only": 1,
    }
    for path, profile, source in (
        discover_profiles()
        + discover_master_registry()
        + discover_app_division_systems()
        + discover_code_only_original_bots()
    ):
        slug = slugify(profile.get("slug") or path.stem)
        existing = merged.get(slug)
        if not existing or source_priority[source] > source_priority[existing[2]]:
            merged[slug] = (path, profile | {"slug": slug}, source)
    return list(merged.values())


def related_code_files(profile_path: Path, profile: dict[str, Any] | None = None) -> list[str]:
    if profile_path.is_file() and profile_path.suffix in {".py", ".ts", ".tsx", ".js", ".jsx"}:
        return [str(profile_path.relative_to(ROOT))]
    repo_path = (profile or {}).get("repoPath") if profile else None
    if repo_path:
        candidate = ROOT / str(repo_path)
        if candidate.is_file():
            return [str(candidate.relative_to(ROOT))]
        if candidate.is_dir():
            files = []
            for suffix in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx"):
                files.extend(sorted(candidate.glob(suffix)))
            return [str(path.relative_to(ROOT)) for path in files]
    bot_dir = profile_path.parent
    code_files = []
    for suffix in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx"):
        code_files.extend(sorted(bot_dir.glob(suffix)))
    return [str(path.relative_to(ROOT)) for path in code_files]


def related_tests(slug: str, display_name: str) -> list[str]:
    candidates = {slugify(slug), slugify(display_name), slugify(slug).replace("-", "_")}
    found = []
    tests_dir = ROOT / "tests"
    if not tests_dir.exists():
        return found
    for path in tests_dir.glob("test_*"):
        normalized = slugify(path.stem)
        if any(candidate and candidate in normalized for candidate in candidates):
            found.append(str(path.relative_to(ROOT)))
    return sorted(found)


def category_tasks(category: str, division: str, description: str) -> list[str]:
    text = f"{category} {division} {description}".lower()
    for key, tasks in CATEGORY_REQUIREMENTS.items():
        if key in text:
            return tasks
    return [
        "task-specific intake",
        "local workflow plan",
        "sandbox output",
        "quality checklist",
        "dashboard/prospectus packet",
    ]


def readiness_score(profile: dict[str, Any], code_files: list[str], tests: list[str]) -> tuple[int, list[str]]:
    score = 35
    missing: list[str] = []
    if profile.get("description"):
        score += 10
    else:
        missing.append("description")
    if profile.get("capabilities"):
        score += 15
    else:
        missing.append("capabilities")
    if code_files:
        score += 20
    else:
        missing.append("runtime code file")
    if tests:
        score += 10
    else:
        missing.append("direct test coverage")
    if profile.get("revenueModel") or profile.get("targetUsers"):
        score += 5
    else:
        missing.append("business model or target users")
    if profile.get("status") == "active":
        score += 5
    else:
        missing.append("active status")
    return min(score, 100), missing


def status_from_score(score: int, missing: list[str]) -> str:
    if score >= 85 and not missing:
        return "ready_for_local_end_to_end_testing"
    if score >= 70:
        return "mostly_ready_needs_targeted_tests"
    if score >= 55:
        return "needs_runtime_or_test_work"
    return "needs_buildout_before_client_demo"


def build_record(profile_path: Path, profile: dict[str, Any], model_choices: list[dict[str, Any]], source: str) -> dict[str, Any]:
    slug = slugify(profile.get("slug") or profile_path.parent.name)
    display_name = profile.get("displayName") or profile.get("name") or slug.replace("-", " ").title()
    division = profile.get("division") or "Unassigned"
    category = profile.get("category") or "general"
    description = profile.get("description") or ""
    code_files = related_code_files(profile_path, profile)
    tests = related_tests(slug, display_name)
    score, missing = readiness_score(profile, code_files, tests)
    local_tasks = category_tasks(category, division, description)
    optional_models = [
        {
            "id": choice.get("id"),
            "provider": choice.get("provider"),
            "best_for": choice.get("best_for", [])[:3],
            "optional_only": True,
        }
        for choice in model_choices[:6]
    ]
    return {
        "slug": slug,
        "displayName": display_name,
        "division": division,
        "category": category,
        "tier": profile.get("tier"),
        "status": profile.get("status", "unknown"),
        "profilePath": str(profile_path.relative_to(ROOT)),
        "source": source,
        "codeFiles": code_files,
        "tests": tests,
        "capabilities": profile.get("capabilities") or [],
        "taskContract": {
            "primary_mode": "local_first_no_external_provider_required",
            "can_run_without_other_providers": True,
            "optional_models_available": True,
            "local_first_tasks": local_tasks,
            "end_to_end_stages": LOCAL_FIRST_STAGES,
            "approval_gates": APPROVAL_GATES,
            "deliverables": [
                "task brief",
                "local sandbox result",
                "test evidence",
                "dashboard/prospectus summary",
                "next approved action packet",
            ],
            "provider_policy": {
                "default": "Use DreamCo local code, local storage, local fixtures, deterministic templates, and no-key fallbacks first.",
                "optional": "Use external AI models only when configured by the owner or selected by the user for quality, speed, or media generation.",
                "cost_control": "Budget-first routing, caching, and owner approval before paid calls.",
            },
            "model_options": optional_models,
        },
        "readiness": {
            "score": score,
            "status": status_from_score(score, missing),
            "missing": missing,
            "next_steps": [
                f"Add or verify {item}." for item in missing[:5]
            ] or ["Run direct smoke test and connect the bot card in Buddy/Actions."],
        },
    }


def main() -> None:
    generated_at = utc_now()
    model_registry = read_json(MODEL_REGISTRY, {})
    model_choices = model_registry.get("choices") if isinstance(model_registry, dict) else []
    if not isinstance(model_choices, list):
        model_choices = []

    source_records = discover_all_sources()
    records = [
        build_record(path, profile, model_choices, source)
        for path, profile, source in source_records
    ]
    records.sort(key=lambda item: (item["division"], item["displayName"], item["slug"]))

    by_division: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_division[slugify(record["division"])].append(record)

    DIVISION_DIR.mkdir(parents=True, exist_ok=True)
    for division_slug, division_records in by_division.items():
        (DIVISION_DIR / f"{division_slug}.json").write_text(
            json.dumps(
                {
                    "schema": "dreamco.bot_end_to_end_readiness.division.v1",
                    "generated_at": generated_at,
                    "division": division_records[0]["division"],
                    "bot_count": len(division_records),
                    "bots": division_records,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    status_counts = Counter(record["readiness"]["status"] for record in records)
    division_counts = Counter(record["division"] for record in records)
    source_counts = Counter(record["source"] for record in records)
    index = {
        "schema": "dreamco.bot_end_to_end_readiness.index.v1",
        "generated_at": generated_at,
        "mission": "Audit every structured bot one by one for provider-free local-first end-to-end task execution, while preserving optional model choice.",
        "policy": {
            "default_execution": "local_first_no_external_provider_required",
            "external_models": "optional_only_when_configured_or_user_selected",
            "approval_required_for": APPROVAL_GATES,
        },
        "totals": {
            "bots": len(records),
            "divisions": len(by_division),
            "source_counts": dict(sorted(source_counts.items())),
            "ready_for_local_end_to_end_testing": status_counts.get("ready_for_local_end_to_end_testing", 0),
            "mostly_ready_needs_targeted_tests": status_counts.get("mostly_ready_needs_targeted_tests", 0),
            "needs_runtime_or_test_work": status_counts.get("needs_runtime_or_test_work", 0),
            "needs_buildout_before_client_demo": status_counts.get("needs_buildout_before_client_demo", 0),
        },
        "division_shards": [
            {
                "division": division,
                "slug": slugify(division),
                "bot_count": count,
                "path": f"config/generated/bot_end_to_end_readiness/divisions/{slugify(division)}.json",
            }
            for division, count in sorted(division_counts.items())
        ],
        "sample_bots": records[:25],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    report_lines = [
        "# Bot End-To-End Readiness",
        "",
        f"Generated: {generated_at}",
        "",
        "## Policy",
        "",
        "- Every bot defaults to local-first execution with no external provider required.",
        "- Other AI models are optional routes for quality, media, long context, or user choice.",
        "- Paid calls, outreach, sensitive data, payments, legal/medical/financial decisions, publishing, and deployment stay behind approval gates.",
        "",
        "## Totals",
        "",
    ]
    for key, value in index["totals"].items():
        report_lines.append(f"- {key}: {value}")
    report_lines.extend(["", "## Sources", ""])
    for source, count in sorted(source_counts.items()):
        report_lines.append(f"- {source}: {count}")
    report_lines.extend(["", "## Divisions", ""])
    for shard in index["division_shards"]:
        report_lines.append(f"- {shard['division']}: {shard['bot_count']} bots -> `{shard['path']}`")
    report_lines.extend(["", "## First 25 Bots", ""])
    for record in records[:25]:
        report_lines.append(
            f"- {record['displayName']} (`{record['slug']}`): {record['readiness']['status']} ({record['readiness']['score']}/100)."
        )
    OUTPUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "bots": len(records), "divisions": len(by_division)}, indent=2))


if __name__ == "__main__":
    main()
