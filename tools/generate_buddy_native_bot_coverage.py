#!/usr/bin/env python3
"""Generate Buddy's repo-native bot coverage map.

This audit does not import bot modules. It statically inspects repository code so
broken optional dependencies cannot stop Buddy from discovering usable local code.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_JSON = ROOT / "config" / "generated" / "buddy_native_bot_coverage.json"
REPORT_MD = ROOT / "reports" / "BUDDY_NATIVE_BOT_COVERAGE.md"

BOT_FILE_PATTERNS = ("bot", "agent", "buddy")
SKIP_PARTS = {".git", "node_modules", "dist", ".venv", "__pycache__"}

TASK_KEYWORDS: dict[str, list[str]] = {
    "coding": ["code", "coder", "debug", "program", "software", "devops", "github", "webhook", "sandbox", "builder"],
    "business_building": ["business", "llc", "startup", "franchise", "plan", "commerce"],
    "sales_and_leads": ["sales", "lead", "closer", "follow", "prospect", "crm"],
    "marketing": ["marketing", "seo", "ads", "brand", "content", "campaign", "social"],
    "finance": ["finance", "loan", "grant", "tax", "payroll", "invoice", "payment", "cash"],
    "real_estate": ["real_estate", "property", "mortgage", "tenant", "lease", "zoning", "auction"],
    "creative_media": ["music", "voice", "image", "video", "photo", "artist", "arts", "asset", "creator"],
    "education": ["education", "course", "learning", "school", "reading", "lesson", "student"],
    "games_and_simulations": ["game", "simulation", "3d", "physics", "unity", "unreal", "sim"],
    "operations": ["ops", "workflow", "scheduler", "inventory", "supply", "transport", "maintenance"],
    "customer_support": ["support", "ticket", "service", "chat", "faq"],
    "data_and_research": ["data", "research", "analytics", "warehouse", "scrape", "search"],
    "legal_and_compliance": ["legal", "contract", "compliance", "privacy", "policy"],
    "health_and_care": ["health", "medical", "mental", "care", "fitness"],
    "security": ["security", "cyber", "risk", "trust", "fraud", "protection"],
}

WEAK_MARKERS = [
    "todo",
    "pass",
    "notimplemented",
    "placeholder",
    "stub",
    "mock_data",
    "sample_data",
]

MODEL_MARKERS = [
    "openai",
    "anthropic",
    "gemini",
    "huggingface",
    "llm",
    "model",
    "api_key",
]

LIVE_ACTION_MARKERS = [
    "payment",
    "charge",
    "email",
    "sms",
    "post",
    "publish",
    "deploy",
    "delete",
    "transfer",
    "outreach",
    "background",
    "clone",
]


@dataclass
class BotAudit:
    path: str
    name: str
    task_types: list[str]
    classes: list[str]
    functions: list[str]
    runnable_score: int
    native_code_first: bool
    optional_model_detected: bool
    implementation_status: str
    approval_required_for_live_use: bool
    evidence: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_name(value: str) -> str:
    value = value.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in value.split())


def choose_bot_name(path: Path, classes: list[str]) -> str:
    for class_name in classes:
        lowered = class_name.lower()
        if (lowered.endswith("bot") or "bot" in lowered) and not lowered.endswith("error") and not lowered.endswith("exception"):
            return class_name
    for class_name in classes:
        lowered = class_name.lower()
        if not lowered.endswith("error") and not lowered.endswith("exception"):
            return class_name
    return normalize_name(path.stem)


def task_match_score(audit: BotAudit, task: str) -> int:
    keywords = TASK_KEYWORDS.get(task, [])
    haystack = " ".join([audit.path, audit.name, *audit.classes, *audit.functions]).lower()
    score = sum(5 for keyword in keywords if keyword in haystack)
    if task.replace("_", "-") in haystack or task in haystack:
        score += 20
    if audit.name.lower().endswith("bot"):
        score += 10
    return score + audit.runnable_score


def is_bot_path(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    lowered = path.name.lower()
    return path.suffix == ".py" and any(pattern in lowered for pattern in BOT_FILE_PATTERNS)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_python(path: Path, text: str) -> tuple[list[str], list[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], []
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return classes[:20], functions[:30]


def infer_tasks(path: Path, text: str) -> list[str]:
    haystack = f"{path.as_posix()} {text[:3000]}".lower()
    tasks = [
        task
        for task, keywords in TASK_KEYWORDS.items()
        if any(keyword in haystack for keyword in keywords)
    ]
    return tasks[:6] or ["general_automation"]


def score_bot(path: Path, text: str, classes: list[str], functions: list[str]) -> tuple[int, list[str]]:
    lowered = text.lower()
    score = 0
    evidence: list[str] = []
    if classes:
        score += 25
        evidence.append(f"{len(classes)} class definitions")
    if functions:
        score += min(30, len(functions) * 3)
        evidence.append(f"{len(functions)} function definitions")
    if re.search(r"\breturn\b", text):
        score += 10
        evidence.append("returns structured results")
    if re.search(r"\b(dict|list|dataclass|BaseModel|TypedDict)\b", text):
        score += 10
        evidence.append("uses structured data")
    if "if __name__" in text or "argparse" in lowered:
        score += 10
        evidence.append("has runnable entrypoint")
    if "runtime.py" in path.as_posix() or path.name == "runtime.py":
        score += 10
        evidence.append("runtime module")
    weak_hits = sum(1 for marker in WEAK_MARKERS if marker in lowered)
    score -= min(25, weak_hits * 5)
    if weak_hits:
        evidence.append(f"{weak_hits} weak implementation markers")
    return max(0, min(score, 100)), evidence


def implementation_status(score: int, text: str) -> str:
    lowered = text.lower()
    if score >= 70 and "notimplemented" not in lowered:
        return "native_runnable_candidate"
    if score >= 40:
        return "partial_native_implementation"
    return "needs_native_completion"


def audit_bot(path: Path) -> BotAudit:
    rel = path.relative_to(ROOT).as_posix()
    text = read_text(path)
    classes, functions = parse_python(path, text)
    score, evidence = score_bot(path, text, classes, functions)
    lowered = text.lower()
    optional_model_detected = any(marker in lowered for marker in MODEL_MARKERS)
    approval_required = any(marker in lowered for marker in LIVE_ACTION_MARKERS)
    name = choose_bot_name(path, classes)
    status = implementation_status(score, text)
    return BotAudit(
        path=rel,
        name=name,
        task_types=infer_tasks(path, text),
        classes=classes,
        functions=functions[:12],
        runnable_score=score,
        native_code_first=score >= 40,
        optional_model_detected=optional_model_detected,
        implementation_status=status,
        approval_required_for_live_use=approval_required,
        evidence=evidence,
    )


def collect_bots() -> list[BotAudit]:
    audits = [audit_bot(path) for path in ROOT.rglob("*.py") if is_bot_path(path)]
    audits.sort(key=lambda item: (-item.runnable_score, item.path))
    return audits


def build_task_routes(audits: list[BotAudit]) -> list[dict[str, Any]]:
    grouped: dict[str, list[BotAudit]] = {}
    for audit in audits:
        for task in audit.task_types:
            grouped.setdefault(task, []).append(audit)
    routes = []
    for task, items in sorted(grouped.items()):
        items = sorted(items, key=lambda item: -task_match_score(item, task))
        usable = [item for item in items if item.native_code_first]
        best = usable[0] if usable else items[0]
        routes.append(
            {
                "task_type": task,
                "primary_native_bot": best.name,
                "primary_native_path": best.path,
                "fallback_native_paths": [item.path for item in usable[1:6]],
                "native_coverage": "ready_candidate" if best.runnable_score >= 70 else "partial",
                "optional_model_after_native": True,
                "approval_required_for_live_use": any(item.approval_required_for_live_use for item in items[:10]),
                "candidate_count": len(items),
            }
        )
    return routes


def build_payload() -> dict[str, Any]:
    audits = collect_bots()
    status_counts: dict[str, int] = {}
    for audit in audits:
        status_counts[audit.implementation_status] = status_counts.get(audit.implementation_status, 0) + 1
    task_routes = build_task_routes(audits)
    return {
        "schema": "dreamco.buddy_native_bot_coverage.v1",
        "generated_at": utc_now(),
        "mission": "Make Buddy route to DreamCo repo-native bot code before any optional model/resource.",
        "policy": {
            "default_execution": "native_repo_code_first",
            "optional_models": "used only for user-selected model help, incomplete native coverage, or explicitly approved premium routing",
            "live_actions": "payment, outreach, account, publishing, cloning, deploy, and personal-data actions require approval",
        },
        "summary": {
            "python_bot_agent_files": len(audits),
            "native_runnable_candidates": status_counts.get("native_runnable_candidate", 0),
            "partial_native_implementations": status_counts.get("partial_native_implementation", 0),
            "needs_native_completion": status_counts.get("needs_native_completion", 0),
            "task_route_count": len(task_routes),
        },
        "task_routes": task_routes,
        "bots": [audit.__dict__ for audit in audits],
    }


def write_report(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Buddy Native Bot Coverage",
        "",
        "Buddy should try repository-native bot code first. Optional models are backup helpers, not the default owner of the task.",
        "",
        "## Summary",
        "",
        f"- Python bot/agent files scanned: {summary['python_bot_agent_files']}",
        f"- Native runnable candidates: {summary['native_runnable_candidates']}",
        f"- Partial native implementations: {summary['partial_native_implementations']}",
        f"- Needs native completion: {summary['needs_native_completion']}",
        f"- Native task routes: {summary['task_route_count']}",
        "",
        "## Native Task Routes",
        "",
    ]
    for route in payload["task_routes"]:
        lines.append(
            f"- `{route['task_type']}` -> `{route['primary_native_bot']}` at `{route['primary_native_path']}` "
            f"({route['native_coverage']}, {route['candidate_count']} candidates)"
        )
    lines.extend(
        [
            "",
            "## Operating Rule",
            "",
            "Buddy should only ask an optional model/resource after native code has been checked, when the user chooses model help, or when a capability is not yet fully implemented locally.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy repo-native bot coverage.")
    parser.add_argument("--check", action="store_true", help="Validate generated files instead of rewriting.")
    args = parser.parse_args()

    if args.check:
        if not COVERAGE_JSON.exists() or not REPORT_MD.exists():
            raise SystemExit("Native bot coverage files are missing. Run without --check.")
        payload = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
        assert payload["summary"]["python_bot_agent_files"] >= 1
        assert payload["summary"]["task_route_count"] >= 1
        print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
        return 0

    COVERAGE_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    COVERAGE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
