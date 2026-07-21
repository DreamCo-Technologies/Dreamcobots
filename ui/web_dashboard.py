"""
DreamCo Web Dashboard — Flask-based centralized control interface.

Provides a real-time web UI to:
  - Monitor bot activity, performance logs, and revenue.
  - Enable manual bot creation, management, and overrides.
  - Visualize system behavior via REST endpoints consumed by a browser.
  - Launch high-revenue bots live via Go Live buttons.
  - Display live GitHub Actions workflow runs and artifacts (read-only).
  - Show Quantum Bot system health.
  - Control bot governance (aggressiveness, execution duration, retry policy).
  - View per-bot dashboard pages with runtime parameters.
  - Detect and report uncoded / stub bots.
  - Track and display failures and merge conflicts.

Usage
-----
    from ui.web_dashboard import create_app

    app = create_app()
    app.run(debug=True, port=5050)

Endpoints
---------
  GET  /                              — Dashboard HTML landing page
  GET  /dashboard/chooser             — Dashboard chooser and side-by-side comparison
  GET  /bots/<name>                   — Per-bot HTML dashboard page
  GET  /api/status                    — System-wide status JSON
  GET  /api/bots                      — Registered bot list with KPI scores
  POST /api/bots/register             — Register a new bot { "name": "...", "tier": "..." }
  POST /api/bots/<name>/go_live       — Deploy / activate a bot instance
  POST /api/bots/<name>/configure     — Configure bot runtime parameters
  GET  /api/bots/<name>/config        — Retrieve bot runtime parameters
  GET  /api/bots/catalog              — Full bot catalog with Go Live status
  GET  /api/bots/uncoded              — Uncoded / stub bots report
  GET  /api/revenue                   — Revenue summary JSON
  GET  /api/leaderboard               — Bot leaderboard (top by composite KPI)
  GET  /api/underperformers           — Bots with composite score < threshold
  POST /api/record_run                — Record a bot run with KPIs
  GET  /api/history/<bot_name>        — Run history for a specific bot
  GET  /api/governance                — Current global governance settings
  POST /api/governance/settings       — Update global governance settings
  GET  /api/failures                  — Recent failure and conflict log
  POST /api/failures/report           — Append an entry to the failure log
  GET  /api/github/workflows          — Live GitHub Actions workflow runs (read-only)
  GET  /api/github/artifacts          — GitHub Actions artifact list (read-only)
  GET  /api/quantum/status            — Quantum Bot system health check
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

try:
    from flask import Flask, jsonify, request, Response
    _FLASK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FLASK_AVAILABLE = False

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _requests = None  # type: ignore[assignment]
    _REQUESTS_AVAILABLE = False

import re as _re
import threading as _threading

from bots.ai_learning_system.database import BotPerformanceDB
from bots.control_center.control_center import ControlCenter
from dreamco_platform import PLATFORM_VERSION
from dreamco_platform.registry.bot_registry import (
    BotRegistry,
    BotRegistryEntry,
    HealthStatus,
)


# ---------------------------------------------------------------------------
# GitHub Actions helpers (read-only)
# ---------------------------------------------------------------------------

_GITHUB_API_BASE = "https://api.github.com"
_DEFAULT_REPO = "DreamCo-Technologies/Dreamcobots"

# Clamp per_page to this range for GitHub API requests
_GITHUB_PER_PAGE_MIN = 1
_GITHUB_PER_PAGE_MAX = 100

# Cached QuantumAIBot check result (reset on each process start)
_quantum_cache: dict = {}
_QUANTUM_CACHE_TTL_S = 60


# ---------------------------------------------------------------------------
# Global governance state (process-local, in-memory)
# ---------------------------------------------------------------------------

_GOVERNANCE_LOCK = _threading.Lock()
_GOVERNANCE_SETTINGS: dict = {
    "aggressiveness": "balanced",
    "max_execution_seconds": 300,
    "retry_policy": "auto",
    "updated_at": None,
}

# Valid values for governance fields
_VALID_AGGRESSIVENESS = {"passive", "balanced", "aggressive", "max"}
_VALID_RETRY_POLICY = {"none", "once", "twice", "auto"}

# ---------------------------------------------------------------------------
# Per-bot runtime configuration (process-local, in-memory)
# ---------------------------------------------------------------------------

_BOT_CONFIG_LOCK = _threading.Lock()
_BOT_CONFIGS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Failure / conflict log (process-local, capped)
# ---------------------------------------------------------------------------

_FAILURE_LOG_LOCK = _threading.Lock()
_FAILURE_LOG: list[dict] = []
_FAILURE_LOG_MAX = 200

# Stub / TODO detection patterns
_STUB_PATTERN = _re.compile(
    r"raise\s+NotImplementedError|#\s*TODO|#\s*FIXME|#\s*STUB|#\s*PLACEHOLDER",
    _re.IGNORECASE,
)


def _github_headers() -> dict:
    """Return HTTP headers for GitHub API calls, including auth if available."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_github_workflows(repo: str = _DEFAULT_REPO, per_page: int = 10) -> dict:
    """Fetch the most recent GitHub Actions workflow runs for *repo*.

    Returns a dict with ``runs`` (list) and ``source`` (``"github_api"`` or
    ``"unavailable"``).  Never raises — failures produce a safe placeholder
    payload so the dashboard always renders.
    """
    if not _REQUESTS_AVAILABLE:
        return {"runs": [], "source": "unavailable", "reason": "requests library not installed"}

    per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, per_page))
    url = f"{_GITHUB_API_BASE}/repos/{repo}/actions/runs"
    try:
        resp = _requests.get(
            url,
            headers=_github_headers(),
            params={"per_page": per_page},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            runs = [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "workflow_id": r.get("workflow_id"),
                    "status": r["status"],
                    "conclusion": r.get("conclusion"),
                    "branch": r.get("head_branch"),
                    "event": r.get("event"),
                    "run_started_at": r.get("run_started_at"),
                    "updated_at": r.get("updated_at"),
                    "url": r.get("html_url"),
                }
                for r in data.get("workflow_runs", [])
            ]
            return {"runs": runs, "total_count": data.get("total_count", len(runs)), "source": "github_api"}
        return {
            "runs": [],
            "source": "unavailable",
            "reason": f"GitHub API returned HTTP {resp.status_code}",
        }
    except Exception:  # noqa: BLE001
        return {"runs": [], "source": "unavailable", "reason": "GitHub API request failed"}


def _fetch_github_artifacts(repo: str = _DEFAULT_REPO, per_page: int = 10) -> dict:
    """Fetch the most recent GitHub Actions artifacts for *repo*.

    Returns a dict with ``artifacts`` (list) and ``source``.  Never raises.
    """
    if not _REQUESTS_AVAILABLE:
        return {"artifacts": [], "source": "unavailable", "reason": "requests library not installed"}

    per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, per_page))
    url = f"{_GITHUB_API_BASE}/repos/{repo}/actions/artifacts"
    try:
        resp = _requests.get(
            url,
            headers=_github_headers(),
            params={"per_page": per_page},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            artifacts = [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "size_in_bytes": a.get("size_in_bytes", 0),
                    "created_at": a.get("created_at"),
                    "expires_at": a.get("expires_at"),
                    "expired": a.get("expired", False),
                    "url": a.get("url"),
                }
                for a in data.get("artifacts", [])
            ]
            return {"artifacts": artifacts, "total_count": data.get("total_count", len(artifacts)), "source": "github_api"}
        return {
            "artifacts": [],
            "source": "unavailable",
            "reason": f"GitHub API returned HTTP {resp.status_code}",
        }
    except Exception:  # noqa: BLE001
        return {"artifacts": [], "source": "unavailable", "reason": "GitHub API request failed"}


def _check_quantum_bot_status() -> dict:
    """Return a cached Quantum Bot health summary (read-only).

    Instantiates QuantumAIBot (FREE tier) at most once per
    ``_QUANTUM_CACHE_TTL_S`` seconds to avoid expensive repeated
    construction on every request.  Never raises.
    """
    global _quantum_cache  # noqa: PLW0603
    import time as _time

    now = _time.monotonic()
    if _quantum_cache and now - _quantum_cache.get("_cached_at", 0) < _QUANTUM_CACHE_TTL_S:
        result = {k: v for k, v in _quantum_cache.items() if not k.startswith("_")}
        result["checked_at"] = datetime.now(timezone.utc).isoformat()
        return result

    try:
        _ai_models_dir = os.path.join(os.path.dirname(__file__), "..", "bots", "ai-models-integration")
        import sys as _sys  # noqa: PLC0415
        if _ai_models_dir not in _sys.path:
            _sys.path.insert(0, _ai_models_dir)

        from bots.quantum_ai_bot.quantum_ai_bot import QuantumAIBot  # noqa: PLC0415
        from bots.ai_learning_system.tiers import Tier  # noqa: PLC0415

        bot = QuantumAIBot(tier=Tier.FREE)
        result = {
            "status": "ok",
            "bot": "QuantumAIBot",
            "tier": bot.tier.value,
            "engines": [
                "QuantumCircuitSimulator",
                "HybridQuantumAIModel",
                "QuantumOptimizer",
                "QuantumPartnershipManager",
            ],
        }
    except Exception:  # noqa: BLE001
        result = {
            "status": "error",
            "bot": "QuantumAIBot",
            "reason": "Quantum Bot health check failed",
        }

    _quantum_cache = {**result, "_cached_at": now}
    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    return result


def _get_governance() -> dict:
    """Return a copy of the current global governance settings."""
    with _GOVERNANCE_LOCK:
        return dict(_GOVERNANCE_SETTINGS)


def _update_governance(aggressiveness: str | None = None,
                       max_execution_seconds: int | None = None,
                       retry_policy: str | None = None) -> dict:
    """Update global governance settings and return the new state.

    Ignores invalid values and keeps the previous setting instead.
    """
    with _GOVERNANCE_LOCK:
        if aggressiveness is not None and aggressiveness in _VALID_AGGRESSIVENESS:
            _GOVERNANCE_SETTINGS["aggressiveness"] = aggressiveness
        if max_execution_seconds is not None:
            clamped = max(30, min(3600, int(max_execution_seconds)))
            _GOVERNANCE_SETTINGS["max_execution_seconds"] = clamped
        if retry_policy is not None and retry_policy in _VALID_RETRY_POLICY:
            _GOVERNANCE_SETTINGS["retry_policy"] = retry_policy
        _GOVERNANCE_SETTINGS["updated_at"] = datetime.now(timezone.utc).isoformat()
        return dict(_GOVERNANCE_SETTINGS)


def _get_bot_config(bot_name: str) -> dict:
    """Return the runtime config for *bot_name*, falling back to governance defaults."""
    gov = _get_governance()
    with _BOT_CONFIG_LOCK:
        cfg = dict(_BOT_CONFIGS.get(bot_name, {}))
    return {
        "bot_name": bot_name,
        "aggressiveness": cfg.get("aggressiveness", gov["aggressiveness"]),
        "max_execution_seconds": cfg.get("max_execution_seconds", gov["max_execution_seconds"]),
        "retry_policy": cfg.get("retry_policy", gov["retry_policy"]),
        "custom": bool(cfg),
        "updated_at": cfg.get("updated_at"),
    }


def _set_bot_config(bot_name: str, **kwargs: object) -> dict:
    """Persist per-bot runtime config overrides. Returns the merged config."""
    with _BOT_CONFIG_LOCK:
        existing = dict(_BOT_CONFIGS.get(bot_name, {}))
        if "aggressiveness" in kwargs and kwargs["aggressiveness"] in _VALID_AGGRESSIVENESS:
            existing["aggressiveness"] = kwargs["aggressiveness"]
        if "max_execution_seconds" in kwargs:
            try:
                clamped = max(30, min(3600, int(kwargs["max_execution_seconds"])))  # type: ignore[arg-type]
                existing["max_execution_seconds"] = clamped
            except (TypeError, ValueError):
                pass
        if "retry_policy" in kwargs and kwargs["retry_policy"] in _VALID_RETRY_POLICY:
            existing["retry_policy"] = kwargs["retry_policy"]
        existing["updated_at"] = datetime.now(timezone.utc).isoformat()
        _BOT_CONFIGS[bot_name] = existing
    return _get_bot_config(bot_name)


def _append_failure(bot_name: str, failure_type: str, message: str, details: dict | None = None) -> dict:
    """Append a failure entry to the in-memory log (capped at _FAILURE_LOG_MAX)."""
    entry: dict = {
        "bot_name": bot_name,
        "failure_type": failure_type,
        "message": message,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _FAILURE_LOG_LOCK:
        _FAILURE_LOG.append(entry)
        while len(_FAILURE_LOG) > _FAILURE_LOG_MAX:
            _FAILURE_LOG.pop(0)
    return entry


def _get_failures(bot_name: str | None = None, limit: int = 50) -> list[dict]:
    """Return recent failures, optionally filtered by *bot_name*."""
    with _FAILURE_LOG_LOCK:
        log = list(_FAILURE_LOG)
    if bot_name:
        log = [e for e in log if e["bot_name"] == bot_name]
    return log[-limit:]


def _detect_uncoded_bots() -> dict:
    """Scan the *bots/* directory for uncoded and stub bots.

    An *uncoded* bot directory has Python files but none define a ``run()``
    method.  A *stub* bot directory has files containing TODO / FIXME /
    NotImplementedError markers.

    Returns a dict with ``uncoded`` and ``stubbed`` lists.  Never raises.
    """
    bots_root = os.path.join(os.path.dirname(__file__), "..", "bots")
    uncoded: list[str] = []
    stubbed: list[dict] = []

    try:
        for dirpath, dirnames, filenames in os.walk(bots_root):
            dirnames[:] = [d for d in dirnames if not d.startswith((".", "__"))]
            py_files = [f for f in filenames if f.endswith(".py")]
            if not py_files:
                continue
            has_run = False
            stub_hints: list[str] = []
            for fname in py_files:
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, encoding="utf-8", errors="replace") as _f:
                        content = _f.read()
                except OSError:
                    continue
                if _re.search(r"def run\(", content):
                    has_run = True
                for lineno, line in enumerate(content.splitlines(), 1):
                    if _STUB_PATTERN.search(line):
                        stub_hints.append(f"{os.path.relpath(fpath, bots_root)}:{lineno}")
            rel = os.path.relpath(dirpath, bots_root)
            if not has_run:
                uncoded.append(rel)
            if stub_hints:
                stubbed.append({"path": rel, "hints": stub_hints[:5]})
    except Exception:  # noqa: BLE001
        pass

    return {
        "uncoded_count": len(uncoded),
        "stubbed_count": len(stubbed),
        "uncoded": uncoded,
        "stubbed": stubbed,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Bot catalog — all high-revenue bots available for Go Live deployment
# ---------------------------------------------------------------------------

_BOT_CATALOG: list[dict] = [
    {
        "name": "multi_source_lead_scraper",
        "display_name": "Lead Generator Bot",
        "emoji": "🎯",
        "description": "Scrapes qualified leads from Google, LinkedIn, Twitter, Reddit & Yelp. AI-scored, CRM-exportable.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Sales & Marketing",
        "priority": 1,
    },
    {
        "name": "real_estate_bot",
        "display_name": "Real Estate Finder Bot",
        "emoji": "🏠",
        "description": "Finds investment properties, calculates cap rates, cash flow, and ROI across 10 US cities.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Real Estate",
        "priority": 2,
    },
    {
        "name": "ai_side_hustle_bot",
        "display_name": "AI Hustle Generator",
        "emoji": "💰",
        "description": "Identifies, launches, and monetizes side hustles with AI-powered content, income calculators & marketing plans.",
        "revenue_model": "$29–$99/mo subscription",
        "category": "Entrepreneurship",
        "priority": 3,
    },
    {
        "name": "stripe_payment_bot",
        "display_name": "Stripe Payment Bot",
        "emoji": "💳",
        "description": "Full Stripe integration: checkouts, subscriptions, invoices, webhooks, fraud detection & Connect.",
        "revenue_model": "2.2–2.9% transaction fee + $29–$299/mo",
        "category": "Payments",
        "priority": 4,
    },
    {
        "name": "fiverr_bot",
        "display_name": "Fiverr Automation Bot",
        "emoji": "🎨",
        "description": "Automates Fiverr gig creation, order management, client communication, and upselling.",
        "revenue_model": "$29–$99/mo subscription",
        "category": "Freelance",
        "priority": 5,
    },
    {
        "name": "crypto_bot",
        "display_name": "Crypto Trading Bot",
        "emoji": "₿",
        "description": "Algorithmic crypto portfolio management, price alerts, and auto-trading strategies.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Finance",
        "priority": 6,
    },
    {
        "name": "open_claw_bot",
        "display_name": "Client Acquisition Bot",
        "emoji": "🤝",
        "description": "Automates client outreach, proposal generation, and deal closing across multiple channels.",
        "revenue_model": "$99–$299/mo subscription",
        "category": "Sales",
        "priority": 7,
    },
    {
        "name": "affiliate_bot",
        "display_name": "Affiliate Marketing Bot",
        "emoji": "🔗",
        "description": "Manages affiliate programs, tracks commissions, and automates partner payouts.",
        "revenue_model": "$29–$99/mo + commission share",
        "category": "Marketing",
        "priority": 8,
    },
    {
        "name": "ai_chatbot",
        "display_name": "AI Customer Support Bot",
        "emoji": "💬",
        "description": "GPT-powered customer support with tier-based conversation limits and CRM integration.",
        "revenue_model": "$29–$299/mo subscription",
        "category": "Customer Service",
        "priority": 9,
    },
    {
        "name": "deal_finder_bot",
        "display_name": "Deal Finder Bot",
        "emoji": "🔍",
        "description": "Scans marketplaces for arbitrage opportunities and profit-generating deals.",
        "revenue_model": "$29–$99/mo subscription",
        "category": "E-Commerce",
        "priority": 10,
    },
]


# ---------------------------------------------------------------------------
# Runtime intelligence manifest helpers
# ---------------------------------------------------------------------------

def _estimate_monthly_revenue(revenue_model: str) -> float:
    matches = [float(value) for value in _re.findall(r"\$([0-9]+(?:\.[0-9]+)?)", revenue_model)]
    if not matches:
        return 0.0
    if len(matches) == 1:
        return round(matches[0], 2)
    return round(sum(matches) / len(matches), 2)


def _derive_capabilities(bot_name: str, category: str) -> list[str]:
    tokens = [part for part in bot_name.split("_") if part and part != "bot"]
    capabilities = [f"{category.lower().replace(' & ', '_').replace(' ', '_')}.{token}" for token in tokens[:3]]
    capabilities.extend(
        capability
        for capability in (
            "runtime.observe",
            "memory.recall",
            "economics.attribute_revenue",
        )
        if capability not in capabilities
    )
    return capabilities


def _normalize_bot_id(bot_name: str) -> str:
    normalized = _re.sub(r"[^a-z0-9_]+", "_", bot_name.lower()).strip("_")
    if not normalized or not normalized[0].isalpha():
        normalized = f"bot_{normalized or 'worker'}"
    return normalized


def _infer_swarm_role(category: str, bot_name: str) -> str:
    normalized = f"{category} {bot_name}".lower()
    if "buddy" in normalized:
        return "observer_modulator"
    if any(token in normalized for token in ("sales", "marketing", "lead", "client")):
        return "negotiator"
    if any(token in normalized for token in ("finance", "payment", "revenue", "crypto")):
        return "economic_optimizer"
    if any(token in normalized for token in ("support", "service", "chat")):
        return "coordinator"
    return "specialist"


def _infer_memory_nodes(bot_name: str, category: str, is_live: bool) -> list[str]:
    prefix = bot_name.replace("-", "_")
    nodes = [
        f"identity.{prefix}",
        f"trust.{prefix}",
        f"specialization.{category.lower().replace(' ', '_')}",
    ]
    if is_live:
        nodes.append(f"runtime.{prefix}.active")
    return nodes


def _infer_permissions(bot_name: str, is_live: bool) -> list[str]:
    permissions = ["observe:runtime", "read:memory", f"claim:{bot_name}"]
    if is_live:
        permissions.extend(["emit:events", "write:memory"])
    return permissions


def _build_runtime_manifest_entry(
    *,
    bot_name: str,
    display_name: str,
    category: str,
    description: str,
    revenue_model: str,
    is_live: bool,
    realized_revenue: float = 0.0,
    composite_score: float = 0.0,
    total_runs: int = 0,
) -> BotRegistryEntry:
    trust_score = min(1.0, max(0.05, composite_score / 100 if composite_score else (0.82 if is_live else 0.58)))
    return BotRegistryEntry(
        bot_id=_normalize_bot_id(bot_name),
        display_name=display_name,
        capabilities=_derive_capabilities(bot_name, category),
        events_emitted=["bot.started", "bot.completed", "governance.reviewed"],
        events_consumed=["workflow.started", "runtime.directive", "swarm.negotiation"],
        pricing_tier="pro" if is_live else "free",
        runtime_requirements={"runtime": "persistent", "control_surface": "dashboard"},
        dependencies=["dreamco_platform.events.EventBus", "dreamco_platform.memory.WorkflowMemory"],
        health=HealthStatus.HEALTHY if is_live else HealthStatus.UNKNOWN,
        learning_enabled=True,
        description=description,
        version="2.0.0",
        category=category,
        tags=["runtime-intelligence", "autonomous-economy", "swarm-ready"],
        lifecycle_state="active" if is_live else "idle",
        swarm_role=_infer_swarm_role(category, bot_name),
        memory_nodes=_infer_memory_nodes(bot_name, category, is_live),
        revenue_attribution={
            "mode": revenue_model or "simulation",
            "estimated_monthly_usd": _estimate_monthly_revenue(revenue_model),
            "realized_usd": round(realized_revenue, 2),
            "roi_score": round(composite_score, 2),
            "runs": total_runs,
        },
        permissions=_infer_permissions(bot_name, is_live),
        trust_score=trust_score,
        specialization=category,
        identity={
            "bot_name": display_name,
            "lineage": "dreamco_runtime",
            "progression": "live" if is_live else "catalogued",
        },
        metadata={
            "governance_mode": "bounded-autonomy",
            "sandbox": "standard",
            "dashboard_generated": True,
        },
    )


def _build_runtime_registry(cc: "ControlCenter", perf_db: BotPerformanceDB) -> BotRegistry:
    registry = BotRegistry()
    status = cc.get_status().get("bots", {})
    scores = {entry["bot_name"]: entry for entry in perf_db.get_all_scores()}
    income = cc.get_income_summary().get("by_source", {})

    registry.register(
        BotRegistryEntry(
            bot_id="buddy_ai",
            display_name="BuddyAI Runtime Governance Engine",
            capabilities=[
                "governance.observe",
                "governance.modulate",
                "runtime.synthesize",
                "swarm.coordinate",
            ],
            events_emitted=["governance.reviewed", "runtime.directive", "swarm.feedback"],
            events_consumed=["bot.started", "bot.completed", "workflow.started", "workflow.failed"],
            pricing_tier="enterprise",
            runtime_requirements={"runtime": "persistent", "mode": "decentralized"},
            dependencies=[
                "dreamco_platform.events.EventBus",
                "dreamco_platform.orchestration.ExecutionRuntime",
                "dreamco_platform.governance.PolicyEvaluator",
            ],
            health=HealthStatus.HEALTHY,
            learning_enabled=True,
            description="Observer, modulator, and runtime synthesizer for bounded distributed autonomy.",
            version="2.0.0",
            category="Governance",
            tags=["buddy", "governance", "runtime-intelligence"],
            lifecycle_state="active",
            swarm_role="observer_modulator",
            memory_nodes=["runtime.audit_fabric", "runtime.shared_memory", "identity.buddy_ai"],
            revenue_attribution={
                "mode": "platform-governance",
                "estimated_monthly_usd": 0.0,
                "realized_usd": round(sum(income.values()), 2),
                "roi_score": 100.0,
                "runs": sum(meta.get("run_count", 0) for meta in status.values()),
            },
            permissions=["observe:all", "modulate:governance", "synthesize:runtime", "quarantine:bot"],
            trust_score=0.99,
            specialization="Distributed governance",
            identity={"lineage": "dreamco_runtime", "progression": "persistent"},
            metadata={
                "decentralized": True,
                "bounded_governance": True,
                "shared_intelligence": True,
            },
        )
    )

    catalog_names = set()
    for bot in _BOT_CATALOG:
        catalog_names.add(bot["name"])
        score = scores.get(bot["name"], {})
        registry.register(
            _build_runtime_manifest_entry(
                bot_name=bot["name"],
                display_name=bot["display_name"],
                category=bot["category"],
                description=bot["description"],
                revenue_model=bot["revenue_model"],
                is_live=bot["name"] in status,
                realized_revenue=float(income.get(bot["name"], 0.0) or 0.0),
                composite_score=float(score.get("composite_score", 0.0) or 0.0),
                total_runs=int(score.get("total_runs", 0) or 0),
            )
        )

    for bot_name, meta in status.items():
        if bot_name in catalog_names:
            continue
        tier = meta.get("tier", "free")
        score = scores.get(bot_name, {})
        registry.register(
            _build_runtime_manifest_entry(
                bot_name=bot_name,
                display_name=bot_name.replace("_", " ").title(),
                category="Runtime Worker",
                description=f"Autonomous runtime worker on tier '{tier}'.",
                revenue_model="simulation",
                is_live=True,
                realized_revenue=float(income.get(bot_name, 0.0) or 0.0),
                composite_score=float(score.get("composite_score", 0.0) or 0.0),
                total_runs=int(meta.get("run_count", 0) or 0),
            )
        )

    return registry


def _build_runtime_overview(cc: "ControlCenter", perf_db: BotPerformanceDB) -> dict:
    registry = _build_runtime_registry(cc, perf_db)
    status = cc.get_monitoring_dashboard()
    stats = perf_db.get_stats()
    manifests = registry.all_manifests()
    realized_revenue = registry.revenue_summary()["realized_usd"]
    avg_trust = registry.average_trust_score()
    coordination_efficiency = round(min(100.0, max(0.0, stats["avg_composite_score"] or (avg_trust * 100))), 2)

    return {
        "schema": "dreamco_runtime_overview.v1",
        "platform_version": PLATFORM_VERSION,
        "summary": registry.manifest_summary(),
        "runtime_layers": [
            {
                "layer": "autonomous_runtime_core",
                "title": "Autonomous Runtime Core",
                "components": [
                    "persistent state layers",
                    "event buses",
                    "swarm coordination engines",
                    "memory fabrics",
                    "execution engines",
                    "lifecycle managers",
                ],
            },
            {
                "layer": "swarm_intelligence",
                "title": "Swarm Intelligence",
                "components": [
                    "task claiming",
                    "fitness propagation",
                    "negotiation loops",
                    "PSO / ACO / MARL strategy hooks",
                ],
            },
            {
                "layer": "governance_safety",
                "title": "Governance & Safety",
                "components": [
                    "policy enforcement",
                    "sandboxing",
                    "quarantining",
                    "trust scoring",
                    "anomaly review",
                ],
            },
            {
                "layer": "interface_layer",
                "title": "Interface Layer",
                "components": [
                    "mission control dashboards",
                    "runtime prospectus pages",
                    "governance controls",
                    "economic monitoring",
                ],
            },
        ],
        "buddy_ai": registry.get("buddy_ai").to_dict() if registry.get("buddy_ai") else None,
        "metrics": {
            "manifested_bots": len(manifests),
            "registered_bots": status["registered_bots"],
            "coordination_efficiency": coordination_efficiency,
            "avg_trust_score": round(avg_trust, 4),
            "estimated_monthly_revenue_usd": registry.revenue_summary()["estimated_monthly_usd"],
            "realized_revenue_usd": realized_revenue,
            "roi_attribution": round(realized_revenue / max(1, len(manifests)), 2),
        },
    }


def super_dashboard_runtime_snapshot(
    control_center: Optional["ControlCenter"] = None,
    db: Optional[BotPerformanceDB] = None,
) -> dict:
    """Return compact runtime metrics for dashboards.super_dashboard."""
    cc = control_center or ControlCenter()
    perf_db = db or BotPerformanceDB()
    overview = _build_runtime_overview(cc, perf_db)
    summary = overview.get("summary", {})
    metrics = overview.get("metrics", {})
    governance = _get_governance()
    return {
        "catalog_total": int(summary.get("total", 0)),
        "live_bots": int(summary.get("live", 0)),
        "degraded_bots": int(summary.get("degraded", 0)),
        "coordination_efficiency": float(metrics.get("coordination_efficiency", 0.0)),
        "realized_revenue_usd": float(metrics.get("realized_revenue_usd", 0.0)),
        "governance_mode": governance.get("aggressiveness", "balanced"),
    }


# ---------------------------------------------------------------------------
# HTML landing page (self-contained, no external CDN needed)
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DreamCo Empire Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0d0d0d; color: #e0e0e0; }
    header {
      background: linear-gradient(90deg, #1a1a2e, #16213e);
      padding: 18px 32px;
      display: flex;
      align-items: center;
      gap: 14px;
      border-bottom: 2px solid #00d4aa;
    }
    header h1 { font-size: 1.6rem; color: #00d4aa; letter-spacing: 1px; }
    header span { font-size: 0.85rem; color: #aaa; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; padding: 24px; }
    .card {
      background: #1a1a2e;
      border: 1px solid #2a2a4a;
      border-radius: 10px;
      padding: 20px;
    }
    .card h2 { font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .card .value { font-size: 2rem; font-weight: 700; color: #00d4aa; }
    .card .sub { font-size: 0.75rem; color: #666; margin-top: 4px; }
    table { width: 100%; border-collapse: collapse; margin-top: 6px; }
    th { text-align: left; font-size: 0.75rem; color: #888; border-bottom: 1px solid #2a2a4a; padding: 6px 4px; }
    td { font-size: 0.8rem; padding: 6px 4px; border-bottom: 1px solid #1a1a2e; }
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
    }
    .badge-ok     { background: #0d3320; color: #00d4aa; }
    .badge-live   { background: #0a3a10; color: #22cc44; }
    .badge-err    { background: #3d1010; color: #ff6b6b; }
    .badge-idle   { background: #1a2a1a; color: #888; }
    footer { text-align: center; color: #444; padding: 20px; font-size: 0.75rem; }
    #refresh-note { text-align: right; color: #555; font-size: 0.72rem; padding: 0 24px 4px; }

    /* Bot catalog cards */
    .bot-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
      padding: 0 24px 24px;
    }
    .bot-card {
      background: #1a1a2e;
      border: 1px solid #2a2a4a;
      border-radius: 10px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: border-color 0.2s;
    }
    .bot-card:hover { border-color: #00d4aa; }
    .bot-card.live { border-color: #22cc44; }
    .bot-card .bot-title {
      font-size: 1rem;
      font-weight: 700;
      color: #e0e0e0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .bot-card .bot-desc { font-size: 0.78rem; color: #888; line-height: 1.4; }
    .bot-card .bot-revenue {
      font-size: 0.75rem;
      color: #00d4aa;
      font-weight: 600;
    }
    .bot-card .bot-category {
      font-size: 0.7rem;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .go-live-btn {
      margin-top: 4px;
      padding: 8px 16px;
      background: linear-gradient(135deg, #00d4aa, #0090ff);
      border: none;
      border-radius: 6px;
      color: #fff;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      letter-spacing: 0.5px;
      transition: opacity 0.15s, transform 0.1s;
      align-self: flex-start;
    }
    .go-live-btn:hover { opacity: 0.88; transform: translateY(-1px); }
    .go-live-btn:active { transform: translateY(0); }
    .go-live-btn:disabled {
      background: #0a3a10;
      color: #22cc44;
      cursor: default;
      opacity: 1;
    }
    .go-live-btn.loading { opacity: 0.6; cursor: wait; }
    .live-indicator {
      display: inline-block;
      width: 8px;
      height: 8px;
      background: #22cc44;
      border-radius: 50%;
      margin-left: 6px;
      box-shadow: 0 0 6px #22cc44;
      animation: pulse 1.4s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.35; }
    }
    .section-header {
      padding: 4px 24px 12px;
      font-size: 0.85rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    /* Governance panel */
    .governance-panel {
      background: #1a1a2e;
      border: 1px solid #2a2a4a;
      border-radius: 10px;
      padding: 20px 24px;
      margin: 0 24px 24px;
    }
    .governance-panel h2 {
      font-size: 0.85rem; color: #888; text-transform: uppercase;
      letter-spacing: 1px; margin-bottom: 14px;
    }
    .gov-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
    }
    .gov-field label {
      display: block; font-size: 0.75rem; color: #aaa; margin-bottom: 4px;
    }
    .gov-field input[type="range"] { width: 100%; accent-color: #00d4aa; }
    .gov-field select, .gov-field input[type="number"] {
      width: 100%; background: #0d0d0d; border: 1px solid #2a2a4a;
      color: #e0e0e0; border-radius: 4px; padding: 5px 8px;
      font-size: 0.82rem;
    }
    .gov-field .range-label {
      font-size: 0.72rem; color: #00d4aa; margin-top: 2px;
    }
    .gov-save-btn {
      margin-top: 14px;
      padding: 8px 20px;
      background: linear-gradient(135deg, #7b2ff7, #00d4aa);
      border: none; border-radius: 6px; color: #fff;
      font-size: 0.82rem; font-weight: 700; cursor: pointer;
      letter-spacing: 0.5px; transition: opacity 0.15s;
    }
    .gov-save-btn:hover { opacity: 0.88; }
    #gov-status { font-size: 0.75rem; color: #00d4aa; margin-left: 10px; }

    /* Failure log */
    .failure-row-failure { color: #ff6b6b; }
    .failure-row-conflict { color: #ff9900; }
    .failure-row-warning  { color: #ffdd57; }

    /* Per-bot dashboard link */
    .bot-dash-link {
      font-size: 0.72rem; color: #0090ff; text-decoration: none;
      margin-top: 2px; display: inline-block;
    }
    .bot-dash-link:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🤖 DreamCo Empire Dashboard</h1>
      <span id="ts">Loading…</span>
    </div>
  </header>

  <div class="grid" id="kpi-cards">
    <div class="card"><h2>Registered Bots</h2><div class="value" id="total-bots">—</div></div>
    <div class="card"><h2>Total Revenue</h2><div class="value" id="total-revenue">—</div><div class="sub">USD</div></div>
    <div class="card"><h2>Avg Composite KPI</h2><div class="value" id="avg-kpi">—</div><div class="sub">0–100 scale</div></div>
    <div class="card"><h2>Underperformers</h2><div class="value" id="underperformers">—</div><div class="sub">score &lt; 30</div></div>
  </div>

  <p class="section-header">🧠 Autonomous Runtime Core</p>
  <div class="grid" id="runtime-kpi-cards" style="padding-top:0">
    <div class="card"><h2>Manifest Coverage</h2><div class="value" id="runtime-manifests">—</div><div class="sub">metadata-driven bot manifests</div></div>
    <div class="card"><h2>Coordination Efficiency</h2><div class="value" id="runtime-coordination">—</div><div class="sub">swarm negotiation + task claiming</div></div>
    <div class="card"><h2>Avg Trust Score</h2><div class="value" id="runtime-trust">—</div><div class="sub">bounded governance confidence</div></div>
    <div class="card"><h2>ROI Attribution</h2><div class="value" id="runtime-roi">—</div><div class="sub">realized revenue per manifested worker</div></div>
  </div>

  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Runtime Layers &amp; BuddyAI Governance</h2>
      <div id="runtime-layers" style="font-size:0.8rem;color:#aaa;line-height:1.6">Loading runtime topology…</div>
      <div id="runtime-buddy" class="sub" style="margin-top:10px;color:#00d4aa"></div>
    </div>
  </div>

  <!-- ── HIGH-REVENUE BOT CATALOG ── -->
  <p class="section-header">🚀 High-Revenue Bots — Go Live</p>
  <div class="bot-grid" id="bot-catalog">
    <div class="card" style="color:#555">Loading bot catalog…</div>
  </div>

  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Bot Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>#</th><th>Bot Name</th><th>Efficiency</th>
            <th>ROI</th><th>Reliability</th><th>Composite</th><th>Runs</th>
          </tr>
        </thead>
        <tbody id="leaderboard-body">
          <tr><td colspan="7" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Revenue by Source</h2>
      <table>
        <thead><tr><th>Source</th><th>Amount (USD)</th></tr></thead>
        <tbody id="revenue-body">
          <tr><td colspan="2" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── QUANTUM BOT SYSTEM HEALTH ── -->
  <p class="section-header">⚛️ Quantum Bot — System Health</p>
  <div class="grid" id="quantum-health" style="padding-top:0">
    <div class="card">
      <h2>Quantum Status</h2>
      <div class="value" id="quantum-status">—</div>
      <div class="sub" id="quantum-tier"></div>
    </div>
    <div class="card">
      <h2>Quantum Engines</h2>
      <div id="quantum-engines" style="font-size:0.8rem;color:#aaa;margin-top:6px">Loading…</div>
    </div>
    <div class="card">
      <h2>Last Checked</h2>
      <div class="value" style="font-size:1rem;color:#aaa" id="quantum-checked">—</div>
    </div>
  </div>

  <!-- ── WORKFLOW MONITOR ── -->
  <p class="section-header">⚙️ GitHub Actions — Workflow Monitor (Live, Read-Only)</p>
  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Recent Workflow Runs</h2>
      <table id="workflow-table">
        <thead>
          <tr>
            <th>Workflow</th><th>Branch</th><th>Event</th>
            <th>Status</th><th>Conclusion</th><th>Started</th><th>Link</th>
          </tr>
        </thead>
        <tbody id="workflow-body">
          <tr><td colspan="7" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── ARTIFACTS ── -->
  <p class="section-header">📦 GitHub Actions — Artifacts</p>
  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Available Artifacts</h2>
      <table>
        <thead>
          <tr><th>Name</th><th>Size</th><th>Created</th><th>Expires</th><th>Status</th></tr>
        </thead>
        <tbody id="artifact-body">
          <tr><td colspan="5" style="color:#555">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── BOT GOVERNANCE CONTROL ── -->
  <p class="section-header">🎛️ Bot Governance — Global Runtime Controls</p>
  <div class="governance-panel" id="governance-panel">
    <h2>Runtime Governance Settings</h2>
    <div class="gov-grid">
      <div class="gov-field">
        <label for="gov-aggressiveness">Aggressiveness Level</label>
        <select id="gov-aggressiveness">
          <option value="passive">Passive — minimal retries, conservative resources</option>
          <option value="balanced" selected>Balanced — 1 retry, standard resources</option>
          <option value="aggressive">Aggressive — 2 retries, elevated resources</option>
          <option value="max">Max — 3 retries, maximum resources</option>
        </select>
      </div>
      <div class="gov-field">
        <label for="gov-max-exec">Max Execution Duration (seconds): <span id="gov-exec-label">300</span></label>
        <input type="range" id="gov-max-exec" min="30" max="3600" step="30" value="300"
          oninput="document.getElementById('gov-exec-label').textContent=this.value">
        <div class="range-label">30 s — 3600 s</div>
      </div>
      <div class="gov-field">
        <label for="gov-retry-policy">Retry Policy</label>
        <select id="gov-retry-policy">
          <option value="none">None — no retries on failure</option>
          <option value="once">Once — 1 retry</option>
          <option value="twice">Twice — 2 retries</option>
          <option value="auto" selected>Auto — determined by aggressiveness level</option>
        </select>
      </div>
    </div>
    <div style="margin-top:14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <button class="gov-save-btn" onclick="saveGovernance()">💾 Save Governance Settings</button>
      <span id="gov-status"></span>
    </div>
  </div>

  <!-- ── UNCODED BOT MONITOR ── -->
  <p class="section-header">🔍 Uncoded Bot Monitor</p>
  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Uncoded / Stub Bot Report</h2>
      <div id="uncoded-summary" style="font-size:0.82rem;color:#aaa;margin-bottom:10px">Loading…</div>
      <table>
        <thead>
          <tr><th>Bot Path</th><th>Status</th><th>Stub Hints</th></tr>
        </thead>
        <tbody id="uncoded-body">
          <tr><td colspan="3" style="color:#555">Scanning…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── FAILURE & CONFLICT LOG ── -->
  <p class="section-header">🚨 Failures &amp; Conflicts — Detailed Report</p>
  <div style="padding: 0 24px 24px;">
    <div class="card">
      <h2 style="margin-bottom:12px;">Recent Failures &amp; Conflicts</h2>
      <table>
        <thead>
          <tr><th>Time</th><th>Bot</th><th>Type</th><th>Message</th></tr>
        </thead>
        <tbody id="failure-body">
          <tr><td colspan="4" style="color:#555">No failures recorded.</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <p id="refresh-note">Auto-refreshes every 15 s</p>
  <footer>DreamCo Empire OS — Powered by the GLOBAL AI SOURCES FLOW framework</footer>

  <script>
    // Track which bots are live in this session
    const liveBots = new Set();

    async function goLive(botName, btn) {
      btn.classList.add('loading');
      btn.disabled = true;
      btn.textContent = '⏳ Deploying…';
      try {
        const res = await fetch(`/api/bots/${encodeURIComponent(botName)}/go_live`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tier: 'pro' }),
        });
        const data = await res.json();
        if (res.ok) {
          liveBots.add(botName);
          btn.textContent = '✅ Live';
          btn.classList.remove('loading');
          btn.closest('.bot-card').classList.add('live');
          const ind = document.createElement('span');
          ind.className = 'live-indicator';
          btn.after(ind);
        } else {
          btn.textContent = '⚠ Error';
          btn.classList.remove('loading');
          btn.disabled = false;
        }
      } catch (e) {
        btn.textContent = '⚠ Error';
        btn.classList.remove('loading');
        btn.disabled = false;
      }
    }

    async function loadWorkflows() {
      try {
        const [wf, art] = await Promise.all([
          fetch('/api/github/workflows').then(r => r.json()),
          fetch('/api/github/artifacts').then(r => r.json()),
        ]);

        const wfBody = document.getElementById('workflow-body');
        const runs = wf.runs || [];
        if (runs.length) {
          const conclusionColor = c => {
            if (c === 'success') return '#22cc44';
            if (c === 'failure') return '#ff4444';
            if (c === 'cancelled') return '#ff9900';
            return '#888';
          };
          wfBody.innerHTML = runs.map(r => `
            <tr>
              <td>${r.name || '—'}</td>
              <td>${r.branch || '—'}</td>
              <td>${r.event || '—'}</td>
              <td>${r.status || '—'}</td>
              <td style="color:${conclusionColor(r.conclusion)};font-weight:600">${r.conclusion || '—'}</td>
              <td>${r.run_started_at ? new Date(r.run_started_at).toLocaleString() : '—'}</td>
              <td>${r.url ? `<a href="${r.url}" target="_blank" rel="noopener" style="color:#00d4aa">View</a>` : '—'}</td>
            </tr>`).join('');
        } else {
          const msg = wf.reason ? `Unavailable: ${wf.reason}` : 'No workflow runs found.';
          wfBody.innerHTML = `<tr><td colspan="7" style="color:#555">${msg}</td></tr>`;
        }

        const artBody = document.getElementById('artifact-body');
        const artifacts = art.artifacts || [];
        if (artifacts.length) {
          artBody.innerHTML = artifacts.map(a => {
            const kb = a.size_in_bytes ? (a.size_in_bytes / 1024).toFixed(1) + ' KB' : '—';
            const created = a.created_at ? new Date(a.created_at).toLocaleString() : '—';
            const expires = a.expires_at ? new Date(a.expires_at).toLocaleDateString() : '—';
            const statusBadge = a.expired
              ? '<span style="color:#ff4444">Expired</span>'
              : '<span style="color:#22cc44">Active</span>';
            return `<tr><td>${a.name}</td><td>${kb}</td><td>${created}</td><td>${expires}</td><td>${statusBadge}</td></tr>`;
          }).join('');
        } else {
          const msg = art.reason ? `Unavailable: ${art.reason}` : 'No artifacts found.';
          artBody.innerHTML = `<tr><td colspan="5" style="color:#555">${msg}</td></tr>`;
        }
      } catch (e) {
        console.error('Workflow load error:', e);
      }
    }

    async function loadQuantum() {
      try {
        const q = await fetch('/api/quantum/status').then(r => r.json());
        const statusEl = document.getElementById('quantum-status');
        const tierEl = document.getElementById('quantum-tier');
        const engEl = document.getElementById('quantum-engines');
        const checkedEl = document.getElementById('quantum-checked');
        if (q.status === 'ok') {
          statusEl.textContent = '✅ OK';
          statusEl.style.color = '#22cc44';
          tierEl.textContent = 'Tier: ' + (q.tier || '—');
          engEl.innerHTML = (q.engines || []).map(e => `<div>✓ ${e}</div>`).join('');
        } else {
          statusEl.textContent = '⚠ Error';
          statusEl.style.color = '#ff4444';
          tierEl.textContent = q.reason || '';
          engEl.textContent = '';
        }
        checkedEl.textContent = q.checked_at ? new Date(q.checked_at).toLocaleTimeString() : '—';
      } catch (e) {
        console.error('Quantum status load error:', e);
      }
    }

    async function loadCatalog() {
      try {
        const data = await fetch('/api/bots/catalog').then(r => r.json());
        const grid = document.getElementById('bot-catalog');
        grid.innerHTML = '';
        (data.catalog || []).forEach(bot => {
          const isLive = liveBots.has(bot.name) || bot.is_live;
          const card = document.createElement('div');
          card.className = 'bot-card' + (isLive ? ' live' : '');
          card.innerHTML = `
            <div class="bot-title">${bot.emoji || '🤖'} ${bot.display_name}</div>
            <div class="bot-category">${bot.category}</div>
            <div class="bot-desc">${bot.description}</div>
            <div class="bot-revenue">💰 ${bot.revenue_model}</div>
            <button
              class="go-live-btn"
              onclick="goLive('${bot.name}', this)"
              ${isLive ? "disabled" : ""}
            >${isLive ? '✅ Live' : '🚀 Go Live'}</button>
            ${isLive ? '<span class="live-indicator"></span>' : ''}
            <a class="bot-dash-link" href="/bots/${encodeURIComponent(bot.name)}">📊 Bot Dashboard →</a>
          `;
          grid.appendChild(card);
        });
      } catch (e) {
        console.error('Catalog load error:', e);
      }
    }

    async function loadGovernance() {
      try {
        const g = await fetch('/api/governance').then(r => r.json());
        const aggSel = document.getElementById('gov-aggressiveness');
        const maxExec = document.getElementById('gov-max-exec');
        const execLabel = document.getElementById('gov-exec-label');
        const retrySel = document.getElementById('gov-retry-policy');
        if (aggSel) aggSel.value = g.aggressiveness || 'balanced';
        if (maxExec) {
          maxExec.value = g.max_execution_seconds || 300;
          if (execLabel) execLabel.textContent = maxExec.value;
        }
        if (retrySel) retrySel.value = g.retry_policy || 'auto';
      } catch (e) {
        console.error('Governance load error:', e);
      }
    }

    async function saveGovernance() {
      const statusEl = document.getElementById('gov-status');
      statusEl.textContent = '⏳ Saving…';
      try {
        const payload = {
          aggressiveness: document.getElementById('gov-aggressiveness').value,
          max_execution_seconds: parseInt(document.getElementById('gov-max-exec').value, 10),
          retry_policy: document.getElementById('gov-retry-policy').value,
        };
        const res = await fetch('/api/governance/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (res.ok) {
          statusEl.textContent = '✅ Saved!';
          setTimeout(() => { statusEl.textContent = ''; }, 3000);
        } else {
          statusEl.textContent = '⚠ Error saving';
        }
      } catch (e) {
        statusEl.textContent = '⚠ Network error';
      }
    }

    async function loadUncoded() {
      try {
        const data = await fetch('/api/bots/uncoded').then(r => r.json());
        const summary = document.getElementById('uncoded-summary');
        const tbody = document.getElementById('uncoded-body');
        summary.textContent =
          `Uncoded bots: ${data.uncoded_count} | Stub/TODO bots: ${data.stubbed_count}`;
        const rows = [];
        (data.uncoded || []).forEach(p => {
          rows.push(`<tr><td><code>${p}</code></td><td><span style="color:#ff9900">⚠ No run()</span></td><td>—</td></tr>`);
        });
        (data.stubbed || []).forEach(s => {
          const hints = (s.hints || []).map(h => `<code style="font-size:0.7rem">${h}</code>`).join('<br>');
          rows.push(`<tr><td><code>${s.path}</code></td><td><span style="color:#ffdd57">🔧 Stub</span></td><td>${hints}</td></tr>`);
        });
        tbody.innerHTML = rows.length
          ? rows.join('')
          : '<tr><td colspan="3" style="color:#22cc44">✅ No uncoded bots found.</td></tr>';
      } catch (e) {
        console.error('Uncoded load error:', e);
      }
    }

    async function loadFailures() {
      try {
        const data = await fetch('/api/failures').then(r => r.json());
        const tbody = document.getElementById('failure-body');
        const failures = data.failures || [];
        if (failures.length) {
          const typeColor = t => {
            if (t === 'failure') return 'failure-row-failure';
            if (t === 'conflict') return 'failure-row-conflict';
            return 'failure-row-warning';
          };
          tbody.innerHTML = failures.slice().reverse().map(f => `
            <tr class="${typeColor(f.failure_type)}">
              <td style="white-space:nowrap">${f.timestamp ? new Date(f.timestamp).toLocaleString() : '—'}</td>
              <td>${f.bot_name || '—'}</td>
              <td><strong>${f.failure_type || '—'}</strong></td>
              <td>${f.message || '—'}</td>
            </tr>`).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="4" style="color:#22cc44">✅ No failures recorded.</td></tr>';
        }
      } catch (e) {
        console.error('Failures load error:', e);
      }
    }

    async function loadRuntime() {
      try {
        const overview = await fetch('/api/runtime/overview').then(r => r.json());
        const metrics = overview.metrics || {};
        document.getElementById('runtime-manifests').textContent = metrics.manifested_bots ?? '—';
        document.getElementById('runtime-coordination').textContent =
          metrics.coordination_efficiency != null ? metrics.coordination_efficiency.toFixed(1) + '%' : '—';
        document.getElementById('runtime-trust').textContent =
          metrics.avg_trust_score != null ? metrics.avg_trust_score.toFixed(2) : '—';
        document.getElementById('runtime-roi').textContent =
          metrics.roi_attribution != null ? '$' + metrics.roi_attribution.toFixed(2) : '—';

        const layers = overview.runtime_layers || [];
        const layersEl = document.getElementById('runtime-layers');
        layersEl.innerHTML = layers.map(layer => `
          <div style="margin-bottom:10px">
            <strong style="color:#e0e0e0">${layer.title}</strong>
            <div>${(layer.components || []).join(' • ')}</div>
          </div>
        `).join('');

        const buddy = overview.buddy_ai || {};
        document.getElementById('runtime-buddy').textContent =
          buddy.display_name
            ? `${buddy.display_name} — ${buddy.swarm_role} | lifecycle: ${buddy.lifecycle_state} | trust: ${buddy.trust_score}`
            : '';
      } catch (e) {
        console.error('Runtime overview load error:', e);
      }
    }

    async function loadAll() {
      try {
        const [status, leader, revenue] = await Promise.all([
          fetch('/api/status').then(r => r.json()),
          fetch('/api/leaderboard').then(r => r.json()),
          fetch('/api/revenue').then(r => r.json()),
        ]);

        document.getElementById('ts').textContent = new Date().toLocaleString();
        document.getElementById('total-bots').textContent = status.registered_bots ?? '—';
        document.getElementById('total-revenue').textContent =
          '$' + (revenue.total_income_usd ?? 0).toFixed(2);
        document.getElementById('avg-kpi').textContent =
          status.avg_composite_kpi != null ? status.avg_composite_kpi.toFixed(1) : '—';
        document.getElementById('underperformers').textContent =
          status.underperformers ?? '—';

        const lbBody = document.getElementById('leaderboard-body');
        if (leader.leaderboard && leader.leaderboard.length) {
          lbBody.innerHTML = leader.leaderboard.map((b, i) => `
            <tr>
              <td>${i + 1}</td>
              <td>${b.bot_name}</td>
              <td>${b.efficiency_score.toFixed(1)}</td>
              <td>${b.roi_score.toFixed(1)}</td>
              <td>${b.reliability_score.toFixed(1)}</td>
              <td><strong style="color:#00d4aa">${b.composite_score.toFixed(1)}</strong></td>
              <td>${b.total_runs}</td>
            </tr>`).join('');
        } else {
          lbBody.innerHTML = '<tr><td colspan="7" style="color:#555">No data yet — record some bot runs.</td></tr>';
        }

        const revBody = document.getElementById('revenue-body');
        const bySource = revenue.by_source ?? {};
        const entries = Object.entries(bySource);
        if (entries.length) {
          revBody.innerHTML = entries
            .sort((a, b) => b[1] - a[1])
            .map(([src, amt]) => `<tr><td>${src}</td><td>$${amt.toFixed(2)}</td></tr>`)
            .join('');
        } else {
          revBody.innerHTML = '<tr><td colspan="2" style="color:#555">No revenue recorded yet.</td></tr>';
        }

      } catch (e) {
        console.error('Dashboard load error:', e);
      }
    }

    loadCatalog();
    loadAll();
    loadWorkflows();
    loadQuantum();
    loadGovernance();
    loadUncoded();
    loadFailures();
    loadRuntime();
    setInterval(() => { loadAll(); loadWorkflows(); loadQuantum(); loadFailures(); loadRuntime(); }, 15000);
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(
    control_center: Optional["ControlCenter"] = None,
    db: Optional[BotPerformanceDB] = None,
) -> Any:
    """Create and configure the Flask dashboard application.

    Parameters
    ----------
    control_center : ControlCenter, optional
        An existing ControlCenter instance.  A new one is created if omitted.
    db : BotPerformanceDB, optional
        An existing BotPerformanceDB.  A new in-memory DB is created if omitted.

    Returns
    -------
    Flask application instance (or a stub if Flask is not installed).
    """
    if not _FLASK_AVAILABLE:
        raise ImportError(
            "Flask is required for the web dashboard. "
            "Install it with: pip install flask flask-cors"
        )

    cc = control_center or ControlCenter()
    perf_db = db or BotPerformanceDB()

    app = Flask(__name__)

    # ---------------------------------------------------------------
    # Landing page
    # ---------------------------------------------------------------

    @app.route("/")
    def index() -> Response:
        return Response(_DASHBOARD_HTML, mimetype="text/html")

    @app.route("/dashboard/chooser")
    def dashboard_chooser() -> Response:
        from ui.dashboard_chooser import (
            load_dashboard_entries,
            parse_filter_args,
            render_dashboard_chooser_html,
        )

        filter_args = parse_filter_args(request.args)
        html = render_dashboard_chooser_html(
            entries=load_dashboard_entries(catalog=_BOT_CATALOG),
            categories=filter_args["categories"],
            production_ready=filter_args["production_ready"],
            governance_compatible=filter_args["governance_compatible"],
            migration_candidate=filter_args["migration_candidate"],
        )
        return Response(html, mimetype="text/html")

    # ---------------------------------------------------------------
    # Status
    # ---------------------------------------------------------------

    @app.route("/api/status")
    def api_status() -> Response:
        monitoring = cc.get_monitoring_dashboard()
        db_stats = perf_db.get_stats()
        return jsonify({
            **monitoring,
            "avg_composite_kpi": db_stats["avg_composite_score"],
            "underperformers": db_stats["underperformers_below_30"],
        })

    # ---------------------------------------------------------------
    # Bots
    # ---------------------------------------------------------------

    @app.route("/api/bots")
    def api_bots() -> Response:
        bot_status = cc.get_status()
        scores = {s["bot_name"]: s for s in perf_db.get_all_scores()}
        bots = []
        for name, meta in bot_status.get("bots", {}).items():
            entry = dict(meta)
            entry["bot_name"] = name
            entry.update(scores.get(name, {}))
            bots.append(entry)
        return jsonify({"bots": bots, "total": len(bots)})

    @app.route("/api/runtime/manifests")
    def api_runtime_manifests() -> Response:
        registry = _build_runtime_registry(cc, perf_db)
        return jsonify({
            "schema": "dreamco_runtime_manifest.v1",
            "platform_version": PLATFORM_VERSION,
            "summary": registry.manifest_summary(),
            "manifests": [entry.to_dict() for entry in registry.all_manifests()],
        })

    @app.route("/api/runtime/overview")
    def api_runtime_overview() -> Response:
        return jsonify(_build_runtime_overview(cc, perf_db))

    @app.route("/api/bots/catalog")
    def api_bots_catalog() -> Response:
        """Return the full high-revenue bot catalog with Go Live status."""
        registered = set(cc.get_status().get("bots", {}).keys())
        catalog = []
        for bot in _BOT_CATALOG:
            entry = dict(bot)
            entry["is_live"] = bot["name"] in registered
            catalog.append(entry)
        return jsonify({"catalog": catalog, "total": len(catalog)})

    @app.route("/api/bots/register", methods=["POST"])
    def api_register_bot() -> Response:
        data = request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Bot name is required."}), 400

        class _Stub:
            """Minimal stub registered when no real bot instance is provided."""
            def __init__(self, tier_str: str):
                from bots.ai_learning_system.tiers import Tier as LSTier
                try:
                    self.tier = LSTier(tier_str)
                except ValueError:
                    self.tier = LSTier.FREE

        cc.register_bot(name, _Stub(data.get("tier", "free")))
        return jsonify({"registered": name, "status": "ok"}), 201

    @app.route("/api/bots/<bot_name>/go_live", methods=["POST"])
    def api_go_live(bot_name: str) -> Response:
        """
        Activate / deploy a bot instance.

        Registers the bot with the ControlCenter if not already registered,
        records an initial run, and returns the deployment record.

        Request JSON (optional)
        -----------------------
        tier : str
            Desired subscription tier (``free``, ``pro``, ``enterprise``).
            Defaults to ``pro``.

        Returns
        -------
        201
            Deployment record with status, timestamp, and bot metadata.
        400
            If ``bot_name`` is blank.
        """
        bot_name = bot_name.strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400

        data = request.get_json(silent=True) or {}
        tier_str = data.get("tier", "pro")

        class _LiveStub:
            """Minimal live bot stub."""
            def __init__(self, t: str):
                from bots.ai_learning_system.tiers import Tier as LSTier
                try:
                    self.tier = LSTier(t)
                except ValueError:
                    self.tier = LSTier.FREE

        # Register (idempotent — no-op if already present)
        cc.register_bot(bot_name, _LiveStub(tier_str))

        # Record the go-live run event
        perf_db.record_run(
            bot_name=bot_name,
            kpis={"revenue_usd": 0.0, "tasks_completed": 0},
            status="ok",
            notes=f"Go Live deployment — tier: {tier_str}",
        )

        deployment = {
            "bot_name": bot_name,
            "status": "live",
            "tier": tier_str,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "message": f"Bot '{bot_name}' is now live on the {tier_str} tier.",
        }
        return jsonify(deployment), 201

    # ---------------------------------------------------------------
    # Revenue
    # ---------------------------------------------------------------

    @app.route("/api/revenue")
    def api_revenue() -> Response:
        return jsonify(cc.get_income_summary())

    # ---------------------------------------------------------------
    # Leaderboard
    # ---------------------------------------------------------------

    @app.route("/api/leaderboard")
    def api_leaderboard() -> Response:
        top_n = request.args.get("top", 10, type=int)
        return jsonify({"leaderboard": perf_db.get_leaderboard(top_n=top_n)})

    # ---------------------------------------------------------------
    # Underperformers
    # ---------------------------------------------------------------

    @app.route("/api/underperformers")
    def api_underperformers() -> Response:
        threshold = request.args.get("threshold", 30.0, type=float)
        return jsonify({
            "threshold": threshold,
            "underperformers": perf_db.get_underperformers(threshold=threshold),
        })

    # ---------------------------------------------------------------
    # Record run
    # ---------------------------------------------------------------

    @app.route("/api/record_run", methods=["POST"])
    def api_record_run() -> Response:
        data = request.get_json(silent=True) or {}
        bot_name = data.get("bot_name", "").strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400
        entry = perf_db.record_run(
            bot_name=bot_name,
            kpis=data.get("kpis", {}),
            status=data.get("status", "ok"),
            notes=data.get("notes", ""),
        )
        return jsonify(entry), 201

    # ---------------------------------------------------------------
    # Run history
    # ---------------------------------------------------------------

    @app.route("/api/history/<bot_name>")
    def api_history(bot_name: str) -> Response:
        limit = request.args.get("limit", 50, type=int)
        history = perf_db.get_run_history(bot_name, limit=limit)
        return jsonify({"bot_name": bot_name, "history": history})

    # ---------------------------------------------------------------
    # GitHub Actions — read-only workflow monitor
    # ---------------------------------------------------------------

    @app.route("/api/github/workflows")
    def api_github_workflows() -> Response:
        """Return recent GitHub Actions workflow runs (read-only)."""
        repo = os.environ.get("GITHUB_REPOSITORY", _DEFAULT_REPO)
        per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, request.args.get("per_page", 10, type=int)))
        data = _fetch_github_workflows(repo=repo, per_page=per_page)
        return jsonify(data)

    @app.route("/api/github/artifacts")
    def api_github_artifacts() -> Response:
        """Return recent GitHub Actions artifacts (read-only)."""
        repo = os.environ.get("GITHUB_REPOSITORY", _DEFAULT_REPO)
        per_page = max(_GITHUB_PER_PAGE_MIN, min(_GITHUB_PER_PAGE_MAX, request.args.get("per_page", 10, type=int)))
        data = _fetch_github_artifacts(repo=repo, per_page=per_page)
        return jsonify(data)

    # ---------------------------------------------------------------
    # Quantum Bot — system health check (read-only)
    # ---------------------------------------------------------------

    @app.route("/api/quantum/status")
    def api_quantum_status() -> Response:
        """Return Quantum Bot health status (read-only instantiation check)."""
        return jsonify(_check_quantum_bot_status())

    # ---------------------------------------------------------------
    # Global governance settings
    # ---------------------------------------------------------------

    @app.route("/api/governance")
    def api_governance_get() -> Response:
        """Return the current global governance settings."""
        return jsonify(_get_governance())

    @app.route("/api/governance/settings", methods=["POST"])
    def api_governance_set() -> Response:
        """Update global governance settings.

        Request JSON (all fields optional)
        ------------------------------------
        aggressiveness : str
            One of ``passive``, ``balanced``, ``aggressive``, ``max``.
        max_execution_seconds : int
            Clamped to [30, 3600].
        retry_policy : str
            One of ``none``, ``once``, ``twice``, ``auto``.

        Returns
        -------
        200
            Updated governance state.
        400
            If no recognisable fields are provided.
        """
        data = request.get_json(silent=True) or {}
        if not any(k in data for k in ("aggressiveness", "max_execution_seconds", "retry_policy")):
            return jsonify({"error": "No valid governance fields provided."}), 400
        updated = _update_governance(
            aggressiveness=data.get("aggressiveness"),
            max_execution_seconds=data.get("max_execution_seconds"),
            retry_policy=data.get("retry_policy"),
        )
        return jsonify(updated)

    # ---------------------------------------------------------------
    # Per-bot runtime configuration
    # ---------------------------------------------------------------

    @app.route("/api/bots/<bot_name>/configure", methods=["POST"])
    def api_bot_configure(bot_name: str) -> Response:
        """Configure runtime parameters for a specific bot.

        Request JSON (all fields optional)
        ------------------------------------
        aggressiveness : str
        max_execution_seconds : int
        retry_policy : str

        Returns
        -------
        200  Updated bot config.
        400  If bot_name is blank.
        """
        bot_name = bot_name.strip()
        if not bot_name:
            return jsonify({"error": "bot_name is required."}), 400
        data = request.get_json(silent=True) or {}
        cfg = _set_bot_config(
            bot_name,
            aggressiveness=data.get("aggressiveness"),
            max_execution_seconds=data.get("max_execution_seconds"),
            retry_policy=data.get("retry_policy"),
        )
        return jsonify(cfg)

    @app.route("/api/bots/<bot_name>/config")
    def api_bot_config_get(bot_name: str) -> Response:
        """Return the current runtime config for a specific bot."""
        return jsonify(_get_bot_config(bot_name.strip()))

    # ---------------------------------------------------------------
    # Uncoded / stub bot monitor
    # ---------------------------------------------------------------

    @app.route("/api/bots/uncoded")
    def api_bots_uncoded() -> Response:
        """Return uncoded and stub bot report."""
        return jsonify(_detect_uncoded_bots())

    # ---------------------------------------------------------------
    # Failure and conflict log
    # ---------------------------------------------------------------

    @app.route("/api/failures")
    def api_failures_get() -> Response:
        """Return recent failure and conflict entries.

        Query parameters
        ----------------
        bot_name : str   (optional) filter by bot name
        limit    : int   (optional, default 50)
        """
        bot_name = request.args.get("bot_name", "").strip() or None
        limit = max(1, min(200, request.args.get("limit", 50, type=int)))
        failures = _get_failures(bot_name=bot_name, limit=limit)
        return jsonify({"failures": failures, "total": len(failures)})

    @app.route("/api/failures/report", methods=["POST"])
    def api_failures_report() -> Response:
        """Append a failure entry to the log.

        Request JSON
        ------------
        bot_name     : str  (required)
        failure_type : str  (required) — e.g. ``failure``, ``conflict``, ``warning``
        message      : str  (required)
        details      : dict (optional)

        Returns
        -------
        201  The appended entry.
        400  Missing required fields.
        """
        data = request.get_json(silent=True) or {}
        bot_name = data.get("bot_name", "").strip()
        failure_type = data.get("failure_type", "").strip()
        message = data.get("message", "").strip()
        if not bot_name or not failure_type or not message:
            return jsonify({"error": "bot_name, failure_type, and message are required."}), 400
        entry = _append_failure(
            bot_name=bot_name,
            failure_type=failure_type,
            message=message,
            details=data.get("details"),
        )
        return jsonify(entry), 201

    # ---------------------------------------------------------------
    # Per-bot HTML dashboard page
    # ---------------------------------------------------------------

    @app.route("/bots/<bot_name>")
    def bot_dashboard_page(bot_name: str) -> Response:
        """Render an HTML dashboard page for a specific bot."""
        bot_name = bot_name.strip()
        catalog_entry = next(
            (b for b in _BOT_CATALOG if b["name"] == bot_name),
            None,
        )
        cfg = _get_bot_config(bot_name)
        gov = _get_governance()
        failures = _get_failures(bot_name=bot_name, limit=20)
        history = perf_db.get_run_history(bot_name, limit=10)
        scores = {s["bot_name"]: s for s in perf_db.get_all_scores()}
        score = scores.get(bot_name, {})
        runtime_registry = _build_runtime_registry(cc, perf_db)

        display_name = (catalog_entry or {}).get("display_name", bot_name)
        emoji = (catalog_entry or {}).get("emoji", "🤖")
        description = (catalog_entry or {}).get("description", "No description available.")
        revenue_model = (catalog_entry or {}).get("revenue_model", "—")
        category = (catalog_entry or {}).get("category", "—")

        is_live = bot_name in cc.get_status().get("bots", {})
        live_badge = '<span style="color:#22cc44;font-weight:700">● LIVE</span>' if is_live else '<span style="color:#888">○ Idle</span>'
        manifest = runtime_registry.get(_normalize_bot_id(bot_name)) or _build_runtime_manifest_entry(
            bot_name=bot_name or "unknown_bot",
            display_name=display_name,
            category=category,
            description=description,
            revenue_model=revenue_model,
            is_live=is_live,
            realized_revenue=0.0,
            composite_score=float(score.get("composite_score", 0.0) or 0.0),
            total_runs=int(score.get("total_runs", 0) or 0),
        )
        manifest_permissions = ", ".join(manifest.permissions) or "—"
        manifest_memory = ", ".join(manifest.memory_nodes) or "—"
        manifest_revenue = manifest.revenue_attribution

        failure_rows = "".join(
            f"<tr><td style='white-space:nowrap'>{e.get('timestamp', '')[:19].replace('T', ' ') if e.get('timestamp') else '—'}</td>"
            f"<td style='color:#ff6b6b'>{e.get('failure_type', '—')}</td>"
            f"<td>{e.get('message', '—')}</td></tr>"
            for e in reversed(failures)
        ) or "<tr><td colspan='3' style='color:#22cc44'>✅ No failures</td></tr>"

        history_rows = "".join(
            f"<tr><td style='white-space:nowrap'>{h.get('timestamp', '')[:19].replace('T', ' ') if h.get('timestamp') else '—'}</td>"
            f"<td>{h.get('status', '—')}</td>"
            f"<td>{h.get('notes', '')}</td></tr>"
            for h in reversed(history)
        ) or "<tr><td colspan='3' style='color:#555'>No runs recorded</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{display_name} — Bot Dashboard</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', sans-serif; background: #0d0d0d; color: #e0e0e0; }}
    header {{ background: linear-gradient(90deg,#1a1a2e,#16213e); padding: 18px 32px;
              border-bottom: 2px solid #00d4aa; display:flex; align-items:center; gap:14px; }}
    header h1 {{ font-size: 1.4rem; color: #00d4aa; }}
    .back {{ font-size: 0.8rem; color: #aaa; text-decoration: none; }}
    .back:hover {{ color: #00d4aa; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; padding:24px; }}
    .card {{ background:#1a1a2e; border:1px solid #2a2a4a; border-radius:10px; padding:18px; }}
    .card h2 {{ font-size:0.8rem; color:#888; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
    .value {{ font-size:1.6rem; font-weight:700; color:#00d4aa; }}
    .sub {{ font-size:0.72rem; color:#666; margin-top:4px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:6px; }}
    th {{ text-align:left; font-size:0.73rem; color:#888; border-bottom:1px solid #2a2a4a; padding:5px 4px; }}
    td {{ font-size:0.78rem; padding:5px 4px; border-bottom:1px solid #1a1a2e; }}
    .gov-field {{ margin-bottom:12px; }}
    .gov-field label {{ display:block; font-size:0.75rem; color:#aaa; margin-bottom:4px; }}
    .gov-field select, .gov-field input[type="number"] {{
      width:100%; background:#0d0d0d; border:1px solid #2a2a4a;
      color:#e0e0e0; border-radius:4px; padding:5px 8px; font-size:0.82rem;
    }}
    .gov-field input[type="range"] {{ width:100%; accent-color:#00d4aa; }}
    .save-btn {{
      padding:8px 18px; background:linear-gradient(135deg,#00d4aa,#0090ff);
      border:none; border-radius:6px; color:#fff; font-size:0.82rem;
      font-weight:700; cursor:pointer;
    }}
    #save-status {{ font-size:0.75rem; color:#00d4aa; margin-left:10px; }}
    .section {{ padding: 0 24px 24px; }}
    footer {{ text-align:center; color:#444; padding:20px; font-size:0.75rem; }}
  </style>
</head>
<body>
  <header>
    <div>
      <a class="back" href="/">← Back to Dashboard</a>
      <h1>{emoji} {display_name} — Bot Dashboard</h1>
      <span style="font-size:0.8rem;color:#aaa">{category} &middot; {live_badge}</span>
    </div>
  </header>

  <div class="grid">
    <div class="card">
      <h2>Description</h2>
      <div style="font-size:0.82rem;color:#aaa;line-height:1.5">{description}</div>
    </div>
    <div class="card">
      <h2>Revenue Model</h2>
      <div class="value" style="font-size:1.1rem">{revenue_model}</div>
    </div>
    <div class="card">
      <h2>Composite KPI</h2>
      <div class="value">{score.get('composite_score', '—')}</div>
      <div class="sub">0–100 scale</div>
    </div>
    <div class="card">
      <h2>Total Runs</h2>
      <div class="value">{score.get('total_runs', 0)}</div>
    </div>
  </div>

  <div class="section">
    <div class="card">
      <h2 style="margin-bottom:14px">📘 Prospectus &amp; Runtime Manifest</h2>
      <table>
        <tbody>
          <tr><th>Lifecycle State</th><td>{manifest.lifecycle_state}</td><th>Swarm Role</th><td>{manifest.swarm_role}</td></tr>
          <tr><th>Specialization</th><td>{manifest.specialization or category}</td><th>Trust Score</th><td>{manifest.trust_score:.2f}</td></tr>
          <tr><th>Capabilities</th><td colspan="3">{", ".join(manifest.capabilities) or "—"}</td></tr>
          <tr><th>Permissions</th><td colspan="3">{manifest_permissions}</td></tr>
          <tr><th>Memory Nodes</th><td colspan="3">{manifest_memory}</td></tr>
          <tr><th>Revenue Attribution</th><td colspan="3">Estimated monthly: ${manifest_revenue.get("estimated_monthly_usd", 0.0):.2f} | Realized: ${manifest_revenue.get("realized_usd", 0.0):.2f} | ROI score: {manifest_revenue.get("roi_score", 0.0)}</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="card">
      <h2 style="margin-bottom:14px">⚙️ Runtime Parameters</h2>
      <div class="gov-field">
        <label>Aggressiveness Level</label>
        <select id="bot-aggressiveness">
          <option value="passive" {"selected" if cfg["aggressiveness"] == "passive" else ""}>Passive</option>
          <option value="balanced" {"selected" if cfg["aggressiveness"] == "balanced" else ""}>Balanced</option>
          <option value="aggressive" {"selected" if cfg["aggressiveness"] == "aggressive" else ""}>Aggressive</option>
          <option value="max" {"selected" if cfg["aggressiveness"] == "max" else ""}>Max</option>
        </select>
      </div>
      <div class="gov-field">
        <label>Max Execution Duration (seconds): <span id="exec-label">{cfg["max_execution_seconds"]}</span></label>
        <input type="range" id="bot-max-exec" min="30" max="3600" step="30" value="{cfg["max_execution_seconds"]}"
          oninput="document.getElementById('exec-label').textContent=this.value">
      </div>
      <div class="gov-field">
        <label>Retry Policy</label>
        <select id="bot-retry-policy">
          <option value="none" {"selected" if cfg["retry_policy"] == "none" else ""}>None</option>
          <option value="once" {"selected" if cfg["retry_policy"] == "once" else ""}>Once</option>
          <option value="twice" {"selected" if cfg["retry_policy"] == "twice" else ""}>Twice</option>
          <option value="auto" {"selected" if cfg["retry_policy"] == "auto" else ""}>Auto</option>
        </select>
      </div>
      <div style="margin-top:10px;display:flex;align-items:center;">
        <button class="save-btn" onclick="saveBotConfig()">💾 Save Parameters</button>
        <span id="save-status"></span>
      </div>
      {"<div style='margin-top:8px;font-size:0.72rem;color:#555'>Using global defaults (not customised)</div>" if not cfg["custom"] else "<div style='margin-top:8px;font-size:0.72rem;color:#00d4aa'>✓ Custom parameters active</div>"}
    </div>
  </div>

  <div class="section">
    <div class="card">
      <h2 style="margin-bottom:10px">🚨 Recent Failures</h2>
      <table>
        <thead><tr><th>Time</th><th>Type</th><th>Message</th></tr></thead>
        <tbody>{failure_rows}</tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="card">
      <h2 style="margin-bottom:10px">📜 Run History</h2>
      <table>
        <thead><tr><th>Time</th><th>Status</th><th>Notes</th></tr></thead>
        <tbody>{history_rows}</tbody>
      </table>
    </div>
  </div>

  <footer>DreamCo Empire OS — {display_name} Bot Dashboard</footer>

  <script>
    async function saveBotConfig() {{
      const statusEl = document.getElementById('save-status');
      statusEl.textContent = '⏳ Saving…';
      try {{
        const payload = {{
          aggressiveness: document.getElementById('bot-aggressiveness').value,
          max_execution_seconds: parseInt(document.getElementById('bot-max-exec').value, 10),
          retry_policy: document.getElementById('bot-retry-policy').value,
        }};
        const res = await fetch('/api/bots/{bot_name}/configure', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        if (res.ok) {{
          statusEl.textContent = '✅ Saved!';
          setTimeout(() => {{ statusEl.textContent = ''; }}, 3000);
        }} else {{
          statusEl.textContent = '⚠ Error';
        }}
      }} catch (e) {{
        statusEl.textContent = '⚠ Network error';
      }}
    }}
  </script>
</body>
</html>"""
        return Response(html, mimetype="text/html")

    return app


__all__ = [
    "create_app",
    "_BOT_CATALOG",
    "_fetch_github_workflows",
    "_fetch_github_artifacts",
    "_check_quantum_bot_status",
    "_get_governance",
    "_update_governance",
    "_get_bot_config",
    "_set_bot_config",
    "_append_failure",
    "_get_failures",
    "_detect_uncoded_bots",
    "_build_runtime_registry",
    "_build_runtime_overview",
]
