#!/usr/bin/env python3
"""Build the public-safe, evidence-backed Buddy learning OS connection graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (
    ROOT / "config/generated/buddy-learning-os-connections.json",
    ROOT / "website/data/buddy-learning-os-connections.json",
)
EXTERNAL_CATALOG = ROOT / "website/data/buddy-connection-catalog.json"
RUNTIME_EVIDENCE = ROOT / "config/runtime-connection-evidence.json"

CATEGORIES = {
    "agents": ("/.github/agents/", "/agents/", "agent"),
    "models": ("/models/", "model"),
    "wrappers_adapters": ("/adapters/", "/connectors/", "adapter", "connector", "wrapper", "bridge"),
    "resources": ("/resources/", "resource", "dataset"),
    "learning": ("/learning/", "learning_", "curriculum", "skill_lifecycle", "/skills/"),
    "memory": ("/memory/", "memory_", "knowledge"),
    "benchmarks": ("/benchmarks/", "benchmark", "evaluation", "eval_"),
    "ontology": ("/ontology/", "ontology", "context_fabric"),
    "tools": ("/tools/", "tool_registry", "capability"),
    "runtime_workflows": ("/workflows/", "/integration/", "/execution/", "runtime", "orchestr", "task_runner"),
    "interfaces": ("/website/", "/client/", "/dashboards/", "command_center"),
}
ALLOWED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".yaml", ".yml", ".html"}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return sorted(line for line in result.stdout.splitlines() if line)


def categories_for(path: str) -> list[str]:
    searchable = f"/{path.lower()}"
    return [name for name, signals in CATEGORIES.items() if any(signal in searchable for signal in signals)]


def node_id(kind: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{kind}:{digest}"


def build_graph() -> dict[str, Any]:
    nodes: list[dict[str, Any]] = [{
        "id": "buddy:learning-os",
        "name": "Buddy Learning Operating System",
        "kind": "orchestrator",
        "categories": ["runtime_workflows", "learning"],
        "status": "connected",
        "readiness": "repository_verified",
        "source_path": "buddy_os/integration/learning_os_connection_graph.py",
        "evidence": ["tests/test_buddy_learning_os_connections.py"],
    }]
    edges: list[dict[str, str]] = []
    for path in tracked_files():
        suffix = Path(path).suffix.lower()
        categories = categories_for(path)
        if suffix not in ALLOWED_EXTENSIONS or not categories:
            continue
        nid = node_id("repo", path)
        nodes.append({
            "id": nid,
            "name": Path(path).name,
            "kind": "repository_component",
            "categories": categories,
            "status": "connected",
            "readiness": "source_verified",
            "source_path": path,
            "evidence": [path],
        })
        relationship = "trained_by" if "learning" in categories else "routes_to"
        edges.append({"from": "buddy:learning-os", "to": nid, "type": relationship})

    catalog = json.loads(EXTERNAL_CATALOG.read_text(encoding="utf-8"))
    evidence_doc = json.loads(RUNTIME_EVIDENCE.read_text(encoding="utf-8"))
    evidence_by_id = {row["connection_id"]: row for row in evidence_doc.get("evidence", [])}
    for profile in catalog.get("platform_profiles", []):
        evidence = evidence_by_id.get(profile["id"], {})
        verified = evidence.get("status") == "runtime_verified"
        nid = f"external:{profile['id']}"
        nodes.append({
            "id": nid,
            "name": profile["label"],
            "kind": "external_resource",
            "categories": ["resources", "wrappers_adapters"],
            "status": "connected" if verified else "partial",
            "readiness": "runtime_verified" if verified else "credentials_required",
            "source_path": "website/data/buddy-connection-catalog.json",
            "evidence": [evidence["evidence_reference"]] if evidence.get("evidence_reference") else [],
        })
        edges.append({"from": "buddy:learning-os", "to": nid, "type": "depends_on"})

    category_counts = Counter(category for node in nodes for category in node["categories"])
    status_counts = Counter(node["status"] for node in nodes)
    readiness_counts = Counter(node["readiness"] for node in nodes)
    graph = {
        "schema": "dreamco.buddy_learning_os_connections.v1",
        "root_node": "buddy:learning-os",
        "truth_boundary": (
            "Repository presence proves discoverability, not live provider access or model quality. "
            "External resources are runtime_verified only when authorized probe evidence exists."
        ),
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "category_counts": dict(sorted(category_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "readiness_counts": dict(sorted(readiness_counts.items())),
            "unlinked_node_count": 0,
        },
        "nodes": nodes,
        "edges": edges,
    }
    return graph


def render(graph: dict[str, Any]) -> str:
    return json.dumps(graph, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args()
    content = render(build_graph())
    stale = [path for path in OUTPUTS if not path.exists() or path.read_text(encoding="utf-8") != content]
    if args.check:
        if stale:
            print("Stale Buddy learning OS graph: " + ", ".join(str(p.relative_to(ROOT)) for p in stale))
            return 1
    else:
        for path in OUTPUTS:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    graph = json.loads(content)
    print(json.dumps(graph["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
