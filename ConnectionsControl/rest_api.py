"""
REST API Manager for DreamCobots ConnectionsControl.

Manages endpoint registration and simulates API requests.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class APIEndpoint:
    path: str
    method: str
    description: str
    auth_required: bool = True
    handler: Optional[Callable] = None


class RestAPIManager:
    """Manages REST API endpoint registration and simulation."""

    def __init__(self) -> None:
        self._endpoints: Dict[str, APIEndpoint] = {}
        self._request_log: List[dict] = []

    def register_endpoint(
        self,
        path: str,
        method: str,
        handler: Callable,
        description: str = "",
        auth_required: bool = True,
    ) -> APIEndpoint:
        """Register a new API endpoint."""
        key = f"{method.upper()}:{path}"
        endpoint = APIEndpoint(
            path=path,
            method=method.upper(),
            description=description,
            auth_required=auth_required,
            handler=handler,
        )
        self._endpoints[key] = endpoint
        return endpoint

    def list_endpoints(self) -> List[dict]:
        """Return a list of all registered endpoints (without handler refs)."""
        return [
            {
                "path": ep.path,
                "method": ep.method,
                "description": ep.description,
                "auth_required": ep.auth_required,
            }
            for ep in self._endpoints.values()
        ]

    def simulate_request(self, path: str, method: str, payload: dict = None) -> dict:
        """Simulate an API request and return a mock response dict."""
        key = f"{method.upper()}:{path}"
        endpoint = self._endpoints.get(key)
        log_entry = {
            "request_id": str(uuid.uuid4()),
            "path": path,
            "method": method.upper(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        if not endpoint:
            log_entry["status"] = 404
            log_entry["body"] = {"error": "endpoint_not_found"}
            self._request_log.append(log_entry)
            return log_entry
        if endpoint.handler:
            try:
                result = endpoint.handler(payload or {})
                log_entry["status"] = 200
                log_entry["body"] = result
            except Exception as exc:  # noqa: BLE001
                log_entry["status"] = 500
                log_entry["body"] = {"error": str(exc)}
        else:
            log_entry["status"] = 200
            log_entry["body"] = {"message": "ok", "path": path}
        self._request_log.append(log_entry)
        return log_entry

    def generate_api_docs(self) -> str:
        """Return Markdown documentation of all registered endpoints."""
        lines = ["# DreamCobots REST API Documentation\n"]
        lines.append(f"Generated: {datetime.utcnow().isoformat()}\n")
        lines.append("## Endpoints\n")
        for ep in self._endpoints.values():
            auth = "🔒 Auth required" if ep.auth_required else "🔓 Public"
            lines.append(f"### `{ep.method} {ep.path}`")
            lines.append(f"- **Description**: {ep.description or 'N/A'}")
            lines.append(f"- **Auth**: {auth}\n")
        return "\n".join(lines)

    def get_request_log(self) -> List[dict]:
        """Return the request simulation log."""
        return list(self._request_log)

    def get_status(self) -> dict:
        """Return API manager status summary."""
        return {
            "registered_endpoints": len(self._endpoints),
            "total_requests_simulated": len(self._request_log),
        }
