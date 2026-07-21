#!/usr/bin/env python3
"""Generate DreamCo professional organization and OS readiness report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "dreamco_professional_os.json"
REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
COMMERCE_FILE = ROOT / "reports" / "buddy_commerce_publishing_os.json"
APP_CATEGORY_FILE = ROOT / "reports" / "app_category_catalog.json"
CAPABILITY_FILE = ROOT / "reports" / "bot_capabilities_library.json"
STORAGE_FILE = ROOT / "reports" / "storage_guard_report.json"
OUTPUT_JSON = ROOT / "reports" / "dreamco_professional_os.json"
OUTPUT_MD = ROOT / "reports" / "DREAMCO_PROFESSIONAL_OS.md"

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    ".pytest_cache",
    "__pycache__",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def scan_repository() -> dict[str, Any]:
    top_level = Counter()
    suffixes = Counter()
    file_count = 0
    source_count = 0
    test_count = 0
    report_count = 0
    config_count = 0
    dashboard_count = 0
    bot_dir_count = 0
    duplicate_name_groups: dict[str, list[str]] = {}

    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_dir():
            if len(relative.parts) == 2 and relative.parts[0] == "bots":
                bot_dir_count += 1
            name_key = path.name.lower().replace("_", "-")
            if name_key in {"dreamco", "dashboard", "frontend", "backend", "bots", "business-launch-pad"}:
                duplicate_name_groups.setdefault(name_key, []).append(str(relative))
            continue
        file_count += 1
        top_level[relative.parts[0]] += 1
        suffixes[path.suffix.lower() or "[no_ext]"] += 1
        if path.suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".java"}:
            source_count += 1
        if "test" in path.name.lower() or "__tests__" in relative.parts:
            test_count += 1
        if relative.parts[0] == "reports":
            report_count += 1
        if relative.parts[0] == "config":
            config_count += 1
        if "dashboard" in str(relative).lower() or "actions" in path.name.lower():
            dashboard_count += 1

    return {
        "file_count": file_count,
        "source_files": source_count,
        "test_files": test_count,
        "report_files": report_count,
        "config_files": config_count,
        "dashboard_files": dashboard_count,
        "bot_directories": bot_dir_count,
        "top_level_file_counts": [{"path": key, "files": value} for key, value in top_level.most_common(25)],
        "top_extensions": [{"extension": key, "files": value} for key, value in suffixes.most_common(15)],
        "duplicate_name_groups": [
            {"name": key, "paths": sorted(values)}
            for key, values in sorted(duplicate_name_groups.items())
            if len(values) > 1
        ],
    }


def build_report() -> dict[str, Any]:
    config = read_json(CONFIG_FILE, {})
    registry = read_json(REGISTRY_FILE, {})
    commerce = read_json(COMMERCE_FILE, {})
    app_categories = read_json(APP_CATEGORY_FILE, {})
    capabilities = read_json(CAPABILITY_FILE, {})
    storage = read_json(STORAGE_FILE, {})
    repo = scan_repository()
    bot_count = len(registry.get("bots", []))

    organization_lanes = [
        {
            "id": "source_of_truth",
            "label": "Source Of Truth",
            "goal": "Keep configs and generated reports linked so dashboards show evidence instead of guesses.",
            "proof": ["config/", "reports/", "config/generated/"],
            "next_safe_action": "Add or refresh generators before editing report JSON by hand.",
        },
        {
            "id": "bot_fleet",
            "label": "Bot Fleet",
            "goal": "Make every bot discoverable through the registry, capabilities library, test packet, and Buddy route.",
            "proof": [f"{bot_count} registry bots", f"{capabilities.get('summary', {}).get('total_capability_slots', 0)} capability slots"],
            "next_safe_action": "Keep large generated bot libraries sharded by division.",
        },
        {
            "id": "client_surface",
            "label": "Client Surface",
            "goal": "Make the Actions page the professional command center for demos, testing, approvals, and delivery.",
            "proof": config.get("actions_page_modules", []),
            "next_safe_action": "Keep each section backed by a generated report or API endpoint.",
        },
        {
            "id": "commerce_domains",
            "label": "Commerce And Domains",
            "goal": "Sell domain research, domain packages, custom DreamCo domains, app publishing packets, and client downloads.",
            "proof": config.get("domain_marketplace", {}).get("domain_types", []),
            "next_safe_action": "Buy, sell, transfer, DNS, and payment actions remain owner-approved.",
        },
        {
            "id": "human_bot_workspace",
            "label": "Human And Bot Workspace",
            "goal": "Make Buddy OS and browser workflows safe, fast, evidence-backed, and reversible.",
            "proof": config.get("human_bot_os_browser", {}).get("workspace_layers", []),
            "next_safe_action": "Route every app/browser/device action through task, approval, evidence, and rollback records.",
        },
    ]

    readiness_checks = [
        {"id": "registry_loaded", "label": "Registry Loaded", "status": "pass" if bot_count else "fail", "value": bot_count},
        {"id": "app_categories", "label": "App Categories", "status": "pass" if app_categories.get("summary", {}).get("app_categories", 0) >= 40 else "warn", "value": app_categories.get("summary", {}).get("app_categories", 0)},
        {"id": "domain_marketplace", "label": "Domain Marketplace", "status": "pass", "value": len(config.get("domain_marketplace", {}).get("domain_types", []))},
        {"id": "commerce_lanes", "label": "Commerce Lanes", "status": "pass" if commerce.get("summary", {}).get("commerce_lanes", 0) else "warn", "value": commerce.get("summary", {}).get("commerce_lanes", 0)},
        {"id": "storage_ready", "label": "Storage Ready", "status": "pass" if storage.get("summary", {}).get("storage_ready") else "warn", "value": storage.get("summary", {}).get("storage_ready", False)},
        {"id": "tests_present", "label": "Tests Present", "status": "pass" if repo["test_files"] else "warn", "value": repo["test_files"]},
    ]

    return {
        "schema": "dreamco.professional_os_report.v1",
        "generated_at": utc_now(),
        "source_config": rel(CONFIG_FILE),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": {
            "professional_readiness_score": sum(1 for check in readiness_checks if check["status"] == "pass") * 100 // len(readiness_checks),
            "file_count": repo["file_count"],
            "source_files": repo["source_files"],
            "test_files": repo["test_files"],
            "bot_count": bot_count,
            "bot_directories": repo["bot_directories"],
            "actions_page_modules": len(config.get("actions_page_modules", [])),
            "domain_types": len(config.get("domain_marketplace", {}).get("domain_types", [])),
            "workspace_layers": len(config.get("human_bot_os_browser", {}).get("workspace_layers", [])),
            "readiness_checks": len(readiness_checks),
            "passing_readiness_checks": sum(1 for check in readiness_checks if check["status"] == "pass"),
            "duplicate_name_groups": len(repo["duplicate_name_groups"]),
        },
        "repository_scan": repo,
        "organization_lanes": organization_lanes,
        "actions_page_modules": config.get("actions_page_modules", []),
        "domain_marketplace": config.get("domain_marketplace", {}),
        "human_bot_os_browser": config.get("human_bot_os_browser", {}),
        "repository_standards": config.get("repository_standards", []),
        "professional_readiness_gates": config.get("professional_readiness_gates", []),
        "readiness_checks": readiness_checks,
        "next_actions": [
            "Keep this report as the evidence map before moving folders.",
            "Consolidate duplicate dashboard and DreamCo roots only with import-impact checks.",
            "Make Actions page modules load from generated reports instead of hardcoded claims.",
            "Treat domain purchase, DNS, app-store, social, payment, and browser account actions as approval-required.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# DreamCo Professional OS",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Professional readiness score: {summary['professional_readiness_score']}",
        f"- Files scanned: {summary['file_count']}",
        f"- Source files: {summary['source_files']}",
        f"- Test files: {summary['test_files']}",
        f"- Registry bots: {summary['bot_count']}",
        f"- Bot directories: {summary['bot_directories']}",
        f"- Actions page modules: {summary['actions_page_modules']}",
        f"- Domain product types: {summary['domain_types']}",
        f"- Human/bot workspace layers: {summary['workspace_layers']}",
        "",
        "## Organization Lanes",
        "",
    ]
    for lane in report["organization_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["goal"])
        lines.append("")
        lines.append(f"- Next safe action: {lane['next_safe_action']}")
        lines.append("")
    lines.extend(["## Domain Marketplace", ""])
    domain_marketplace = report["domain_marketplace"]
    for domain_type in domain_marketplace.get("domain_types", []):
        lines.append(f"- {domain_type}")
    lines.extend(["", "## Readiness Checks", ""])
    for check in report["readiness_checks"]:
        lines.append(f"- {check['label']}: {check['status']} ({check['value']})")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("professional OS report missing; run generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        if json.dumps(existing, indent=2, sort_keys=True) + "\n" != rendered:
            raise SystemExit("professional OS report stale; run generator")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(
        "professional_os_ready score={score} files={files} bots={bots} domain_types={domains}".format(
            score=summary["professional_readiness_score"],
            files=summary["file_count"],
            bots=summary["bot_count"],
            domains=summary["domain_types"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
