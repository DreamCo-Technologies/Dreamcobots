from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard_capability_adapter import normalize_dashboard_schema


REPO_ROOT = Path(__file__).resolve().parent
INVENTORY_DIR = REPO_ROOT / "dashboard_inventory"
DREAMCO_LEGACY_DIR = INVENTORY_DIR / "dreamco_legacy_assets"

SOURCE_HINTS = [
    "docs/dashboards.html",
    "ui/web_dashboard.py",
    "dashboard/static/dashboard.js",
    "dreamco/frontend/dashboard.js",
    ".dreamco",
    "dreamco.nix",
    "dreamco.md",
]

DISCOVERY_GLOBS = [
    "**/*dashboard*.py",
    "**/*dashboard*.js",
    "**/*dashboard*.html",
    "**/*dashboard*.md",
    "**/*analytics*.py",
    "**/*analytics*.js",
    "**/*governance*.py",
    "**/*admin*.py",
    "**/*monitor*.py",
    "**/*operator*.py",
    "**/*monetization*.py",
    "**/*.zip",
    "**/*.tar",
    "**/*.tar.gz",
    "**/*.tgz",
]

IGNORED_PARTS = {".git", "node_modules", "__pycache__", ".pytest_cache"}

ENDPOINT_PATTERN = re.compile(r"['\"](/api/[A-Za-z0-9_\-./{}:]+)['\"]")
BUTTON_PATTERN = re.compile(r"<button|onclick=|\bstart\(|\bstop\(|\bgo_live\b", re.IGNORECASE)
ACTION_PATTERN = re.compile(r"fetch\(|axios\.|XMLHttpRequest|method\s*:\s*['\"](POST|PUT|PATCH|DELETE)", re.IGNORECASE)
WS_PATTERN = re.compile(r"\b(wss?://|WebSocket\()", re.IGNORECASE)
ROUTE_PATTERN = re.compile(r"@\w+\.route\(|\bFastAPI\(|\bAPIRouter\(|\bapp\.(get|post|put|delete)\(", re.IGNORECASE)
QUEUE_PATTERN = re.compile(r"\b(queue|enqueue|dequeue|celery|rabbitmq|sqs|redis\s*queue|job\s*queue)\b", re.IGNORECASE)
ORCHESTRATOR_PATTERN = re.compile(r"\b(orchestrator|control_center|runtime|lifecycle|workflow)\b", re.IGNORECASE)
GITHUB_ACTIONS_PATTERN = re.compile(r"\bgithub\s*actions|/actions/|workflow\b", re.IGNORECASE)
PERSISTENCE_PATTERN = re.compile(r"\b(sqlite|postgres|mysql|mongo|redis|persist|storage|database|db\.)\b", re.IGNORECASE)

SECURITY_PATTERNS = {
    "hardcoded_secret_like_value": re.compile(
        r"(api[_-]?key|secret|token|client_secret|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]",
        re.IGNORECASE,
    ),
    "jwt_like_token": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "oauth_credentials": re.compile(r"(client_id|client_secret|oauth_token)", re.IGNORECASE),
    "insecure_websocket": re.compile(r"\bws://", re.IGNORECASE),
    "unrestricted_cors": re.compile(r"CORS\([^)]*\*|Access-Control-Allow-Origin\s*[:=]\s*['\"]\*['\"]", re.IGNORECASE),
    "hardcoded_admin_path": re.compile(r"['\"]/admin(?:/|['\"]|$)", re.IGNORECASE),
}

AUTH_PATTERNS = [
    ("rbac", re.compile(r"\brbac\b", re.IGNORECASE)),
    ("oauth", re.compile(r"\boauth|openid|github auth|google auth\b", re.IGNORECASE)),
    ("jwt", re.compile(r"\bjwt|bearer\b", re.IGNORECASE)),
    ("session", re.compile(r"\bsession\b", re.IGNORECASE)),
    ("api_key", re.compile(r"api[_-]?key|token", re.IGNORECASE)),
]

CAPABILITY_KEYWORDS = {
    "operations": ["operation", "monitor", "status", "control", "runtime"],
    "governance": ["governance", "policy", "admin", "approval", "rbac", "audit"],
    "monetization": ["revenue", "billing", "pricing", "payment", "monetization"],
    "analytics": ["analytics", "telemetry", "metric", "insight", "report"],
    "automation": ["workflow", "automation", "ci", "cd", "actions"],
    "queue": ["queue", "job", "scheduler"],
    "event": ["event", "webhook", "bus"],
    "integration": ["integration", "github", "slack", "api"],
    "bot_control": ["bot", "start", "stop", "go live", "deploy"],
}


@dataclass(slots=True)
class DashboardSource:
    path: Path
    relative_path: str
    text: str


def _iter_discovered_paths() -> list[Path]:
    discovered: set[Path] = set()
    for rel_path in SOURCE_HINTS:
        candidate = REPO_ROOT / rel_path
        if candidate.exists() and candidate.is_file():
            discovered.add(candidate.resolve())

    for pattern in DISCOVERY_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            if not path.is_file():
                continue
            if any(part in IGNORED_PARTS for part in path.parts):
                continue
            discovered.add(path.resolve())

    return sorted(discovered)


def _read_source(path: Path) -> DashboardSource:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = ""
    return DashboardSource(path=path, relative_path=str(path.relative_to(REPO_ROOT)), text=text)


def _extract_capabilities(text: str, relative_path: str) -> list[str]:
    lowered = f"{relative_path}\n{text[:20000]}".lower()
    matched = []
    for capability, keywords in CAPABILITY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matched.append(capability)
    return sorted(set(matched))


def _extract_auth_model(text: str) -> str:
    for name, pattern in AUTH_PATTERNS:
        if pattern.search(text):
            return name
    return "none_detected"


def _extract_security_findings(text: str) -> list[str]:
    findings = []
    for finding, pattern in SECURITY_PATTERNS.items():
        if pattern.search(text):
            findings.append(finding)
    return sorted(findings)


def _deployment_readiness(relative_path: str, text: str) -> str:
    lowered = f"{relative_path}\n{text[:20000]}".lower()
    high_signals = ["create_app", "@app.route", "fastapi", "workflow", "tests/"]
    med_signals = ["dashboard", "api", "render", "bot"]
    score = sum(1 for token in high_signals if token in lowered) * 2 + sum(1 for token in med_signals if token in lowered)
    if score >= 8:
        return "production"
    if score >= 4:
        return "staging"
    if score >= 1:
        return "experimental"
    return "unknown"


def _source_type(path: str) -> str:
    if path.endswith((".js", ".html", ".css")):
        return "frontend"
    if path.endswith(".py"):
        return "backend"
    if path.endswith((".yml", ".yaml")):
        return "workflow"
    if path.endswith((".zip", ".tar", ".tar.gz", ".tgz")):
        return "archive"
    return "document"


def _dead_dashboard(relative_path: str, capabilities: list[str], endpoints: list[str], buttons: int, actions: int) -> bool:
    rel = relative_path.lower()
    archive_markers = ["archive", "archived", "legacy", "prototype", "abandoned", "old", "backup"]
    if any(marker in rel for marker in archive_markers):
        return True
    if not capabilities and not endpoints and buttons == 0 and actions == 0:
        return True
    return False


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


def _build_registry(sources: list[DashboardSource]) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    entries: list[dict[str, Any]] = []
    duplicate_groups: dict[str, list[str]] = {}

    for source in sources:
        text = source.text
        endpoints = sorted(set(ENDPOINT_PATTERN.findall(text)))
        button_count = len(BUTTON_PATTERN.findall(text))
        action_count = len(ACTION_PATTERN.findall(text))
        capabilities = _extract_capabilities(text, source.relative_path)
        governance_features = [c for c in capabilities if c in {"governance", "automation"}]
        revenue_controls = [c for c in capabilities if c == "monetization"]
        bot_controls = [c for c in capabilities if c == "bot_control"]

        schema = normalize_dashboard_schema(
            dashboard_id=source.relative_path,
            raw={
                "capabilities": capabilities,
                "buttons_actions": [f"buttons:{button_count}", f"actions:{action_count}"],
                "api_endpoints": endpoints,
                "bot_controls": bot_controls,
                "governance_features": governance_features,
                "revenue_controls": revenue_controls,
                "auth_model": _extract_auth_model(text),
                "deployment_readiness": _deployment_readiness(source.relative_path, text),
                "security_findings": _extract_security_findings(text),
                "duplicate_mappings": [],
            },
        )

        entry = {
            "id": source.relative_path,
            "path": source.relative_path,
            "source_type": _source_type(source.relative_path),
            "capabilities": schema["capabilities"],
            "buttons_actions": {
                "buttons": button_count,
                "actions": action_count,
            },
            "api_endpoints": schema["api_endpoints"],
            "websocket_usage": bool(WS_PATTERN.search(text)),
            "routes_detected": bool(ROUTE_PATTERN.search(text)),
            "queue_integrations": bool(QUEUE_PATTERN.search(text)),
            "orchestrator_bindings": bool(ORCHESTRATOR_PATTERN.search(text)),
            "github_actions_integrations": bool(GITHUB_ACTIONS_PATTERN.search(text)),
            "persistence_hooks": bool(PERSISTENCE_PATTERN.search(text)),
            "bot_controls": schema["bot_controls"],
            "governance_features": schema["governance_features"],
            "revenue_controls": schema["revenue_controls"],
            "auth_model": schema["auth_model"],
            "deployment_readiness": schema["deployment_readiness"],
            "security_findings": schema["security_findings"],
            "dead_dashboard": _dead_dashboard(source.relative_path, capabilities, endpoints, button_count, action_count),
            "content_hash": _content_hash(text[:40000]),
        }
        entries.append(entry)

        duplicate_key = json.dumps(
            {
                "name": Path(source.relative_path).name.lower(),
                "endpoints": endpoints,
                "capabilities": capabilities,
            },
            sort_keys=True,
        )
        duplicate_groups.setdefault(duplicate_key, []).append(source.relative_path)

    duplicate_map: dict[str, list[str]] = {}
    for group in duplicate_groups.values():
        if len(group) < 2:
            continue
        for member in group:
            duplicate_map[member] = sorted([x for x in group if x != member])

    for entry in entries:
        entry["duplicate_mappings"] = duplicate_map.get(entry["id"], [])

    return entries, duplicate_map


def _lineage_map(entries: list[dict[str, Any]], duplicate_map: dict[str, list[str]]) -> dict[str, Any]:
    seen = set()
    groups = []
    for entry in entries:
        anchor = entry["id"]
        if anchor in seen:
            continue
        related = sorted(set([anchor, *duplicate_map.get(anchor, [])]))
        for item in related:
            seen.add(item)
        groups.append(
            {
                "canonical": related[0],
                "related": related,
                "kind": "duplicate_cluster" if len(related) > 1 else "singleton",
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clusters": sorted(groups, key=lambda x: x["canonical"]),
    }


def _capability_graph(entries: list[dict[str, Any]]) -> dict[str, Any]:
    capability_nodes = sorted({cap for entry in entries for cap in entry.get("capabilities", [])})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "nodes": {
            "dashboards": [entry["id"] for entry in entries],
            "capabilities": capability_nodes,
        },
        "edges": [
            {"from": entry["id"], "to": capability}
            for entry in entries
            for capability in entry.get("capabilities", [])
        ],
    }


def _migration_candidates(entries: list[dict[str, Any]]) -> dict[str, Any]:
    target_caps = {"bot_control", "monetization", "automation", "integration", "analytics", "queue", "governance"}
    selected = []
    for entry in entries:
        capabilities = set(entry.get("capabilities", []))
        if entry.get("dead_dashboard"):
            continue
        if capabilities.intersection(target_caps):
            selected.append(
                {
                    "id": entry["id"],
                    "path": entry["path"],
                    "capabilities": sorted(capabilities.intersection(target_caps)),
                    "deployment_readiness": entry["deployment_readiness"],
                    "auth_model": entry["auth_model"],
                    "security_findings": entry["security_findings"],
                }
            )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_capabilities": sorted(target_caps),
        "candidates": sorted(selected, key=lambda x: (x["deployment_readiness"], x["id"]), reverse=True),
    }


def _dead_dashboards(entries: list[dict[str, Any]]) -> dict[str, Any]:
    dead = [
        {
            "id": entry["id"],
            "path": entry["path"],
            "reason": "archived_or_low_signal",
            "duplicate_mappings": entry.get("duplicate_mappings", []),
        }
        for entry in entries
        if entry.get("dead_dashboard")
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dead_dashboards": sorted(dead, key=lambda x: x["id"]),
    }


def _dreamco_assets(entries: list[dict[str, Any]]) -> dict[str, Any]:
    dreamco_entries = [entry for entry in entries if "dreamco" in entry["path"].lower() or entry["path"].endswith(".dreamco")]
    archive_entries = [
        entry
        for entry in entries
        if entry["path"].lower().endswith((".zip", ".tar", ".tar.gz", ".tgz"))
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dreamco_assets": dreamco_entries,
        "archived_assets": archive_entries,
    }


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_inventory() -> dict[str, Any]:
    sources = [_read_source(path) for path in _iter_discovered_paths()]
    entries, duplicate_map = _build_registry(sources)

    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(entries),
        "dashboards": sorted(entries, key=lambda x: x["id"]),
    }

    _write_json(INVENTORY_DIR / "canonical_dashboard_registry.json", registry)
    _write_json(INVENTORY_DIR / "dashboard_lineage_map.json", _lineage_map(entries, duplicate_map))
    _write_json(INVENTORY_DIR / "dashboard_capability_graph.json", _capability_graph(entries))
    _write_json(INVENTORY_DIR / "migration_candidates.json", _migration_candidates(entries))
    _write_json(INVENTORY_DIR / "dead_dashboards.json", _dead_dashboards(entries))
    _write_json(DREAMCO_LEGACY_DIR / "assets_inventory.json", _dreamco_assets(entries))

    return {
        "inventory_dir": str(INVENTORY_DIR),
        "dashboard_count": len(entries),
    }


def main() -> None:
    result = build_inventory()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
