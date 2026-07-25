#!/usr/bin/env python3
"""Generate a deterministic repository-wide test and integration registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "repository-test-suites.json"
GENERATED = ROOT / "config" / "generated" / "repository_test_registry.json"
PUBLIC = ROOT / "website" / "data" / "repository-test-registry.json"

SKIPPED_ROOTS = {
    ".git",
    ".wrangler",
    "__pycache__",
    "dist",
    "logs",
    "node_modules",
    "reports",
}
SKIPPED_FILES = {
    GENERATED.relative_to(ROOT).as_posix(),
    PUBLIC.relative_to(ROOT).as_posix(),
    "website/data/repository-system-map.json",
}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
ROUTE_PATTERN = re.compile(
    r"""\bapp\.(get|post|put|patch|delete)\(\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
SHARED_PATH_PATTERN = re.compile(r"""\bpath:\s*["'](/api/[^"']+)["']""")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected an object in {path.relative_to(ROOT)}")
    return payload


def normalized_files() -> list[Path]:
    rows: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in SKIPPED_ROOTS for part in relative.parts):
            continue
        if relative.as_posix() in SKIPPED_FILES:
            continue
        rows.append(path)
    return sorted(rows, key=lambda item: item.relative_to(ROOT).as_posix().lower())


def path_kind(relative: str) -> str:
    path = Path(relative)
    name = path.name.lower()
    parts = path.parts
    if relative.startswith(".github/workflows/"):
        return "workflow"
    if relative.startswith("attached_assets/"):
        return "reference_asset"
    if relative.startswith(("App_bots/", "bots/", "original-bots/")):
        return "bot_source"
    if relative.startswith("tests/") or ".test." in name or ".spec." in name or name.startswith("test_"):
        return "test"
    if relative.startswith("website/") and path.suffix == ".html":
        return "web_page"
    if relative.startswith("website/"):
        return "web_asset"
    if relative.startswith("tools/"):
        return "generator_or_tool"
    if relative.startswith("dreamco_platform/"):
        return "platform_module"
    if relative.startswith("server/provider_integrations/") or relative.startswith("client/provider_integrations/"):
        return "provider_adapter"
    if relative.startswith("server/") and ("policy" in name or name in {"fleet-runtime.ts", "outbound-adapters.ts"}):
        return "policy"
    if relative.startswith("server/"):
        return "server_source"
    if relative.startswith("client/src/"):
        return "client_source"
    if relative.startswith("shared/"):
        return "shared_contract"
    if relative.startswith("config/"):
        return "configuration"
    if relative.startswith("docs/") or path.suffix == ".md":
        return "documentation"
    return "project_file"


def file_suite(relative: str) -> str:
    value = relative.lower()
    rules = [
        ("data-rights", ("privacy", "data-control", "data-rights", "memory")),
        ("open-source-lab", ("open-model", "opensource", "repository-test")),
        ("model-routing", ("model", "ai-model")),
        ("payments", ("stripe", "payment", "subscription", "webhookhandler")),
        ("github", ("github", ".github/workflows")),
        ("creative-media", ("creative", "studio", "audio", "voice", "image", "music")),
        ("games-education", ("game", "course", "education", "simulation")),
        ("connections", ("connection", "device-action", "token-transfer", "approval-notification", "outbound-adapter")),
        ("calculators", ("calculator", "formula", "deal-calculation")),
        ("distribution", ("distribution", "install", "launch")),
        ("social", ("social",)),
        ("leads", ("lead", "sales")),
        ("government", ("government", "grant", "procurement")),
        ("crypto", ("crypto", "wallet", "mining", "dreamcoin")),
        ("observability", ("metric", "debug", "error", "cost", "alert")),
        ("task-automation", ("automation", "autonomy", "task")),
        ("code-lab", ("code", "bot-builder", "codelab")),
        ("bot-fleet", ("bot", "fleet", "division", "master_bot_registry")),
        ("public-site", ("website", "public-site", "sitemap", "service-worker")),
    ]
    for suite_id, markers in rules:
        if any(marker in value for marker in markers):
            return suite_id
    if relative.startswith("dreamco_platform/"):
        return "python-platform"
    if relative.startswith(("client/", "server/", "shared/")):
        return "client-build"
    return "repository-contracts"


def route_suite(path: str) -> str:
    value = path.lower()
    rules = [
        ("data-rights", ("/data", "/memory")),
        ("harness", ("/harness", "/governance")),
        ("payments", ("/stripe", "/payments", "/financial", "/deals")),
        ("github", ("/github",)),
        ("creative-media", ("/voice", "/generate-image", "/analyze-image", "/batch")),
        ("open-source-lab", ("/open-source", "/open-model")),
        ("model-routing", ("/model",)),
        ("connections", ("/connection", "/device", "/signup", "/token-transfer", "/approval-notification")),
        ("calculators", ("/calculator", "/formula")),
        ("distribution", ("/distribution", "/deploy-config")),
        ("social", ("/social",)),
        ("leads", ("/lead",)),
        ("government", ("/government",)),
        ("crypto", ("/crypto",)),
        ("observability", ("/metric", "/debug", "/error", "/cost", "/alert", "/interaction")),
        ("task-automation", ("/task", "/kill-switch", "/snapshot")),
        ("code-lab", ("/code", "/bot-builder", "/vibe-code", "/architect", "/refactor", "/security-scan")),
        ("bot-fleet", ("/fleet", "/bots", "/empire", "/council")),
        ("buddy-routing", ("/buddy", "/conversations")),
    ]
    for suite_id, markers in rules:
        if any(marker in value for marker in markers):
            return suite_id
    return "repository-contracts"


def route_classification(method: str, path: str) -> str:
    value = path.lower()
    if method == "CONTRACT":
        return "shared_contract"
    if method == "DELETE" or any(
        marker in value
        for marker in ("/push", "/sync", "/trigger", "/checkout", "/portal", "/install", "/uninstall", "/kill-switch")
    ):
        return "external_or_destructive_gate"
    if any(marker in value for marker in ("/plan", "/catalog", "/status", "/health", "/features", "/resources", "/classify")):
        return "plan_or_readiness"
    if method == "GET":
        return "read_only"
    return "state_change"


def route_runtime(classification: str, suite_id: str) -> str:
    if classification == "external_or_destructive_gate":
        return "credentials_and_exact_approval_required"
    if suite_id in {"payments", "github"}:
        return "credentials_required"
    if suite_id in {"creative-media", "connections", "distribution", "social", "leads", "government", "model-routing"}:
        return "adapter_optional"
    return "local_contract"


def scan_routes(files: list[Path]) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix not in {".ts", ".tsx"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in ROUTE_PATTERN.finditer(text):
            method = match.group(1).upper()
            route_path = match.group(2)
            line = text.count("\n", 0, match.start()) + 1
            classification = route_classification(method, route_path)
            suite_id = route_suite(route_path)
            routes.append({
                "id": hashlib.sha256(f"{method}:{route_path}:{relative}:{line}".encode()).hexdigest()[:20],
                "method": method,
                "path": route_path,
                "source": relative,
                "line": line,
                "classification": classification,
                "runtime": route_runtime(classification, suite_id),
                "suite_id": suite_id,
            })
        if relative == "shared/routes.ts":
            for match in SHARED_PATH_PATTERN.finditer(text):
                route_path = match.group(1)
                line = text.count("\n", 0, match.start()) + 1
                suite_id = route_suite(route_path)
                routes.append({
                    "id": hashlib.sha256(f"CONTRACT:{route_path}:{relative}:{line}".encode()).hexdigest()[:20],
                    "method": "CONTRACT",
                    "path": route_path,
                    "source": relative,
                    "line": line,
                    "classification": "shared_contract",
                    "runtime": route_runtime("shared_contract", suite_id),
                    "suite_id": suite_id,
                })
    return sorted(routes, key=lambda row: (row["path"], row["method"], row["source"], row["line"]))


def scan() -> dict[str, Any]:
    source = read_json(SOURCE)
    package = read_json(ROOT / "package.json")
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        raise TypeError("package.json scripts must be an object")

    files = normalized_files()
    file_rows = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        file_rows.append({
            "path": relative,
            "kind": path_kind(relative),
            "suite_id": file_suite(relative),
            "bytes": path.stat().st_size,
        })

    suite_rows = []
    suite_ids: set[str] = set()
    for raw in source.get("suites", []):
        suite = dict(raw)
        suite_id = str(suite.get("id", ""))
        if not re.fullmatch(r"[a-z][a-z0-9-]{2,63}", suite_id):
            raise ValueError(f"Invalid suite id: {suite_id!r}")
        if suite_id in suite_ids:
            raise ValueError(f"Duplicate suite id: {suite_id}")
        suite_ids.add(suite_id)
        missing_scripts = [key for key in suite.get("scripts", []) if key not in scripts]
        evidence_paths = [*suite.get("sources", []), *suite.get("tests", [])]
        missing_evidence = [item for item in evidence_paths if not (ROOT / item).exists()]
        if missing_scripts or missing_evidence:
            status = "blocked_missing_evidence"
        elif suite.get("level") == "credentials_required":
            status = "credentials_required"
        elif suite.get("level") == "adapter_optional":
            status = "local_contract_ready_live_adapter_required"
        elif suite.get("level") == "repository_sandbox":
            status = "repository_sandbox_ready"
        else:
            status = "local_contract_ready"
        suite_rows.append({
            **suite,
            "status": status,
            "missing_scripts": missing_scripts,
            "missing_evidence": missing_evidence,
            "tests_execute_from_browser": False,
        })

    routes = scan_routes(files)
    unmapped_routes = [route for route in routes if route["suite_id"] not in suite_ids]
    if unmapped_routes:
        raise ValueError(f"Routes map to unknown suites: {unmapped_routes[:3]}")

    duplicate_counter = Counter((route["method"], route["path"]) for route in routes if route["method"] != "CONTRACT")
    duplicates = [
        {"method": method, "path": path, "registrations": count}
        for (method, path), count in sorted(duplicate_counter.items())
        if count > 1
    ]
    kinds = Counter(row["kind"] for row in file_rows)
    route_classes = Counter(route["classification"] for route in routes)
    suite_statuses = Counter(suite["status"] for suite in suite_rows)
    extension_counts = Counter(Path(row["path"]).suffix.lower() or "[none]" for row in file_rows)
    source_hash = hashlib.sha256(
        (
            SOURCE.read_text(encoding="utf-8")
            + "\n"
            + "\n".join(f"{row['path']}:{row['bytes']}" for row in file_rows)
        ).encode("utf-8")
    ).hexdigest()

    return {
        "schema": "dreamco.repository_test_registry.v1",
        "scan_id": source_hash[:24],
        "summary": {
            "files_scanned": len(file_rows),
            "api_route_registrations": len(routes),
            "literal_api_routes": sum(route["method"] != "CONTRACT" for route in routes),
            "shared_route_contracts": sum(route["method"] == "CONTRACT" for route in routes),
            "web_pages": kinds["web_page"],
            "test_files": kinds["test"],
            "bot_sources": kinds["bot_source"],
            "platform_modules": kinds["platform_module"],
            "provider_adapters": kinds["provider_adapter"],
            "workflows": kinds["workflow"],
            "test_suites": len(suite_rows),
            "locally_testable_suites": sum(
                suite["status"] in {"local_contract_ready", "repository_sandbox_ready", "local_contract_ready_live_adapter_required"}
                for suite in suite_rows
            ),
            "credential_required_suites": suite_statuses["credentials_required"],
            "blocked_suites": suite_statuses["blocked_missing_evidence"],
            "duplicate_route_keys": len(duplicates),
        },
        "safety_contract": {
            "browser_executes_repository_commands": False,
            "network_default": source.get("defaults", {}).get("network", "off"),
            "external_writes": source.get("defaults", {}).get("external_writes", "forbidden"),
            "test_data": source.get("defaults", {}).get("data", "synthetic_or_owner_authorized"),
            "adapter_tests_require_credentials": True,
            "external_actions_require_exact_approval": True,
            "results_must_distinguish_contract_from_live_e2e": True,
        },
        "file_kinds": dict(sorted(kinds.items())),
        "extensions": dict(sorted(extension_counts.items())),
        "route_classifications": dict(sorted(route_classes.items())),
        "duplicate_route_registrations": duplicates,
        "suites": suite_rows,
        "routes": routes,
        "files": file_rows,
    }


def serialized(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated registries without rewriting them.")
    args = parser.parse_args()
    payload = scan()
    expected = serialized(payload)

    if args.check:
        for path in (GENERATED, PUBLIC):
            if not path.exists():
                raise SystemExit(f"Missing generated registry: {path.relative_to(ROOT)}")
            if path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated registry is stale: {path.relative_to(ROOT)}")
    else:
        for path in (GENERATED, PUBLIC):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "scan_id": payload["scan_id"],
        **payload["summary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
