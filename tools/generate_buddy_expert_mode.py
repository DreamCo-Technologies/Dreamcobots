#!/usr/bin/env python3
"""Build Buddy Expert Mode from the repository's real resource and connection catalogs."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "buddy-expert-mode.json"
INVENTION = ROOT / "config" / "buddy-invention-to-store.json"
RESOURCES = ROOT / "website" / "data" / "buddy-resource-connection-catalog.json"
CONNECTIONS = ROOT / "website" / "data" / "buddy-connection-catalog.json"
LEARNING_GRAPH = ROOT / "website" / "data" / "buddy-learning-os-connections.json"
LEARNING_STRATEGIES = ROOT / "config" / "buddy-learning-strategies.json"
LEARNING_SOURCES = ROOT / "config" / "buddy-learning-source-adapters.json"
ACTIONS = ROOT / "website" / "data" / "actions-health-report.json"
OUTPUTS = (
    ROOT / "config" / "generated" / "buddy_expert_mode.json",
    ROOT / "website" / "data" / "buddy-expert-mode.js",
)


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected object in {path.relative_to(ROOT)}")
    return payload


def validate_invention(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "dreamco.buddy_invention_to_store.v1":
        raise ValueError("Unsupported invention navigator schema.")
    resources = payload.get("resources", [])
    resource_ids = [item.get("id") for item in resources]
    if len(resources) < 35 or len(resource_ids) != len(set(resource_ids)):
        raise ValueError("Invention resources need broad unique coverage.")
    for item in resources:
        source = urlsplit(str(item.get("url", "")))
        if source.scheme != "https" or not source.netloc:
            raise ValueError(f"Invention resources require HTTPS: {item.get('id')}")
        if "connected" == item.get("connection_status"):
            raise ValueError("An invention resource cannot be marked connected without runtime evidence.")
    known = set(resource_ids)
    for stage in payload.get("stages", []):
        unknown = set(stage.get("resource_ids", [])) - known
        if unknown:
            raise ValueError(f"Unknown invention resources in {stage.get('id')}: {sorted(unknown)}")
    used = {item for stage in payload.get("stages", []) for item in stage.get("resource_ids", [])}
    if known - used:
        raise ValueError(f"Invention resources are not routed to a stage: {sorted(known - used)}")


def choose_day(resource: dict[str, Any], days: list[dict[str, Any]]) -> int:
    searchable = " ".join([resource.get("host", ""), *resource.get("source_lists", [])]).lower()
    scores = [sum(1 for keyword in day["keywords"] if keyword in searchable) for day in days]
    best = max(scores)
    if best:
        return scores.index(best)
    digest = hashlib.sha256(resource["id"].encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % len(days)


def build() -> dict[str, Any]:
    protocol = load(PROTOCOL)
    invention = load(INVENTION)
    resource_catalog = load(RESOURCES)
    connections = load(CONNECTIONS)
    graph = load(LEARNING_GRAPH)
    strategies = load(LEARNING_STRATEGIES)
    learning_sources = load(LEARNING_SOURCES)
    actions = load(ACTIONS)
    if protocol.get("schema") != "dreamco.buddy_expert_mode.v1":
        raise ValueError("Unsupported Buddy Expert Mode schema.")
    days = protocol.get("days", [])
    if [item.get("day") for item in days] != list(range(1, 8)):
        raise ValueError("Expert Mode must contain exactly days one through seven.")
    validate_invention(invention)

    resources = resource_catalog.get("resources", [])
    resource_ids = [item.get("id") for item in resources]
    if len(resource_ids) != len(set(resource_ids)) or any(not item for item in resource_ids):
        raise ValueError("Repository resource ids must be present and unique.")
    day_resources: list[list[dict[str, Any]]] = [[] for _ in days]
    section_index: dict[str, list[str]] = defaultdict(list)
    for resource in resources:
        day_resources[choose_day(resource, days)].append(resource)
        for source in resource.get("source_lists", []):
            section_index[source].append(resource["id"])
    schedule = []
    assigned: list[str] = []
    for day, bucket in zip(days, day_resources):
        ordered = sorted(bucket, key=lambda item: item["id"])
        assigned.extend(item["id"] for item in ordered)
        schedule.append({
            **day,
            "resource_count": len(ordered),
            "resource_ids": [item["id"] for item in ordered],
            "connection_state_counts": dict(sorted(Counter(item.get("connection_status", "unknown") for item in ordered).items())),
            "protocol": protocol["daily_protocol"],
            "evidence_required": ["retrieval receipt", "source verification", "application fixture", "active-recall result", "teach-back result", "hidden holdout result", "cost latency and failure record"],
        })
    if len(assigned) != len(resources) or set(assigned) != set(resource_ids):
        raise ValueError("Every repository resource must be assigned to exactly one Expert Mode day.")

    connection_methods = resource_catalog.get("connection_methods", [])
    if "mcp_transport" not in connection_methods or "custom_rest" not in connection_methods:
        raise ValueError("Expert Mode requires both MCP and API connection options.")
    runtime_verified = int(graph.get("summary", {}).get("readiness_counts", {}).get("runtime_verified", 0))
    return {
        **protocol,
        "summary": {
            "days": len(schedule),
            "repository_resources": len(resources),
            "resource_sections": len(section_index),
            "learning_graph_nodes": int(graph.get("summary", {}).get("node_count", 0)),
            "learning_techniques": len(strategies.get("techniques", [])),
            "learning_source_adapters": len(learning_sources.get("sources", [])),
            "actions_workflows": int(actions.get("workflow_count", 0)),
            "connection_methods": len(connection_methods),
            "runtime_verified_external_connections": runtime_verified,
            "invention_stages": len(invention.get("stages", [])),
            "invention_resources": len(invention.get("resources", [])),
        },
        "days": schedule,
        "resource_index": resources,
        "resource_section_index": [
            {"source": source, "resource_count": len(ids), "resource_ids": sorted(ids)}
            for source, ids in sorted(section_index.items())
        ],
        "connections": {
            "methods": connection_methods,
            "auth_methods": connections.get("auth_methods", []),
            "connector_contracts": connections.get("connector_contracts", []),
            "platform_profiles": connections.get("platform_profiles", []),
            "secret_rule": resource_catalog.get("secret_rule"),
        },
        "learning_strategy_summary": {
            "techniques": len(strategies.get("techniques", [])),
            "categories": len({item.get("category") for item in strategies.get("techniques", [])}),
            "failure_controls": len(strategies.get("failure_controls", [])),
        },
        "learning_sources": learning_sources,
        "actions_summary": {
            "workflows": int(actions.get("workflow_count", 0)),
            "static_passed": int(actions.get("workflow_count", 0)) - int(actions.get("critical_error_count", 0)),
            "static_failed": int(actions.get("critical_error_count", 0)),
            "live_operational_evidence": int(actions.get("operational_workflow_count", 0)),
        },
        "invention_navigator": invention,
        "truth": {
            **protocol.get("truth", {}),
            "all_repository_resources_assigned": True,
            "live_resource_connections_proven": runtime_verified,
            "universal_mastery_proven": False,
            "production_ready": False,
        },
    }


def serialized(payload: dict[str, Any]) -> tuple[str, str]:
    document = json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True) + "\n"
    # Pages already ships the full resource catalog. Keep the public Expert
    # payload small enough for the zero-cost hosting gate instead of duplicating
    # hundreds of records and source-section memberships.
    public_payload = {key: value for key, value in payload.items() if key not in {"resource_index", "resource_section_index"}}
    public_payload["resource_catalog_url"] = "data/buddy-resource-connection-catalog.json"
    public_payload["connections"] = {
        "methods": payload["connections"]["methods"],
        "secret_rule": payload["connections"]["secret_rule"],
    }
    public = f"window.BUDDY_EXPERT_MODE={json.dumps(public_payload, separators=(',', ':'), ensure_ascii=True, sort_keys=True)};\n"
    return document, public


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    expected = serialized(payload)
    stale = [path for path, content in zip(OUTPUTS, expected) if not path.exists() or path.read_text(encoding="utf-8") != content]
    if args.check and stale:
        raise SystemExit("Expert Mode outputs are stale: " + ", ".join(str(path.relative_to(ROOT)) for path in stale))
    if not args.check:
        for path, content in zip(OUTPUTS, expected):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
