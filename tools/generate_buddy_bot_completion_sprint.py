#!/usr/bin/env python3
"""Build Buddy's ASAP bot-completion sprint queue."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NATIVE_COVERAGE = ROOT / "config" / "generated" / "buddy_native_bot_coverage.json"
SPRINT_JSON = ROOT / "config" / "generated" / "buddy_bot_completion_sprint.json"
REPORT_MD = ROOT / "reports" / "BUDDY_BOT_COMPLETION_SPRINT.md"

SUPPORT_PREFIXES = (
    "__tests__/",
    "tests/",
    "tools/",
    "scripts/",
    "data/",
    "reports/",
    "config/",
    "docs/",
    "automation-tools/",
)

SUPPORT_PATH_PARTS = (
    "/scripts/",
    "/examples/",
    "/__tests__/",
    "/tests/",
)

PRODUCT_PREFIXES = (
    "bots/",
    "Business_bots/",
    "Marketing_bots/",
    "Real_Estate_bots/",
    "Fiverr_bots/",
    "Occupational_bots/",
    "ConnectionsControl/",
    "communication_bot/",
    "python_bots/",
    "original-bots/",
    "healthcare-tools/",
    "analytics-elites/",
)

LIVE_GATED_TASKS = {
    "finance",
    "sales_and_leads",
    "legal_and_compliance",
    "health_and_care",
    "security",
    "real_estate",
}

COMPLETION_TEMPLATE = [
    "add stable Bot class or repair existing class name",
    "add deterministic analyze/list/run methods that return dictionaries",
    "add local sandbox input fixtures",
    "add smoke test covering free/local behavior",
    "add approval packet for live money, outreach, account, personal-data, or deploy actions",
    "connect Buddy route and dashboard/prospectus metadata",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_role(path: str) -> str:
    if path.startswith(SUPPORT_PREFIXES):
        return "support_tool_or_test"
    if any(part in f"/{path}" for part in SUPPORT_PATH_PARTS):
        return "support_tool_or_test"
    if path.startswith(PRODUCT_PREFIXES):
        return "product_bot"
    return "uncategorized_code"


def is_wrapper_delegate(path: str) -> bool:
    full_path = ROOT / path
    if not full_path.exists():
        return False
    text = full_path.read_text(encoding="utf-8", errors="ignore")
    if "from " not in text or "import " not in text:
        return False
    if "__main__" not in text and ".run(" not in text and "main()" not in text:
        return False
    content_lines = [
        line
        for line in text.splitlines()
        if line.strip()
        and not line.strip().startswith("#")
        and not line.strip().startswith('"""')
        and not line.strip().startswith("'''")
    ]
    return len(content_lines) <= 15


def priority_score(bot: dict[str, Any]) -> int:
    score = 100 - int(bot.get("runnable_score", 0))
    tasks = bot.get("task_types", [])
    score += 10 * sum(1 for task in tasks if task in LIVE_GATED_TASKS)
    if bot.get("approval_required_for_live_use"):
        score += 5
    if "general_automation" in tasks:
        score -= 5
    return max(score, 0)


def completion_status(bot: dict[str, Any]) -> str:
    if is_wrapper_delegate(bot["path"]):
        return "wrapper_delegate_verify_target"
    status = bot.get("implementation_status", "")
    if status == "native_runnable_candidate":
        return "ready_candidate_keep_testing"
    if status == "partial_native_implementation":
        return "finish_interface_and_tests"
    return "code_core_runtime_now"


def sprint_batch(index: int) -> str:
    if index < 25:
        return "batch_01_asap_revenue_and_core"
    if index < 75:
        return "batch_02_customer_facing"
    if index < 150:
        return "batch_03_category_depth"
    return "batch_04_long_tail_completion"


def build_payload() -> dict[str, Any]:
    coverage = read_json(NATIVE_COVERAGE)
    bots = coverage.get("bots", [])
    rows: list[dict[str, Any]] = []
    role_counts = Counter()
    status_counts = Counter()
    product_status_counts = Counter()
    for bot in bots:
        role = file_role(bot["path"])
        status = bot.get("implementation_status", "unknown")
        role_counts[role] += 1
        status_counts[status] += 1
        if role == "product_bot":
            product_status_counts[status] += 1
        sprint_status = completion_status(bot)
        if role != "product_bot" or status == "native_runnable_candidate" or sprint_status == "wrapper_delegate_verify_target":
            continue
        rows.append(
            {
                "path": bot["path"],
                "name": bot["name"],
                "task_types": bot.get("task_types", []),
                "current_status": status,
                "completion_status": sprint_status,
                "runnable_score": bot.get("runnable_score", 0),
                "priority_score": priority_score(bot),
                "approval_required_for_live_use": bot.get("approval_required_for_live_use", False),
                "optional_model_detected": bot.get("optional_model_detected", False),
                "fix_steps": COMPLETION_TEMPLATE,
            }
        )
    rows.sort(key=lambda row: (-row["priority_score"], row["path"]))
    for index, row in enumerate(rows):
        row["sprint_batch"] = sprint_batch(index)
        row["sprint_rank"] = index + 1
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for task in row["task_types"]:
            by_task[task].append({"rank": row["sprint_rank"], "name": row["name"], "path": row["path"]})
    return {
        "schema": "dreamco.buddy_bot_completion_sprint.v1",
        "generated_at": utc_now(),
        "mission": "Drive every product bot toward fully coded, locally testable, Buddy-routable operation as fast as possible.",
        "policy": {
            "native_code_first": True,
            "no_fake_completion_claims": True,
            "asap_rule": "Fix highest-priority product bots first, regenerate coverage, rerun smoke checks, then repeat until incomplete count is zero.",
            "paid_or_live_actions": "approval-gated even after bot code is complete",
        },
        "summary": {
            "all_scanned_files": len(bots),
            "product_bot_files": role_counts.get("product_bot", 0),
            "support_tool_or_test_files": role_counts.get("support_tool_or_test", 0),
            "uncategorized_code_files": role_counts.get("uncategorized_code", 0),
            "product_native_runnable_candidates": product_status_counts.get("native_runnable_candidate", 0),
            "product_partial_implementations": product_status_counts.get("partial_native_implementation", 0),
            "product_need_core_runtime": product_status_counts.get("needs_native_completion", 0),
            "product_completion_queue": len(rows),
        },
        "status_counts_all_scanned": dict(status_counts),
        "completion_queue": rows,
        "queue_by_task": {task: items[:25] for task, items in sorted(by_task.items())},
    }


def write_report(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Buddy Bot Completion Sprint",
        "",
        "This is the ASAP queue for getting every product bot fully coded, locally testable, and Buddy-routable.",
        "",
        "## Summary",
        "",
        f"- Product bot files: {summary['product_bot_files']}",
        f"- Product native runnable candidates: {summary['product_native_runnable_candidates']}",
        f"- Product partial implementations: {summary['product_partial_implementations']}",
        f"- Product bots needing core runtime: {summary['product_need_core_runtime']}",
        f"- Product completion queue: {summary['product_completion_queue']}",
        f"- Support/test/tool files separated out: {summary['support_tool_or_test_files']}",
        "",
        "## ASAP Top 50",
        "",
    ]
    for row in payload["completion_queue"][:50]:
        lines.append(
            f"- #{row['sprint_rank']} `{row['name']}` at `{row['path']}` "
            f"({row['completion_status']}, score {row['runnable_score']}, {row['sprint_batch']})"
        )
    lines.extend(
        [
            "",
            "## Completion Definition",
            "",
            "A bot is not treated as finished until it has deterministic local behavior, structured outputs, a smoke test, Buddy routing metadata, and approval gates for live/money/account/personal-data actions.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy's ASAP bot completion sprint.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not SPRINT_JSON.exists() or not REPORT_MD.exists():
            raise SystemExit("Bot completion sprint files are missing. Run without --check.")
        payload = read_json(SPRINT_JSON)
        assert payload["summary"]["product_bot_files"] >= 1
        print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
        return 0
    SPRINT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    SPRINT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
