#!/usr/bin/env python3
"""Generate the canonical, public-safe DreamCo command-center data bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
COMMAND_DATA = ROOT / "command-center" / "data"
WEBSITE_DATA = ROOT / "website" / "data" / "command-center"
REGISTRY = ROOT / "config" / "master_bot_registry.json"
BENCHMARK_INDEX = ROOT / "config" / "buddy-benchmark-index.json"

EVIDENCE_TAXONOMY = [
    "catalogued",
    "implemented",
    "sandbox_verified",
    "benchmark_verified",
    "regression_verified",
    "production_verified",
]
GENERATED_NAMES = [
    "repository-inventory.json",
    "bots.json",
    "divisions.json",
    "capabilities.json",
    "benchmarks.json",
    "workflows.json",
    "system-health.json",
    "release-readiness.json",
    "index.json",
]
IGNORED_PARTS = {".git", ".pytest_cache", "node_modules", "dist", ".cache", "__pycache__"}
SECRET_NAME = re.compile(r"(^|/)(\.env($|\.)|.*\.(pem|p12|pfx|key)$|id_(rsa|ed25519)$)", re.I)


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a JSON object: {path.relative_to(ROOT)}")
    return payload


def source_digest(paths: Iterable[Path]) -> str:
    checksum = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        checksum.update(path.relative_to(ROOT).as_posix().encode())
        checksum.update(b"\0")
        checksum.update(path.read_bytes())
        checksum.update(b"\0")
    return checksum.hexdigest()


def repository_files() -> list[Path]:
    """Return reproducible evidence files, excluding machine-local ignored data."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        candidates = [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]
    except (FileNotFoundError, subprocess.CalledProcessError, UnicodeDecodeError):
        # Source archives may intentionally omit Git metadata.
        candidates = list(ROOT.rglob("*"))
    return sorted(
        (
            path
            for path in candidates
            if path.is_file()
            and not any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)
            and COMMAND_DATA not in path.parents
            and WEBSITE_DATA not in path.parents
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def artifact(schema: str, sources: list[Path], **values: Any) -> dict[str, Any]:
    return {
        "schema": schema,
        "evidence_taxonomy": EVIDENCE_TAXONOMY,
        "source_sha256": source_digest(sources),
        **values,
    }


def normalized_status(value: str, evidence_refs: list[str]) -> str:
    token = value.lower().strip()
    if token in EVIDENCE_TAXONOMY:
        status = token
    elif "production" in token and ("verified" in token or "ready" in token):
        status = "implemented"
    elif any(word in token for word in ("runtime", "ready", "active", "implemented", "generated")):
        status = "implemented"
    else:
        status = "catalogued"
    if status != "catalogued" and not evidence_refs:
        return "catalogued"
    return status


def build_repository_inventory(files: list[Path]) -> dict[str, Any]:
    extensions = Counter((path.suffix.lower() or "[none]") for path in files)
    top_level = Counter(path.relative_to(ROOT).parts[0] for path in files)
    secret_named = sorted(
        path.relative_to(ROOT).as_posix()
        for path in files
        if SECRET_NAME.search(path.relative_to(ROOT).as_posix()) and path.name != ".env.example"
    )
    sources = [ROOT / "AGENTS.md", ROOT / "package.json"]
    return artifact(
        "dreamco.command_center.repository_inventory.v1",
        sources,
        summary={
            "tracked_and_untracked_files_scanned": len(files),
            "top_level_areas": len(top_level),
            "secret_named_files": len(secret_named),
        },
        files_by_extension=dict(sorted(extensions.items())),
        files_by_top_level_area=dict(sorted(top_level.items())),
        security_observations={"secret_named_files": secret_named},
        status="implemented",
        evidence_refs=["tools/generate_command_center_data.py", "tests/test_command_center_data.py"],
    )


def build_fleet(registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    bots: list[dict[str, Any]] = []
    capabilities: dict[str, dict[str, Any]] = {}
    division_bots: dict[str, list[str]] = defaultdict(list)
    for bot in registry.get("bots", []):
        identity = bot.get("identity", {})
        slug = identity.get("slug", "")
        division = identity.get("division", "unassigned")
        evidence_refs = sorted({str(ref) for ref in bot.get("evidence", {}).values() if isinstance(ref, str)})
        status = normalized_status(str(identity.get("catalog_status", "catalogued")), evidence_refs)
        bot_caps = []
        for capability in bot.get("capabilities", []):
            name = str(capability.get("name", "")).strip()
            if not name:
                continue
            cap_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            bot_caps.append(cap_id)
            record = capabilities.setdefault(
                cap_id,
                {"id": cap_id, "name": name, "bot_ids": [], "source_refs": [], "evidence_refs": [], "status": "catalogued"},
            )
            record["bot_ids"].append(slug)
            if capability.get("source"):
                record["source_refs"].append(str(capability["source"]))
            if capability.get("test_evidence"):
                record["evidence_refs"].append(str(capability["test_evidence"]))
            record["status"] = normalized_status(str(capability.get("evidence_level", "catalogued")), record["evidence_refs"])
        bots.append(
            {
                "id": slug,
                "name": identity.get("display_name", slug),
                "division_id": division.lower().replace(" ", "-"),
                "category": identity.get("category", "uncategorized"),
                "status": status,
                "capability_ids": sorted(set(bot_caps)),
                "source_refs": sorted({cap.get("source", "") for cap in bot.get("capabilities", []) if cap.get("source")}),
                "evidence_refs": evidence_refs,
            }
        )
        division_bots[division].append(slug)

    original_sources = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "original-bots").rglob("*") if path.is_file())
    for record in capabilities.values():
        record["bot_ids"] = sorted(set(record["bot_ids"]))
        record["source_refs"] = sorted(set(record["source_refs"]))
        record["evidence_refs"] = sorted(set(record["evidence_refs"]))
    bots.sort(key=lambda item: item["id"])
    capability_rows = sorted(capabilities.values(), key=lambda item: item["id"])
    divisions = [
        {
            "id": str(row.get("name", "")).lower().replace(" ", "-"),
            "name": row.get("name"),
            "bot_ids": sorted(division_bots.get(str(row.get("name", "")), [])),
            "source_refs": [row.get("source")],
            "status": "implemented",
            "evidence_refs": ["config/master_bot_registry.json"],
        }
        for row in registry.get("divisions", [])
    ]
    sources = [REGISTRY, *[ROOT / ref for ref in original_sources]]
    bot_payload = artifact(
        "dreamco.command_center.bots.v1",
        sources,
        summary={"registered_bots": len(bots), "preserved_original_bot_files": len(original_sources)},
        original_bot_sources=original_sources,
        items=bots,
    )
    division_payload = artifact(
        "dreamco.command_center.divisions.v1",
        [REGISTRY],
        summary={"registered_divisions": len(divisions)},
        items=divisions,
    )
    capability_payload = artifact(
        "dreamco.command_center.capabilities.v1",
        [REGISTRY],
        summary={"unique_capabilities": len(capability_rows), "bot_capability_edges": sum(len(row["capability_ids"]) for row in bots)},
        items=capability_rows,
    )
    return bot_payload, division_payload, capability_payload


def build_benchmarks() -> dict[str, Any]:
    source = read_json(BENCHMARK_INDEX)
    items = []
    for row in source.get("programs", []):
        evidence_refs = [value for key, value in row.items() if key in {"generator", "public_page", "public_data"} and isinstance(value, str)]
        items.append({**row, "status": normalized_status(str(row.get("status", "catalogued")), evidence_refs), "evidence_refs": sorted(evidence_refs)})
    return artifact(
        "dreamco.command_center.benchmarks.v1",
        [BENCHMARK_INDEX],
        summary={"registered_benchmark_programs": len(items), "executed_in_this_generation": 0},
        truth="This catalog does not claim a benchmark ran; execution evidence must be recorded separately.",
        items=sorted(items, key=lambda item: str(item.get("id", ""))),
    )


def build_workflows() -> dict[str, Any]:
    paths = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
    items = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*(.+)$", text, re.M)
        items.append(
            {
                "id": path.stem,
                "name": name_match.group(1).strip(' "\'') if name_match else path.stem,
                "source_refs": [path.relative_to(ROOT).as_posix()],
                "status": "implemented",
                "evidence_refs": [path.relative_to(ROOT).as_posix()],
                "execution_status": "not_checked_by_offline_generator",
            }
        )
    return artifact(
        "dreamco.command_center.workflows.v1",
        paths,
        summary={"workflow_definitions": len(items), "live_runs_checked": 0},
        items=items,
    )


def build_bundle() -> dict[str, dict[str, Any]]:
    files = repository_files()
    registry = read_json(REGISTRY)
    bots, divisions, capabilities = build_fleet(registry)
    payloads = {
        "repository-inventory.json": build_repository_inventory(files),
        "bots.json": bots,
        "divisions.json": divisions,
        "capabilities.json": capabilities,
        "benchmarks.json": build_benchmarks(),
        "workflows.json": build_workflows(),
    }
    status_counts = Counter()
    for payload in payloads.values():
        if payload.get("status") in EVIDENCE_TAXONOMY:
            status_counts[payload["status"]] += 1
        status_counts.update(item.get("status") for item in payload.get("items", []) if item.get("status") in EVIDENCE_TAXONOMY)
    health = artifact(
        "dreamco.command_center.system_health.v1",
        [REGISTRY, BENCHMARK_INDEX, ROOT / "package.json"],
        summary={
            "status_counts": {status: status_counts.get(status, 0) for status in EVIDENCE_TAXONOMY},
            "generator_status": "sandbox_verified",
            "live_provider_checks": 0,
            "production_checks": 0,
        },
        checks=[
            {"id": "registry-loaded", "status": "sandbox_verified", "evidence_refs": ["tests/test_command_center_data.py"]},
            {"id": "taxonomy-enforced", "status": "sandbox_verified", "evidence_refs": ["tests/test_command_center_data.py"]},
            {"id": "deterministic-output", "status": "sandbox_verified", "evidence_refs": ["tests/test_command_center_data.py"]},
        ],
    )
    readiness = artifact(
        "dreamco.command_center.release_readiness.v1",
        [ROOT / "package.json", ROOT / "tools" / "production_readiness_gate.py"],
        overall_status="implemented",
        production_ready=False,
        blockers=[
            "Live provider, deployment, and production checks are outside this offline generation step.",
            "Merge-level and strict production-readiness suites must pass in CI before promotion.",
        ],
        required_commands=["npm run test:command-center", "npm run test:repository", "npm run production:readiness:strict"],
        evidence_refs=["tools/production_readiness_gate.py", ".github/workflows/command-center-index.yml"],
    )
    payloads["system-health.json"] = health
    payloads["release-readiness.json"] = readiness
    entries = []
    for name, payload in sorted(payloads.items()):
        body = canonical_json(payload).encode()
        entries.append({"name": name, "schema": payload["schema"], "sha256": digest_bytes(body), "bytes": len(body)})
    payloads["index.json"] = artifact(
        "dreamco.command_center.index.v1",
        [REGISTRY, BENCHMARK_INDEX, ROOT / "tools" / "generate_command_center_data.py"],
        summary={
            "artifacts": len(entries),
            "bots": bots["summary"]["registered_bots"],
            "divisions": divisions["summary"]["registered_divisions"],
            "capabilities": capabilities["summary"]["unique_capabilities"],
            "benchmark_programs": payloads["benchmarks.json"]["summary"]["registered_benchmark_programs"],
            "workflows": payloads["workflows.json"]["summary"]["workflow_definitions"],
        },
        artifacts=entries,
    )
    return payloads


def write_or_check(payloads: dict[str, dict[str, Any]], check: bool) -> list[str]:
    stale = []
    for directory in (COMMAND_DATA, WEBSITE_DATA):
        if not check:
            directory.mkdir(parents=True, exist_ok=True)
        for name in GENERATED_NAMES:
            path = directory / name
            expected = canonical_json(payloads[name])
            if check:
                if not path.exists() or path.read_text(encoding="utf-8") != expected:
                    stale.append(path.relative_to(ROOT).as_posix())
            else:
                path.write_text(expected, encoding="utf-8")
    return stale


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail when committed artifacts are stale")
    args = parser.parse_args()
    payloads = build_bundle()
    stale = write_or_check(payloads, args.check)
    if stale:
        print("Command-center artifacts are stale or missing:", file=sys.stderr)
        print("\n".join(f"- {path}" for path in stale), file=sys.stderr)
        return 1
    action = "validated" if args.check else "generated"
    print(f"Command-center data {action}: {len(payloads)} artifacts in 2 destinations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
