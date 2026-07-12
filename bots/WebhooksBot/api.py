"""
WebhooksBot FastAPI application — REST API for webhook management.

Endpoints:
  POST   /webhooks/register                — register a new subscription
  DELETE /webhooks/{subscription_id}       — deregister subscription
  GET    /webhooks                         — list all subscriptions
  POST   /webhooks/trigger                 — trigger an event
  POST   /webhooks/bulk-register           — auto-register all bots
  POST   /webhooks/validate/{sub_id}       — sandbox validate subscription
  GET    /webhooks/health                  — health summary
  GET    /webhooks/dead-letter             — dead-letter queue

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, HttpUrl
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False
    class BaseModel:  # type: ignore
        def __init__(self, **data: Any) -> None:
            self.__dict__.update(data)

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW
from .webhook_bot import WebhooksBot, WebhookEventType
from .registry import WebhookBotRegistry
from .health import WebhookHealthMonitor

_webhooks_bot = WebhooksBot()
_registry = WebhookBotRegistry(_webhooks_bot)
_monitor = WebhookHealthMonitor(_webhooks_bot)


def create_app() -> Any:
    """Build and return the FastAPI application for WebhooksBot."""
    if not _HAS_FASTAPI:
        raise RuntimeError("Install fastapi and pydantic: pip install fastapi pydantic")

    app = FastAPI(
        title="DreamCo WebhooksBot API",
        description="Universal webhook management for all 1,254 DreamCo bots",
        version="2.0.0",
    )

    class RegisterRequest(BaseModel):
        bot_id: str
        url: str
        events: List[str]
        secret: Optional[str] = None

    class TriggerRequest(BaseModel):
        event_type: str
        payload: Dict[str, Any] = {}
        bot_id: Optional[str] = None

    class BulkRegisterRequest(BaseModel):
        base_url_template: str = "https://hooks.dreamco.io/bots/{bot_id}"
        sandbox_validate: bool = False

    @app.post("/webhooks/register", tags=["Subscriptions"])
    def register_webhook(req: RegisterRequest) -> Dict[str, Any]:
        try:
            events = [WebhookEventType(e) for e in req.events]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        sub = _webhooks_bot.register(req.bot_id, req.url, events, req.secret or "")
        return sub.to_dict()

    @app.delete("/webhooks/{subscription_id}", tags=["Subscriptions"])
    def deregister_webhook(subscription_id: str) -> Dict[str, Any]:
        ok = _webhooks_bot.deregister(subscription_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return {"deleted": subscription_id}

    @app.get("/webhooks", tags=["Subscriptions"])
    def list_webhooks(bot_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return _webhooks_bot.get_subscriptions(bot_id)

    @app.post("/webhooks/trigger", tags=["Events"])
    def trigger_event(req: TriggerRequest) -> List[Dict[str, Any]]:
        try:
            event_type = WebhookEventType(req.event_type)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return _webhooks_bot.trigger_sync(event_type, req.payload, req.bot_id)

    @app.post("/webhooks/bulk-register", tags=["Management"])
    def bulk_register(req: BulkRegisterRequest) -> Dict[str, Any]:
        subs = _registry.register_all(req.base_url_template, sandbox_validate=req.sandbox_validate)
        return {"registered": len(subs), "summary": _registry.get_summary()}

    @app.post("/webhooks/validate/{subscription_id}", tags=["Management"])
    def sandbox_validate(subscription_id: str) -> Dict[str, Any]:
        try:
            return _webhooks_bot.sandbox_validate(subscription_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.get("/webhooks/health", tags=["Observability"])
    def health_check() -> Dict[str, Any]:
        return _monitor.check()

    @app.get("/webhooks/dead-letter", tags=["Observability"])
    def dead_letter() -> List[Dict[str, Any]]:
        return _webhooks_bot._engine.get_dead_letter()

    return app


if _HAS_FASTAPI:
    app = create_app()
