"""
bot_control_api.py — API endpoints for bot control and integration.

Exposes a REST-style interface for managing DreamCo bot deployments,
triggering retraining, rolling back strategies, and querying bot status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .learning_api import APIResponse


class BotControlAPI:
    """
    Framework-agnostic REST API for DreamCo bot control operations.

    Parameters
    ----------
    prefix : str
        URL prefix for all bot-control routes.
    """

    def __init__(self, prefix: str = "/api/v1/bots"):
        self.prefix = prefix.rstrip("/")
        self._routes: Dict[str, Dict[str, Callable]] = {}
        self._register_defaults()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def register_route(self, path: str, method: str, handler: Callable) -> None:
        """Register a custom handler for *method* + *path*."""
        full_path = self.prefix + path
        if full_path not in self._routes:
            self._routes[full_path] = {}
        self._routes[full_path][method.upper()] = handler

    def dispatch(self, path: str, method: str = "GET", payload: Optional[Dict] = None) -> APIResponse:
        """Dispatch a request to the matching handler."""
        handlers = self._routes.get(path, {})
        handler = handlers.get(method.upper())
        if handler is None:
            return APIResponse(status="error", error=f"Route {method} {path} not found.")
        try:
            result = handler(payload) if payload is not None else handler()
            return result if isinstance(result, APIResponse) else APIResponse(status="ok", data=result)
        except Exception as exc:  # noqa: BLE001
            return APIResponse(status="error", error=str(exc))

    def list_routes(self) -> List[Dict[str, str]]:
        """Return all registered routes."""
        routes = []
        for path, methods in self._routes.items():
            for method in methods:
                routes.append({"path": path, "method": method})
        return routes

    # ------------------------------------------------------------------
    # Default route registrations
    # ------------------------------------------------------------------

    def _register_defaults(self) -> None:
        self.register_route("/health", "GET", self._health_handler)
        self.register_route("/list", "GET", self._list_bots_handler)
        self.register_route("/deploy", "POST", self._deploy_handler)
        self.register_route("/rollback", "POST", self._rollback_handler)
        self.register_route("/retrain", "POST", self._retrain_handler)
        self.register_route("/status", "GET", self._status_handler)

    # ------------------------------------------------------------------
    # Default handlers (stubs)
    # ------------------------------------------------------------------

    def _health_handler(self) -> APIResponse:
        return APIResponse(status="ok", data={"service": "bot_control_api", "healthy": True})

    def _list_bots_handler(self) -> APIResponse:
        return APIResponse(status="ok", data={"bots": [], "message": "Connect to BotUpdater."})

    def _deploy_handler(self, payload: Optional[Dict]) -> APIResponse:
        p = payload or {}
        return APIResponse(
            status="ok",
            data={
                "deployment_id": p.get("deployment_id", ""),
                "strategy_id": p.get("strategy_id", ""),
                "message": "Connect to StrategyDeployer.",
            },
        )

    def _rollback_handler(self, payload: Optional[Dict]) -> APIResponse:
        p = payload or {}
        return APIResponse(
            status="ok",
            data={"deployment_id": p.get("deployment_id", ""), "message": "Connect to StrategyDeployer.rollback()."},
        )

    def _retrain_handler(self, payload: Optional[Dict]) -> APIResponse:
        p = payload or {}
        return APIResponse(
            status="ok",
            data={"bot_name": p.get("bot_name", ""), "message": "Connect to BotUpdater.trigger_retrain()."},
        )

    def _status_handler(self) -> APIResponse:
        return APIResponse(status="ok", data={"status": "operational", "message": "Connect to BotUpdater."})
