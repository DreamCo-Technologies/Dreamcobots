#!/usr/bin/env python3
"""Generate Buddy capability and bot readiness inventory reports."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
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
    r"NotImplementedError|pass\s*(#.*)?$|TODO|placeholder|stub|coming soon",
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
    files = list((ROOT / "tests").glob("test_*.py"))
    control_tower = ROOT / "dreamco-control-tower"
    files += list(control_tower.glob("**/*.test.js"))
    files += list(control_tower.glob("**/*.test.jsx"))
    return sorted(files)


def related_tests(slug: str, name: str, files: list[Path]) -> list[str]:
    normalized_slug = normalize(slug)
    normalized_name = normalize(name)
    matches: list[str] = []
    for path in files:
        normalized_test = normalize(path.stem.replace("test-", "").replace("test_", ""))
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
            if PLACEHOLDER_RE.search(text):
                marker_hits.append(relative)
    return files, marker_hits


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


def classify_bot(
    profile_path: Path,
    profile: dict,
    library_by_slug: dict[str, set[str]],
    tests: list[Path],
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
    coding_path = coding_path_for_bot(
        build_state=build_state,
        test_state=test_state,
        has_all_libraries=has_all_libraries,
        marker_hits=marker_hits,
        risk=risk,
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
        "placeholder_markers": marker_hits,
        "tests": related,
        "test_count": len(related),
        "system_libraries": libraries,
        "has_all_system_libraries": has_all_libraries,
        "build_state": build_state,
        "test_state": test_state,
        "risk_hint": risk,
        "coding_path": coding_path,
        "coding_path_status": coding_path["status"],
        "next_coding_step": coding_path["next_step"],
        "target_workflow": coding_path["target_workflow"],
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
    library_counts, library_by_slug = library_coverage()
    tests = test_files()
    profiles = sorted((ROOT / "bots").glob("*/bot_profile.json"))
    bots = [
        classify_bot(profile_path, load_json(profile_path), library_by_slug, tests)
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
            "placeholder_marker_bots": len(placeholder_bots),
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


if __name__ == "__main__":
    main()
