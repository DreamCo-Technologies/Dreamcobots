"""
APIBot FastAPI application — REST API for the autonomous API intelligence system.

Endpoints:
  POST   /api-bot/register                 — register an API endpoint
  POST   /api-bot/study-all                — study all bot APIs
  POST   /api-bot/test/{api_id}            — run sandbox test suite
  POST   /api-bot/inject-webhooks          — inject webhooks into all bots (dry-run)
  POST   /api-bot/inject-webhooks/apply    — inject webhooks (write mode)
  GET    /api-bot/apis                     — list all registered APIs
  GET    /api-bot/health/{api_id}          — API health check
  GET    /api-bot/summary                  — overall summary
  GET    /api-bot/top-apis                 — most-used APIs across ecosystem

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False
    class BaseModel:  # type: ignore
        def __init__(self, **data: Any) -> None:
            self.__dict__.update(data)

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW
from .api_bot import APIBot, KNOWN_API_PATTERNS
from .api_studier import APIStudier
from .sandbox_tester import APISandboxTester
from .webhook_injector import APIWebhookInjector

_api_bot = APIBot()
_studier = APIStudier()
_tester = APISandboxTester()


def create_app() -> Any:
    if not _HAS_FASTAPI:
        raise RuntimeError("Install fastapi: pip install fastapi pydantic")

    app = FastAPI(
        title="DreamCo APIBot",
        description="Autonomous API intelligence for 1,254 DreamCo bots",
        version="1.0.0",
    )

    class RegisterAPIRequest(BaseModel):
        bot_id: str
        name: str
        base_url: str
        auth_type: str = "bearer"
        rate_limit_rpm: int = 60

    class RegisterFromPatternRequest(BaseModel):
        bot_id: str
        patterns: List[str]

    @app.post("/api-bot/register", tags=["APIs"])
    def register_api(req: RegisterAPIRequest) -> Dict[str, Any]:
        ep = _api_bot.register_api(
            req.bot_id, req.name, req.base_url, req.auth_type, req.rate_limit_rpm
        )
        return ep.to_dict()

    @app.post("/api-bot/register-pattern", tags=["APIs"])
    def register_from_pattern(req: RegisterFromPatternRequest) -> List[Dict[str, Any]]:
        eps = _api_bot.register_from_known_patterns(req.bot_id, req.patterns)
        return [ep.to_dict() for ep in eps]

    @app.post("/api-bot/study-all", tags=["Intelligence"])
    def study_all() -> Dict[str, Any]:
        return _studier.study_all_bots()

    @app.get("/api-bot/top-apis", tags=["Intelligence"])
    def top_apis(top_n: int = 10) -> List[Dict[str, Any]]:
        return _studier.get_most_used_apis(top_n)

    @app.post("/api-bot/test/{api_id}", tags=["Sandbox"])
    def run_sandbox_test(api_id: str) -> Dict[str, Any]:
        ep = _api_bot._apis.get(api_id)
        if not ep:
            raise HTTPException(status_code=404, detail=f"API {api_id!r} not registered")
        return _tester.run_full_suite(ep)

    @app.post("/api-bot/inject-webhooks", tags=["Webhooks"])
    def inject_webhooks_dry_run() -> Dict[str, Any]:
        injector = APIWebhookInjector(dry_run=True)
        return injector.inject_all()

    @app.post("/api-bot/inject-webhooks/apply", tags=["Webhooks"])
    def inject_webhooks_apply() -> Dict[str, Any]:
        injector = APIWebhookInjector(dry_run=False)
        return injector.inject_all()

    @app.get("/api-bot/apis", tags=["APIs"])
    def list_apis() -> List[Dict[str, Any]]:
        return _api_bot.get_all_apis()

    @app.get("/api-bot/health/{api_id}", tags=["Observability"])
    def api_health(api_id: str) -> Dict[str, Any]:
        try:
            return _api_bot.check_api_health(api_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.get("/api-bot/summary", tags=["Observability"])
    def summary() -> Dict[str, Any]:
        return _api_bot.get_summary()

    @app.get("/api-bot/known-patterns", tags=["Intelligence"])
    def known_patterns() -> Dict[str, Any]:
        return KNOWN_API_PATTERNS

    return app


if _HAS_FASTAPI:
    app = create_app()
