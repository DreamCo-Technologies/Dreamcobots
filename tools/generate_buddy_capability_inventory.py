#!/usr/bin/env python3
"""Generate Buddy capability and bot readiness inventory reports."""

from __future__ import annotations

import csv
import ast
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
APPROVAL_REGISTRY_FILE = ROOT / "config" / "production_approvals" / "high_risk_bot_approvals.json"
REQUIRED_BUDDY_MONEY_REQUEST = (
    "Buddy, help me make money with this bot. "
    "I approve the listed live actions and understand the risks."
)
LIBRARY_NAMES = ("tools", "apis", "webhooks", "workflows", "skills", "sandboxes")
IMPLEMENTATION_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}
SKIP_IMPLEMENTATION_NAMES = {
    "__init__.py",
    "tiers.py",
    "bot_profile.json",
    "README.md",
    "requirements.txt",
    "Dockerfile",
    "config.py",
}
PLACEHOLDER_RE = re.compile(
    r"NotImplementedError|pass\s*(#.*)?$|TODO",
    re.IGNORECASE | re.MULTILINE,
)
SLUG_RE = re.compile(r"[^a-z0-9]+")


def normalize(value: object) -> str:
    return SLUG_RE.sub("-", str(value).lower()).strip("-")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - report should preserve read errors
        return {"_error": str(exc)}


def current_branch() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return None


def library_coverage() -> tuple[dict[str, int], dict[str, set[str]]]:
    counts: dict[str, int] = {}
    by_slug: dict[str, set[str]] = {name: set() for name in LIBRARY_NAMES}
    for name in LIBRARY_NAMES:
        path = ROOT / "config" / "generated" / "system_libraries" / f"{name}.json"
        if not path.exists():
            counts[name] = 0
            continue
        data = load_json(path)
        entries = data.get("entries", [])
        counts[name] = len(entries)
        for entry in entries:
            bot_id = entry.get("bot_id") or entry.get("bot_slug") or entry.get("slug")
            if bot_id:
                by_slug[name].add(str(bot_id))
    return counts, by_slug


def test_files() -> list[Path]:
    files = list((ROOT / "tests").rglob("test_*.py"))
    control_tower = ROOT / "dreamco-control-tower"
    files += list(control_tower.glob("**/*.test.js"))
    files += list(control_tower.glob("**/*.test.jsx"))
    return sorted(files)


def related_tests(slug: str, name: str, files: list[Path]) -> list[str]:
    normalized_slug = normalize(slug)
    normalized_name = normalize(name)
    matches: list[str] = []
    for path in files:
        stem = path.stem
        if stem.startswith("test_"):
            stem = stem.removeprefix("test_")
        elif stem.startswith("test-"):
            stem = stem.removeprefix("test-")
        normalized_test = normalize(stem)
        if normalized_slug and (normalized_slug in normalized_test or normalized_test in normalized_slug):
            matches.append(str(path.relative_to(ROOT)))
        elif normalized_name and (normalized_name in normalized_test or normalized_test in normalized_name):
            matches.append(str(path.relative_to(ROOT)))
    return sorted(set(matches))[:20]


def implementation_files(folder: Path) -> tuple[list[str], list[str]]:
    files: list[str] = []
    marker_hits: list[str] = []
    for path in sorted(folder.iterdir()):
        if (
            path.is_file()
            and path.suffix in IMPLEMENTATION_EXTENSIONS
            and path.name not in SKIP_IMPLEMENTATION_NAMES
        ):
            relative = str(path.relative_to(ROOT))
            files.append(relative)
            text = path.read_text(encoding="utf-8", errors="ignore")[:20_000]
            if has_blocking_placeholder(path, text):
                marker_hits.append(relative)
    return files, marker_hits


def has_blocking_placeholder(path: Path, text: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if "TODO" in stripped or "NotImplementedError" in stripped:
            return True
        if not stripped or stripped.startswith("#"):
            continue

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Pass):
            continue
        parent = parent_node(tree, node)
        if isinstance(parent, ast.ClassDef) and is_exception_class(parent):
            continue
        if isinstance(parent, ast.ExceptHandler):
            continue
        return True
    return False


def parent_node(tree: ast.AST, target: ast.AST) -> ast.AST | None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            if child is target:
                return node
    return None


def is_exception_class(node: ast.ClassDef) -> bool:
    if not node.name.lower().endswith(("error", "exception")):
        return False
    return len(node.body) == 1 and isinstance(node.body[0], ast.Pass)


def risk_hint(slug: str, name: str, description: str) -> str:
    high_risk_terms = (
        "trading",
        "crypto",
        "payment",
        "legal",
        "medical",
        "health",
        "security",
        "defense",
        "tax",
        "loan",
        "credit",
        "wallet",
        "fraud",
    )
    searchable = normalize(f"{slug} {name} {description}")
    return "high" if any(term in searchable for term in high_risk_terms) else "standard"


def load_approval_registry() -> dict:
    if not APPROVAL_REGISTRY_FILE.exists():
        return {"approvals": []}
    data = load_json(APPROVAL_REGISTRY_FILE)
    if not isinstance(data.get("approvals"), list):
        data["approvals"] = []
    return data


def approvals_by_slug(registry: dict) -> dict[str, dict]:
    return {
        str(entry.get("slug")): entry
        for entry in registry.get("approvals", [])
        if entry.get("slug")
    }


def buddy_money_approval_for_bot(slug: str, approvals: dict[str, dict]) -> dict:
    approval = approvals.get(str(slug), {})
    checklist = approval.get("checklist", {})
    allowed_live_actions = approval.get("allowed_live_actions") or []
    required_request = approval.get("required_buddy_money_request")
    valid = all(
        [
            approval.get("approved") is True,
            approval.get("approved_by"),
            approval.get("approved_at"),
            approval.get("user_asked_buddy_to_help_make_money") is True,
            required_request == REQUIRED_BUDDY_MONEY_REQUEST,
            approval.get("risk_acknowledged") is True,
            bool(allowed_live_actions),
            checklist.get("sandbox_smoke_test_passed") is True,
            checklist.get("no_unapproved_live_money_movement") is True,
            checklist.get("secrets_are_environment_only") is True,
            checklist.get("audit_logging_enabled") is True,
            checklist.get("human_review_before_external_action") is True,
        ]
    )
    return {
        "approved": valid,
        "registry_entry_found": bool(approval),
        "approved_by": approval.get("approved_by"),
        "approved_at": approval.get("approved_at"),
        "required_buddy_money_request": REQUIRED_BUDDY_MONEY_REQUEST,
        "allowed_live_actions": allowed_live_actions,
        "risk_acknowledged": approval.get("risk_acknowledged") is True,
        "user_asked_buddy_to_help_make_money": approval.get(
            "user_asked_buddy_to_help_make_money"
        )
        is True,
    }


def coding_path_for_bot(
    *,
    build_state: str,
    test_state: str,
    has_all_libraries: bool,
    marker_hits: list[str],
    risk: str,
) -> dict:
    gates = [
        "profile",
        "implementation",
        "tool_contract",
        "api_contract",
        "webhook_contract",
        "workflow_contract",
        "skill_contract",
        "sandbox_contract",
        "tests",
        "review",
    ]
    completed = ["profile"]
    if build_state != "profile_only_being_built":
        completed.append("implementation")
    if has_all_libraries:
        completed.extend(
            [
                "tool_contract",
                "api_contract",
                "webhook_contract",
                "workflow_contract",
                "skill_contract",
                "sandbox_contract",
            ]
        )
    if test_state == "ready_for_test_run":
        completed.append("tests")
    if test_state in {"ready_for_test_run", "ready_for_contract_testing"} and not marker_hits:
        completed.append("review")

    if test_state == "needs_implementation_before_testing":
        status = "needs_core_implementation"
        next_step = "Create or map the bot implementation file, then regenerate contracts and tests."
        target_workflow = "bot-submission.yml"
    elif build_state == "profiled_from_existing_system_needs_direct_impl_check":
        status = "needs_existing_system_mapping"
        next_step = "Map the profile to its concrete implementation files and add a direct smoke test."
        target_workflow = "bot-health-scan.yml"
    elif marker_hits:
        status = "needs_placeholder_review"
        next_step = "Review placeholder-like markers, replace stubs with real behavior, then add or run focused tests."
        target_workflow = "dreamco-debug-audit.yml"
    elif test_state == "ready_for_contract_testing":
        status = "needs_direct_test_coverage"
        next_step = "Promote generated contracts into direct unit or integration tests for the bot."
        target_workflow = "framework-compliance.yml"
    else:
        status = "on_full_code_path"
        next_step = "Run existing tests, keep contracts current, and expand behavior through reviewed pull requests."
        target_workflow = "pr-test-validation.yml"

    return {
        "status": status,
        "next_step": next_step,
        "target_workflow": target_workflow,
        "completed_gates": completed,
        "remaining_gates": [gate for gate in gates if gate not in completed],
        "human_approval_required": risk == "high",
        "has_full_coding_path": True,
    }


def production_readiness_for_bot(
    *,
    implementation_count: int,
    marker_hits: list[str],
    has_all_libraries: bool,
    test_state: str,
    risk: str,
    buddy_money_approval: dict,
) -> dict:
    blockers: list[str] = []
    if implementation_count == 0:
        blockers.append("missing_core_implementation")
    if marker_hits:
        blockers.append("placeholder_review_required")
    if not has_all_libraries:
        blockers.append("missing_generated_contracts")
    if test_state != "ready_for_test_run":
        blockers.append("direct_test_coverage_required")
    if risk == "high" and not buddy_money_approval["approved"]:
        blockers.append("buddy_money_help_user_approval_required")

    fully_coded = not any(
        blocker
        in {
            "missing_core_implementation",
            "placeholder_review_required",
            "direct_test_coverage_required",
        }
        for blocker in blockers
    )

    if not blockers:
        status = "production_ready"
        next_step = "Keep tests green and monitor production telemetry."
    elif fully_coded and blockers == ["buddy_money_help_user_approval_required"]:
        status = "production_candidate_approval_required"
        next_step = (
            "User must ask Buddy to help make money, acknowledge the risk, "
            "and approve allowed live actions before production release."
        )
    elif "missing_core_implementation" in blockers:
        status = "not_ready_missing_implementation"
        next_step = "Build or map core implementation files, then regenerate readiness reports."
    elif "placeholder_review_required" in blockers:
        status = "not_ready_placeholder_review"
        next_step = "Replace placeholder-like code paths with real behavior and focused tests."
    elif "direct_test_coverage_required" in blockers:
        status = "not_ready_needs_tests"
        next_step = "Add direct unit or integration tests and run the production readiness gate."
    else:
        status = "not_ready_contract_or_review_gap"
        next_step = "Complete generated contracts, review evidence, and production safety checks."

    return {
        "status": status,
        "fully_coded": fully_coded,
        "production_ready": status == "production_ready",
        "blockers": blockers,
        "next_step": next_step,
        "buddy_money_approval": buddy_money_approval,
    }


def classify_bot(
    profile_path: Path,
    profile: dict,
    library_by_slug: dict[str, set[str]],
    tests: list[Path],
    approvals: dict[str, dict],
) -> dict:
    slug = profile.get("slug") or profile_path.parent.name
    name = (
        profile.get("displayName")
        or profile.get("name")
        or str(slug).replace("-", " ").replace("_", " ").title()
    )
    impl_files, marker_hits = implementation_files(profile_path.parent)
    related = related_tests(str(slug), str(name), tests)
    libraries = {name: str(slug) in library_by_slug[name] for name in LIBRARY_NAMES}
    has_all_libraries = all(libraries.values())
    runtime_file = str((profile_path.parent / "runtime.py").relative_to(ROOT))
    has_generated_runtime = runtime_file in impl_files
    has_generated_smoke_test = any(
        "/generated_bot_smoke/" in test and normalize(str(slug)) in normalize(test)
        for test in related
    )

    if impl_files and related:
        build_state = "built_and_test_covered"
    elif impl_files and has_all_libraries:
        build_state = "built_contract_ready"
    elif impl_files:
        build_state = "built_needs_contract_or_tests"
    elif profile.get("systemProfile") or profile.get("generatedFromExistingCode"):
        build_state = "profiled_from_existing_system_needs_direct_impl_check"
    else:
        build_state = "profile_only_being_built"

    if related:
        test_state = "ready_for_test_run"
    elif impl_files and has_all_libraries:
        test_state = "ready_for_contract_testing"
    elif impl_files:
        test_state = "needs_test_file"
    else:
        test_state = "needs_implementation_before_testing"

    capabilities = profile.get("capabilities") or []
    if isinstance(capabilities, str):
        capabilities = [capabilities]

    risk = risk_hint(str(slug), str(name), profile.get("description", ""))
    buddy_money_approval = buddy_money_approval_for_bot(str(slug), approvals)
    coding_path = coding_path_for_bot(
        build_state=build_state,
        test_state=test_state,
        has_all_libraries=has_all_libraries,
        marker_hits=marker_hits,
        risk=risk,
    )
    production_readiness = production_readiness_for_bot(
        implementation_count=len(impl_files),
        marker_hits=marker_hits,
        has_all_libraries=has_all_libraries,
        test_state=test_state,
        risk=risk,
        buddy_money_approval=buddy_money_approval,
    )

    return {
        "slug": slug,
        "name": name,
        "division": profile.get("division") or "Unassigned",
        "category": profile.get("category") or "uncategorized",
        "tier": profile.get("tier"),
        "status": profile.get("status") or "unknown",
        "description": profile.get("description", ""),
        "capabilities": capabilities,
        "implementation_files": impl_files,
        "implementation_count": len(impl_files),
        "generated_runtime_file": runtime_file if has_generated_runtime else None,
        "has_generated_runtime": has_generated_runtime,
        "has_generated_smoke_test": has_generated_smoke_test,
        "executable_runtime_ready": has_generated_runtime and has_generated_smoke_test,
        "placeholder_markers": marker_hits,
        "tests": related,
        "test_count": len(related),
        "system_libraries": libraries,
        "has_all_system_libraries": has_all_libraries,
        "build_state": build_state,
        "test_state": test_state,
        "risk_hint": risk,
        "buddy_money_approval": buddy_money_approval,
        "coding_path": coding_path,
        "coding_path_status": coding_path["status"],
        "next_coding_step": coding_path["next_step"],
        "target_workflow": coding_path["target_workflow"],
        "production_readiness": production_readiness,
        "production_readiness_status": production_readiness["status"],
        "fully_coded": production_readiness["fully_coded"],
        "production_ready": production_readiness["production_ready"],
        "path": str(profile_path.parent.relative_to(ROOT)),
    }


def workflow_summary() -> list[dict]:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    workflows += sorted((ROOT / ".github" / "workflows").glob("*.yaml"))
    summary = []
    for path in workflows:
        text = path.read_text(encoding="utf-8", errors="ignore")
        summary.append(
            {
                "file": str(path.relative_to(ROOT)),
                "name": path.stem,
                "mentions_buddy": "buddy" in text.lower(),
                "manual": "workflow_dispatch" in text,
                "scheduled": "schedule:" in text,
                "push": "push:" in text,
            }
        )
    return summary


def build_inventory() -> dict:
    registry_path = ROOT / "config" / "master_bot_registry.json"
    registry = load_json(registry_path) if registry_path.exists() else {}
    approval_registry = load_approval_registry()
    approvals = approvals_by_slug(approval_registry)
    library_counts, library_by_slug = library_coverage()
    tests = test_files()
    profiles = sorted((ROOT / "bots").glob("*/bot_profile.json"))
    bots = [
        classify_bot(profile_path, load_json(profile_path), library_by_slug, tests, approvals)
        for profile_path in profiles
    ]

    capability_counter: Counter[str] = Counter()
    division_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()
    for bot in bots:
        division_counter[bot["division"]] += 1
        category_counter[bot["category"]] += 1
        capability_counter.update(str(capability) for capability in bot["capabilities"])

    build_counter = Counter(bot["build_state"] for bot in bots)
    test_counter = Counter(bot["test_state"] for bot in bots)
    coding_path_counter = Counter(bot["coding_path_status"] for bot in bots)
    production_counter = Counter(bot["production_readiness_status"] for bot in bots)
    buddy_bots = [
        bot
        for bot in bots
        if "buddy" in str(bot["slug"]).lower()
        or "buddy" in str(bot["name"]).lower()
        or "buddy" in str(bot["description"]).lower()
    ]
    placeholder_bots = [bot for bot in bots if bot["placeholder_markers"]]

    return {
        "schema": "dreamco.buddy_capability_inventory.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "branch": current_branch(),
        "summary": {
            "bot_profiles_scanned": len(bots),
            "registry_bot_count": registry.get("summary", {}).get("bot_count"),
            "registry_division_count": registry.get("summary", {}).get("division_count"),
            "workflows": len(workflow_summary()),
            "test_files": len(tests),
            "buddy_related_files": count_buddy_files(),
            "buddy_related_bots": len(buddy_bots),
            "system_library_counts": library_counts,
            "all_system_libraries_cover_profiled_bots": all(
                library_counts.get(name, 0) >= len(bots) for name in LIBRARY_NAMES
            ),
            "build_states": dict(build_counter),
            "test_states": dict(test_counter),
            "coding_path_states": dict(coding_path_counter),
            "bots_with_full_coding_path": sum(
                1 for bot in bots if bot["coding_path"]["has_full_coding_path"]
            ),
            "all_bots_have_full_coding_path": all(
                bot["coding_path"]["has_full_coding_path"] for bot in bots
            ),
            "production_readiness_states": dict(production_counter),
            "fully_coded_bots": sum(1 for bot in bots if bot["fully_coded"]),
            "production_ready_bots": sum(1 for bot in bots if bot["production_ready"]),
            "all_bots_fully_coded": all(bot["fully_coded"] for bot in bots),
            "all_bots_production_ready": all(bot["production_ready"] for bot in bots),
            "executable_runtime_ready_bots": sum(
                1 for bot in bots if bot["executable_runtime_ready"]
            ),
            "all_bots_have_executable_runtime": all(
                bot["executable_runtime_ready"] for bot in bots
            ),
            "placeholder_marker_bots": len(placeholder_bots),
            "buddy_money_approval_required_bots": sum(
                1
                for bot in bots
                if bot["risk_hint"] == "high" and not bot["buddy_money_approval"]["approved"]
            ),
            "buddy_money_approved_high_risk_bots": sum(
                1
                for bot in bots
                if bot["risk_hint"] == "high" and bot["buddy_money_approval"]["approved"]
            ),
        },
        "approval_policy": {
            "registry_file": str(APPROVAL_REGISTRY_FILE.relative_to(ROOT)),
            "required_buddy_money_request": REQUIRED_BUDDY_MONEY_REQUEST,
            "rule": (
                "High-risk bots require a user request to Buddy for money help, "
                "risk acknowledgement, approved live actions, and checklist evidence."
            ),
        },
        "top_divisions": division_counter.most_common(),
        "top_categories": category_counter.most_common(),
        "top_capabilities": capability_counter.most_common(),
        "buddy_bots": sorted(buddy_bots, key=lambda bot: bot["slug"]),
        "attention": {
            "needs_implementation": [
                bot for bot in bots if bot["test_state"] == "needs_implementation_before_testing"
            ],
            "needs_existing_system_mapping": [
                bot
                for bot in bots
                if bot["coding_path_status"] == "needs_existing_system_mapping"
            ],
            "needs_direct_test_coverage": [
                bot for bot in bots if bot["coding_path_status"] == "needs_direct_test_coverage"
            ],
            "needs_placeholder_review": [
                bot for bot in bots if bot["coding_path_status"] == "needs_placeholder_review"
            ],
            "production_blockers": [
                bot for bot in bots if not bot["production_ready"]
            ],
            "placeholder_marker_bots": placeholder_bots,
        },
        "workflows": workflow_summary(),
        "bots": bots,
    }


def count_buddy_files() -> int:
    count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {"node_modules", "dist", ".git"} for part in path.parts):
            continue
        if "buddy" in str(path.relative_to(ROOT)).lower():
            count += 1
    return count


def write_markdown(inventory: dict, path: Path) -> None:
    summary = inventory["summary"]
    build_states = summary["build_states"]
    test_states = summary["test_states"]
    coding_path_states = summary["coding_path_states"]
    production_readiness_states = summary["production_readiness_states"]
    lines = [
        "# Buddy Capability Inventory",
        "",
        f"Generated: {inventory['generated_at']}",
        f"Branch scanned: `{inventory.get('branch')}`",
        "",
        "## Executive Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")

    lines += [
        "",
        "## Direct Buddy Systems Found",
        "",
    ]
    for bot in inventory["buddy_bots"]:
        lines.append(
            f"- `{bot['slug']}` — {bot['name']}: "
            f"{bot['build_state']}; {bot['test_state']}"
        )

    lines += [
        "",
        "## Built / Being Built / Ready For Testing",
        "",
        "| Group | Count | Meaning |",
        "| --- | ---: | --- |",
        (
            f"| Built and test-covered | {build_states.get('built_and_test_covered', 0)} "
            "| Implementation files plus matching tests were found. |"
        ),
        (
            f"| Built and contract-ready | {build_states.get('built_contract_ready', 0)} "
            "| Implementation files plus generated contracts were found. |"
        ),
        (
            f"| Profiled from existing system | "
            f"{build_states.get('profiled_from_existing_system_needs_direct_impl_check', 0)} "
            "| Existing-system profiles that need direct mapping review. |"
        ),
        (
            f"| Profile-only / being built | {build_states.get('profile_only_being_built', 0)} "
            "| Profile exists but direct implementation was not found. |"
        ),
        "",
        "## Test Readiness",
        "",
        "| Test State | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(test_states.items()):
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "## Full Coding Path Coverage",
        "",
        f"- Bots with a tracked coding path: {summary['bots_with_full_coding_path']}",
        f"- All bots have a tracked coding path: {summary['all_bots_have_full_coding_path']}",
        "",
        "| Coding Path State | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(coding_path_states.items()):
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "## Production Readiness",
        "",
        f"- Fully coded bots: {summary['fully_coded_bots']}",
        f"- Production-ready bots: {summary['production_ready_bots']}",
        f"- All bots fully coded: {summary['all_bots_fully_coded']}",
        f"- All bots production ready: {summary['all_bots_production_ready']}",
        "",
        "| Production Readiness State | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(production_readiness_states.items()):
        lines.append(f"| {key} | {value} |")

    lines += ["", "## Needs Implementation", ""]
    needs = inventory["attention"]["needs_implementation"]
    for bot in needs:
        lines.append(f"- `{bot['slug']}` — {bot['name']} ({bot['division']})")
    if not needs:
        lines.append("- None found.")

    lines += ["", "## Generated Files", "", "- Full JSON inventory: `reports/buddy_capability_inventory.json`", "- CSV: `reports/buddy_bot_readiness.csv`"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(inventory: dict, path: Path) -> None:
    fields = [
        "slug",
        "name",
        "division",
        "category",
        "status",
        "build_state",
        "test_state",
        "implementation_count",
        "test_count",
        "has_all_system_libraries",
        "risk_hint",
        "coding_path_status",
        "next_coding_step",
        "target_workflow",
        "production_readiness_status",
        "fully_coded",
        "production_ready",
        "path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for bot in inventory["bots"]:
            writer.writerow({field: bot.get(field) for field in fields})


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    inventory = build_inventory()
    (REPORT_DIR / "buddy_capability_inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(inventory, REPORT_DIR / "BUDDY_CAPABILITY_INVENTORY.md")
    write_csv(inventory, REPORT_DIR / "buddy_bot_readiness.csv")
    print(json.dumps(inventory["summary"], indent=2))
    if "--strict-production-ready" in sys.argv and not inventory["summary"]["all_bots_production_ready"]:
        print(
            "Production readiness gate failed: not all bots are production-ready.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
