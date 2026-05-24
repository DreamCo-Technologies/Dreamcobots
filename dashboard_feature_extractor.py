from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard_inventory_builder import INVENTORY_DIR, REPO_ROOT, build_inventory


FRONTEND_HANDLER_PATTERN = re.compile(r"\bfunction\s+([A-Za-z0-9_]+)\s*\(|=>\s*\{", re.IGNORECASE)
REST_PATTERN = re.compile(r"['\"](/api/[A-Za-z0-9_\-./{}:]+)['\"]")
AUTH_PATTERN = re.compile(r"\boauth|jwt|session|rbac|api[_-]?key|token\b", re.IGNORECASE)
TELEMETRY_PATTERN = re.compile(r"\btelemetry|metrics|kpi|monitor|insight|analytics\b", re.IGNORECASE)
EMBEDDED_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|secret|token|client_secret|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]",
    re.IGNORECASE,
)
ROUTES_PATTERN = re.compile(r"@\w+\.route\(|\bFastAPI\(|\bAPIRouter\(", re.IGNORECASE)
QUEUE_PATTERN = re.compile(r"\b(queue|enqueue|dequeue|job|celery|rabbitmq|sqs)\b", re.IGNORECASE)
ORCHESTRATOR_PATTERN = re.compile(r"\borchestrator|control_center|runtime|lifecycle\b", re.IGNORECASE)
GITHUB_ACTIONS_PATTERN = re.compile(r"\bgithub\s*actions|workflow\b", re.IGNORECASE)
PERSISTENCE_PATTERN = re.compile(r"\bpersist|storage|database|sqlite|postgres|redis|mysql\b", re.IGNORECASE)
COMMAND_CONTROL_PATTERN = re.compile(r"\bstart|stop|go_live|deploy|configure|command\b", re.IGNORECASE)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _source_group(path: str) -> str:
    lowered = path.lower()
    if lowered.endswith((".js", ".html", ".css")):
        return "frontend"
    if lowered.endswith(".py"):
        return "backend"
    return "mixed"


def _feature_groups(entry: dict[str, Any], text: str) -> dict[str, bool]:
    capabilities = set(entry.get("capabilities", []))
    lowered = text.lower()
    return {
        "operations": bool(capabilities.intersection({"operations", "bot_control", "queue"})) or "runtime" in lowered,
        "governance": bool(capabilities.intersection({"governance", "automation"})) or "policy" in lowered or "rbac" in lowered,
        "monetization": "monetization" in capabilities or "revenue" in lowered or "billing" in lowered,
        "growth_analytics": "analytics" in capabilities or "telemetry" in lowered or "kpi" in lowered,
    }


def extract_features() -> dict[str, Any]:
    registry_path = INVENTORY_DIR / "canonical_dashboard_registry.json"
    if not registry_path.exists():
        build_inventory()
    registry = _read_json(registry_path)
    dashboards = registry.get("dashboards", [])

    rows: list[dict[str, Any]] = []
    security_rows: list[dict[str, Any]] = []
    endpoint_universe = set()

    for entry in dashboards:
        path = entry["path"]
        text = _read_text(path)
        endpoints = sorted(set(REST_PATTERN.findall(text)) | set(entry.get("api_endpoints", [])))
        endpoint_universe.update(endpoints)
        handlers = sorted(set(FRONTEND_HANDLER_PATTERN.findall(text)))
        source_group = _source_group(path)

        row = {
            "id": entry["id"],
            "path": path,
            "source_group": source_group,
            "feature_groups": _feature_groups(entry, text),
            "frontend": {
                "button_count": int(entry.get("buttons_actions", {}).get("buttons", 0)),
                "action_count": int(entry.get("buttons_actions", {}).get("actions", 0)),
                "js_handlers": handlers if source_group == "frontend" else [],
                "websocket_usage": bool(entry.get("websocket_usage")),
                "rest_endpoints": endpoints,
                "auth_session_signals": bool(AUTH_PATTERN.search(text)),
                "telemetry_widgets": len(TELEMETRY_PATTERN.findall(text)),
                "embedded_secrets_tokens": bool(EMBEDDED_SECRET_PATTERN.search(text)),
            },
            "backend": {
                "routes_detected": bool(ROUTES_PATTERN.search(text)) or bool(entry.get("routes_detected")),
                "queue_integrations": bool(QUEUE_PATTERN.search(text)) or bool(entry.get("queue_integrations")),
                "orchestrator_bindings": bool(ORCHESTRATOR_PATTERN.search(text)) or bool(entry.get("orchestrator_bindings")),
                "github_actions_integrations": bool(GITHUB_ACTIONS_PATTERN.search(text)) or bool(entry.get("github_actions_integrations")),
                "persistence_hooks": bool(PERSISTENCE_PATTERN.search(text)) or bool(entry.get("persistence_hooks")),
                "command_control_apis": len(COMMAND_CONTROL_PATTERN.findall(text)),
            },
            "security_findings": entry.get("security_findings", []),
            "deployment_readiness": entry.get("deployment_readiness", "unknown"),
            "duplicate_mappings": entry.get("duplicate_mappings", []),
        }
        rows.append(row)

        if row["frontend"]["embedded_secrets_tokens"] or row["security_findings"]:
            security_rows.append(
                {
                    "id": row["id"],
                    "path": row["path"],
                    "embedded_secrets_tokens": row["frontend"]["embedded_secrets_tokens"],
                    "security_findings": row["security_findings"],
                }
            )

    matrix = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dashboard_count": len(rows),
        "endpoint_coverage": {
            "unique_endpoints": len(endpoint_universe),
            "endpoints": sorted(endpoint_universe),
        },
        "dashboards": rows,
    }
    security = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "findings": security_rows,
    }

    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)
    (INVENTORY_DIR / "dashboard_feature_matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (INVENTORY_DIR / "dashboard_security_findings.json").write_text(json.dumps(security, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {"matrix_path": str(INVENTORY_DIR / "dashboard_feature_matrix.json"), "dashboards": len(rows)}


def main() -> None:
    result = extract_features()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
