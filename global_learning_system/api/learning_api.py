"""
learning_api.py — Exposes learning-related API endpoints.

Provides a lightweight REST-style API layer (framework-agnostic) for
querying and updating the Global Learning Matrix, triggering ingestion,
and managing classifier operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class APIResponse:
    """Standard API response envelope."""

    status: str  # "ok" | "error"
    data: Any = None
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Route registry helpers
# ---------------------------------------------------------------------------

_Route = Dict[str, Any]


class LearningAPI:
    """
    Framework-agnostic REST API for the Global Learning System.

    Routes are registered via :meth:`register_route` and dispatched
    through :meth:`dispatch`.  Integrate with Flask, FastAPI, or any
    WSGI/ASGI framework by wiring ``dispatch`` to the respective
    request handler.

    Parameters
    ----------
    prefix : str
        URL prefix prepended to all routes (e.g. ``"/api/v1/learning"``).
    """

    def __init__(self, prefix: str = "/api/v1/learning"):
        self.prefix = prefix.rstrip("/")
        self._routes: Dict[str, Dict[str, Callable]] = {}  # path → {method → handler}
        self._register_defaults()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def register_route(self, path: str, method: str, handler: Callable) -> None:
        """
        Register a handler for *method* requests to *path*.

        Parameters
        ----------
        path : str
            Relative path (without prefix), e.g. ``"/matrix/rank"``.
        method : str
            HTTP method (``"GET"``, ``"POST"``, etc.).
        handler : callable
            Zero-or-one-argument callable returning an ``APIResponse``.
        """
        full_path = self.prefix + path
        if full_path not in self._routes:
            self._routes[full_path] = {}
        self._routes[full_path][method.upper()] = handler

    def dispatch(self, path: str, method: str = "GET", payload: Optional[Dict] = None) -> APIResponse:
        """
        Dispatch a request to the matching handler.

        Parameters
        ----------
        path : str
            Full path (including prefix).
        method : str
        payload : dict | None

        Returns
        -------
        APIResponse
        """
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
        self.register_route("/matrix/rank", "GET", self._matrix_rank_handler)
        self.register_route("/classify", "POST", self._classify_handler)
        self.register_route("/ingest", "POST", self._ingest_handler)

    # ------------------------------------------------------------------
    # Default handlers (stubs — wire to real services in production)
    # ------------------------------------------------------------------

    def _health_handler(self) -> APIResponse:
        return APIResponse(status="ok", data={"service": "learning_api", "healthy": True})

    def _matrix_rank_handler(self) -> APIResponse:
        return APIResponse(status="ok", data={"rankings": [], "message": "Connect to LearningMatrix for real data."})

    def _classify_handler(self, payload: Optional[Dict]) -> APIResponse:
        text = (payload or {}).get("text", "")
        return APIResponse(status="ok", data={"text": text, "category": "unknown", "message": "Connect to MethodClassifier."})

    def _ingest_handler(self, payload: Optional[Dict]) -> APIResponse:
        query = (payload or {}).get("query", "")
        return APIResponse(status="ok", data={"query": query, "ingested": 0, "message": "Connect to PaperScraper."})
