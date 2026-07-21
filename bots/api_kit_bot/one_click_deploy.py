"""
One-Click Deploy — automated deployment engine for the DreamCo API Kit Bot.

Supports deploying API kits to AWS Lambda, Google Cloud Run, Azure Functions,
Heroku, Vercel, Railway, and Docker with simulated lifecycle management.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import random
import uuid
from datetime import datetime, timezone

from framework import GlobalAISourcesFlow  # noqa: F401

# ---------------------------------------------------------------------------
# Deploy targets
# ---------------------------------------------------------------------------

AWS_LAMBDA = "aws_lambda"
GOOGLE_CLOUD_RUN = "google_cloud_run"
AZURE_FUNCTIONS = "azure_functions"
HEROKU = "heroku"
VERCEL = "vercel"
RAILWAY = "railway"
DOCKER = "docker"

DEPLOY_TARGETS: list = [
    AWS_LAMBDA,
    GOOGLE_CLOUD_RUN,
    AZURE_FUNCTIONS,
    HEROKU,
    VERCEL,
    RAILWAY,
    DOCKER,
]

_TARGET_BASE_URLS: dict = {
    AWS_LAMBDA: "https://{id}.execute-api.us-east-1.amazonaws.com/prod",
    GOOGLE_CLOUD_RUN: "https://{id}-uc.a.run.app",
    AZURE_FUNCTIONS: "https://{id}.azurewebsites.net/api",
    HEROKU: "https://{id}.herokuapp.com",
    VERCEL: "https://{id}.vercel.app",
    RAILWAY: "https://{id}.up.railway.app",
    DOCKER: "http://localhost:8080/{id}",
}

_TARGET_READY_SECONDS: dict = {
    AWS_LAMBDA: 45,
    GOOGLE_CLOUD_RUN: 60,
    AZURE_FUNCTIONS: 75,
    HEROKU: 90,
    VERCEL: 30,
    RAILWAY: 35,
    DOCKER: 20,
}


class OneClickDeploy:
    """Deploy API kits to cloud targets with one call."""

    def __init__(self) -> None:
        self._deployments: dict = {}

    def deploy_kit(
        self,
        kit_id: str,
        owner_id: str,
        target: str,
        config: dict | None = None,
    ) -> dict:
        """Initiate a deployment of *kit_id* to *target*.

        Returns a deployment record with status DEPLOYING and an estimated
        ready time in seconds.
        """
        if target not in DEPLOY_TARGETS:
            return {"error": f"Unknown deploy target '{target}'. Choose from {DEPLOY_TARGETS}."}

        deployment_id = f"dep_{uuid.uuid4().hex[:12]}"
        short_id = deployment_id.replace("dep_", "")
        endpoint_url = _TARGET_BASE_URLS[target].format(id=short_id)
        estimated_seconds = _TARGET_READY_SECONDS.get(target, 60)

        record = {
            "deployment_id": deployment_id,
            "kit_id": kit_id,
            "owner_id": owner_id,
            "target": target,
            "status": "DEPLOYING",
            "endpoint_url": endpoint_url,
            "estimated_ready_seconds": estimated_seconds,
            "config": config or {},
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "live_at": None,
            "previous_endpoint_url": None,
            "uptime_pct": None,
            "requests_total": 0,
            "p99_latency_ms": None,
            "cost_usd_monthly": None,
        }
        self._deployments[deployment_id] = record
        return {
            k: v
            for k, v in record.items()
            if k not in ("uptime_pct", "requests_total", "p99_latency_ms", "cost_usd_monthly", "previous_endpoint_url")
        }

    def get_deployment(self, deployment_id: str) -> dict:
        """Return deployment details."""
        record = self._deployments.get(deployment_id)
        if record is None:
            return {"error": f"Deployment '{deployment_id}' not found."}
        return {k: v for k, v in record.items() if k not in ("previous_endpoint_url",)}

    def list_deployments(self, owner_id: str) -> list:
        """Return all deployments owned by *owner_id*."""
        return [
            {k: v for k, v in rec.items() if k not in ("previous_endpoint_url",)}
            for rec in self._deployments.values()
            if rec["owner_id"] == owner_id
        ]

    def simulate_deployment_ready(self, deployment_id: str) -> dict:
        """Simulate a deployment becoming LIVE (for testing/demos)."""
        record = self._deployments.get(deployment_id)
        if record is None:
            return {"error": f"Deployment '{deployment_id}' not found."}
        record["status"] = "LIVE"
        record["live_at"] = datetime.now(tz=timezone.utc).isoformat()
        record["uptime_pct"] = 100.0
        record["requests_total"] = 0
        record["p99_latency_ms"] = random.randint(80, 300)
        record["cost_usd_monthly"] = round(random.uniform(5.0, 50.0), 2)
        return {
            "deployment_id": deployment_id,
            "status": "LIVE",
            "endpoint_url": record["endpoint_url"],
            "live_at": record["live_at"],
        }

    def get_deployment_metrics(self, deployment_id: str) -> dict:
        """Return runtime metrics for a deployment."""
        record = self._deployments.get(deployment_id)
        if record is None:
            return {"error": f"Deployment '{deployment_id}' not found."}
        if record["status"] != "LIVE":
            return {
                "deployment_id": deployment_id,
                "status": record["status"],
                "metrics": "Not available until deployment is LIVE.",
            }
        return {
            "deployment_id": deployment_id,
            "uptime_pct": record.get("uptime_pct", 100.0),
            "requests_total": record.get("requests_total", 0),
            "p99_latency_ms": record.get("p99_latency_ms"),
            "cost_usd_monthly": record.get("cost_usd_monthly"),
        }

    def rollback_deployment(self, deployment_id: str) -> dict:
        """Roll back a deployment to its previous endpoint URL."""
        record = self._deployments.get(deployment_id)
        if record is None:
            return {"error": f"Deployment '{deployment_id}' not found."}

        previous = record.get("previous_endpoint_url")
        current = record["endpoint_url"]

        if previous:
            record["previous_endpoint_url"] = current
            record["endpoint_url"] = previous
            record["status"] = "ROLLED_BACK"
        else:
            record["status"] = "ROLLED_BACK"

        return {
            "deployment_id": deployment_id,
            "status": record["status"],
            "endpoint_url": record["endpoint_url"],
            "rolled_back": True,
        }
