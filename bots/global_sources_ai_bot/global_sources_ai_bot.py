"""
GlobalSourcesAIBot — Universal AI Model Router & Collaboration System

This bot implements the BuddyAI Universal AI Collaboration System described
in the DreamCo problem statement.  It layers on top of — and never replaces —
the existing Dreamcobots GLOBAL AI SOURCES FLOW framework pipeline.

Architecture (10 layers from the problem statement)
----------------------------------------------------
Layer 1  Master Orchestrator  — decides which AI to use for every task
Layer 2  AI Router            — scores cost/speed/accuracy/creativity
Layer 3  Buddy Intelligence Memory — learning from routing outcomes
Layer 4  Universal Collaboration Engine — cross-ecosystem partnerships
Layer 5  Continuous Benchmarking — daily model scoring cycles
Layer 6  Buddy Marketplace — catalog of bots/agents/templates
Layer 7  Self-Improvement Engine — autonomous model discovery
Layer 8  Multi-Agent Workforce — CEO / CTO / Sales / Finance agents
Layer 9  Universal API Hub — developer-facing endpoints
Layer 10 DreamCo Ecosystem Integration — ties to all DreamCo products

Strategic Rules (hardcoded)
---------------------------
1  Never rely on one AI provider
2  Always benchmark
3  Open ecosystem > closed ecosystem
4  Best model handles the task
5  Memory compounds value
6  Automate improvement itself
7  Collaborate before competing

GLOBAL AI SOURCES FLOW: This bot integrates with the Dreamcobots GLOBAL AI
SOURCES FLOW framework via GlobalAISourcesFlow.run_pipeline() so that every
routing decision is traceable through the full 8-stage pipeline.
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# ── CRITICAL: existing framework import (must not be removed) ────────────────
from framework import GlobalAISourcesFlow  # GLOBAL AI SOURCES FLOW

from bots.global_sources_ai_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    FEATURE_FULL_ROUTING,
    FEATURE_BENCHMARKING,
    FEATURE_CUSTOM_API_KEYS,
    FEATURE_AUTONOMOUS_UPGRADE,
    FEATURE_MULTI_AGENT,
    FEATURE_COLLABORATION_ENGINE,
    FEATURE_REAL_TIME_BENCHMARK,
    FEATURE_API_ACCESS,
)
from bots.global_sources_ai_bot.model_registry import (
    AIModel,
    UseCase,
    TOP_100_AI_MODELS,
    TOP_100_USE_CASES,
)
from bots.global_sources_ai_bot.task_router import TaskRouter, RoutingConfig, RoutingResult
from bots.global_sources_ai_bot.benchmarks import BenchmarkEngine


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class GlobalSourcesBotError(Exception):
    """Base exception for the GlobalSourcesAIBot."""


class GlobalSourcesBotTierError(GlobalSourcesBotError):
    """Raised when a requested feature requires a higher tier."""


# ---------------------------------------------------------------------------
# Multi-Agent Workforce department specs
# ---------------------------------------------------------------------------

DEPARTMENTS: dict[str, dict[str, Any]] = {
    "ceo":        {"name": "CEO Agent",        "primary_model": "chatgpt",   "specialty": ["decision", "strategy", "business"]},
    "cto":        {"name": "CTO Agent",         "primary_model": "claude_code","specialty": ["coding", "architecture", "deployment"]},
    "sales":      {"name": "Sales Agent",       "primary_model": "chatgpt",   "specialty": ["sales", "crm", "outreach"]},
    "finance":    {"name": "Finance Agent",     "primary_model": "bloomberg_gpt","specialty": ["finance", "forecasting", "investing"]},
    "legal":      {"name": "Legal Agent",       "primary_model": "harvey_ai", "specialty": ["legal", "contracts", "compliance"]},
    "marketing":  {"name": "Marketing Agent",   "primary_model": "jasper",    "specialty": ["marketing", "seo", "advertising"]},
    "research":   {"name": "Research Agent",    "primary_model": "perplexity","specialty": ["research", "analysis", "science"]},
    "automation": {"name": "Automation Agent",  "primary_model": "zapier_ai", "specialty": ["automation", "workflow", "integration"]},
    "security":   {"name": "Security Agent",    "primary_model": "crowdstrike_ai","specialty": ["cybersecurity", "fraud_detection", "security"]},
    "hiring":     {"name": "Hiring Agent",      "primary_model": "chatgpt",   "specialty": ["recruiting", "hr", "interview"]},
}


# ---------------------------------------------------------------------------
# Main GlobalSourcesAIBot class
# ---------------------------------------------------------------------------

class GlobalSourcesAIBot:
    """
    Universal AI Model Router and BuddyAI Collaboration System.

    This bot:
    • Routes every task to the globally best AI model using a live benchmark-
      weighted scoring engine (Layer 1 & 2).
    • Runs through all 8 stages of the existing GlobalAISourcesFlow pipeline
      so every decision is fully traceable (GLOBAL AI SOURCES FLOW compliance).
    • Maintains a memory of routing outcomes for compound learning (Layer 3).
    • Provides a cross-ecosystem collaboration catalog (Layer 4).
    • Benchmarks all 100 global AI models continuously (Layer 5).
    • Exposes a marketplace of use-case templates (Layer 6).
    • Autonomously discovers and tests new models (Layer 7, PRO/ENTERPRISE).
    • Manages a 10-department multi-agent workforce (Layer 8, ENTERPRISE).
    • Exposes a universal API hub (Layer 9, ENTERPRISE).
    • Integrates with all DreamCo products (Layer 10).

    Tiers
    -----
    FREE ($0)         5 categories, top-3 models, basic routing
    PRO ($49)         All 100 categories, top-10 models, benchmarking
    ENTERPRISE ($199) All features, multi-agent workforce, custom API keys
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self._tier = tier
        self._tier_config: TierConfig = get_tier_config(tier)

        # Existing GlobalAISourcesFlow pipeline — never modified, always present
        self._flow = GlobalAISourcesFlow(bot_name="GlobalSourcesAIBot")

        # Benchmark engine (Layer 5)
        self._benchmark = BenchmarkEngine()

        # Task router (Layer 2) — seeded with default benchmark scores
        self._router = TaskRouter(
            config=RoutingConfig(top_k=self._tier_config.max_models_per_task),
            benchmark_scores=self._benchmark.scores_for_router(),
        )

        # Routing memory (Layer 3) — stores outcomes for compound learning
        self._memory: list[dict[str, Any]] = []

        # Collaboration partners catalog (Layer 4)
        self._collaboration_catalog = self._build_collaboration_catalog()

        # Discovered models awaiting sandbox testing (Layer 7)
        self._pending_discovery: list[dict[str, Any]] = []

    # ── Tier gate ─────────────────────────────────────────────────────────

    def _require_feature(self, feature: str, friendly_name: str) -> None:
        if not self._tier_config.has_feature(feature):
            raise GlobalSourcesBotTierError(
                f"'{friendly_name}' requires {feature!r}. "
                f"Upgrade from {self._tier.value.upper()} to unlock."
            )

    # =========================================================================
    # Layer 1 + 2 — Master Orchestrator & AI Router
    # =========================================================================

    def route_task(self, task: str, top_k: Optional[int] = None) -> dict[str, Any]:
        """
        Route *task* to the best AI model, running the full GlobalAISourcesFlow
        pipeline so the decision is traceable end-to-end.

        Parameters
        ----------
        task : str
            Free-text description of the work to do.
        top_k : int, optional
            Override the tier default for number of candidate models returned.

        Returns
        -------
        dict with keys:
            primary_model, ranked_models, use_cases, reasoning,
            pipeline_trace (the full 8-stage flow result)
        """
        # Sync router with latest benchmark scores
        self._router = TaskRouter(
            config=RoutingConfig(top_k=top_k or self._tier_config.max_models_per_task),
            benchmark_scores=self._benchmark.scores_for_router(),
        )

        result: RoutingResult = self._router.route(task, top_k=top_k)

        # Enforce category limit on FREE tier
        if (self._tier_config.max_categories is not None and
                len(result.matched_use_cases) > self._tier_config.max_categories):
            result.matched_use_cases = result.matched_use_cases[:self._tier_config.max_categories]

        # Run through the existing GlobalAISourcesFlow pipeline (Layer 10 compliance)
        pipeline_trace = self._flow.run_pipeline(
            raw_data={
                "task": task,
                "primary_model": result.primary_model.model_id if result.primary_model else None,
                "tags": result.tags_used,
            },
            learning_method="supervised",
        )

        # Store outcome in memory (Layer 3)
        self._remember(task, result)

        return {
            "task": task,
            "primary_model": {
                "id": result.primary_model.model_id,
                "name": result.primary_model.display_name,
                "provider": result.primary_model.provider,
                "type": result.primary_model.model_type,
                "api_endpoint": result.primary_model.api_endpoint_hint,
                "cost_tier": result.primary_model.cost_tier,
                "open_source": result.primary_model.is_open_source,
                "strengths": result.primary_model.strengths,
            } if result.primary_model else None,
            "ranked_models": [
                {"model_id": mid, "score": round(score, 4)}
                for mid, score in result.ranked_models
            ],
            "matched_use_cases": [
                {"id": uc.id, "name": uc.name, "tags": uc.tags}
                for uc in result.matched_use_cases
            ],
            "reasoning": result.reasoning,
            "pipeline_trace": pipeline_trace,
        }

    def route_batch(self, tasks: list[str]) -> list[dict[str, Any]]:
        """Route a list of tasks, returning one result dict per task."""
        return [self.route_task(t) for t in tasks]

    # =========================================================================
    # Layer 3 — Buddy Intelligence Memory
    # =========================================================================

    def _remember(self, task: str, result: RoutingResult) -> None:
        """Store a routing outcome in memory for compound learning."""
        self._memory.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_snippet": task[:120],
            "primary_model": result.primary_model.model_id if result.primary_model else None,
            "tags": result.tags_used,
            "use_case_ids": [uc.id for uc in result.matched_use_cases],
        })

    def memory_summary(self) -> dict[str, Any]:
        """Return aggregate routing memory statistics."""
        if not self._memory:
            return {"total_routed": 0, "model_frequency": {}, "top_use_cases": []}

        model_freq: dict[str, int] = {}
        uc_freq: dict[int, int] = {}
        for entry in self._memory:
            pm = entry.get("primary_model")
            if pm:
                model_freq[pm] = model_freq.get(pm, 0) + 1
            for uc_id in entry.get("use_case_ids", []):
                uc_freq[uc_id] = uc_freq.get(uc_id, 0) + 1

        top_uc = sorted(uc_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_routed": len(self._memory),
            "model_frequency": dict(sorted(model_freq.items(), key=lambda x: x[1], reverse=True)),
            "top_use_cases": [{"use_case_id": uid, "count": cnt} for uid, cnt in top_uc],
        }

    # =========================================================================
    # Layer 4 — Universal Collaboration Engine
    # =========================================================================

    def collaboration_catalog(self) -> dict[str, Any]:
        """
        Return the cross-ecosystem collaboration catalog.

        FREE tier sees partner summary only.
        PRO/ENTERPRISE see full integration metadata.
        """
        if not self._tier_config.has_feature(FEATURE_COLLABORATION_ENGINE):
            return {"partners": list(self._collaboration_catalog.keys()), "details": "Upgrade to PRO"}
        return {"partners": self._collaboration_catalog}

    @staticmethod
    def _build_collaboration_catalog() -> dict[str, dict[str, Any]]:
        return {
            "OpenAI":       {"type": "api_federation", "models": ["chatgpt", "claude_code", "dalle3", "sora"],
                             "endpoint": "https://api.openai.com/v1"},
            "Anthropic":    {"type": "api_federation", "models": ["claude", "claude_code"],
                             "endpoint": "https://api.anthropic.com/v1"},
            "Google":       {"type": "api_federation", "models": ["gemini", "gemini_code", "veo", "alphafold"],
                             "endpoint": "https://generativelanguage.googleapis.com/v1beta"},
            "Meta":         {"type": "open_source_sync", "models": ["llama", "meta_ai"],
                             "endpoint": "https://huggingface.co/meta-llama"},
            "NVIDIA":       {"type": "partner_integration", "models": ["nvidia_isaac", "nvidia_dgx", "nvidia_omniverse"],
                             "endpoint": "https://api.nvidia.com/v1"},
            "Microsoft":    {"type": "api_federation", "models": ["ms_copilot", "azure_ai", "autogen"],
                             "endpoint": "https://api.cognitive.microsoft.com"},
            "xAI":          {"type": "api_federation", "models": ["grok"],
                             "endpoint": "https://api.x.ai/v1"},
            "Amazon":       {"type": "api_federation", "models": ["aws_bedrock", "aws_sagemaker"],
                             "endpoint": "https://bedrock.us-east-1.amazonaws.com"},
            "HuggingFace":  {"type": "open_source_sync", "models": ["llama", "mistral", "deepseek", "qwen", "gemma"],
                             "endpoint": "https://api-inference.huggingface.co"},
            "Mistral AI":   {"type": "open_source_sync", "models": ["mistral"],
                             "endpoint": "https://api.mistral.ai/v1"},
            "DeepSeek":     {"type": "open_source_sync", "models": ["deepseek"],
                             "endpoint": "https://api.deepseek.com/v1"},
            "ElevenLabs":   {"type": "plugin_marketplace", "models": ["elevenlabs"],
                             "endpoint": "https://api.elevenlabs.io/v1"},
            "Runway":       {"type": "plugin_marketplace", "models": ["runway"],
                             "endpoint": "https://api.runwayml.com/v1"},
            "Perplexity":   {"type": "api_federation", "models": ["perplexity"],
                             "endpoint": "https://api.perplexity.ai"},
            "LangChain":    {"type": "agent_to_agent", "models": ["langgraph"],
                             "endpoint": "https://api.langchain.com"},
        }

    # =========================================================================
    # Layer 5 — Continuous Benchmarking
    # =========================================================================

    def run_benchmark_cycle(
        self,
        custom_scores: Optional[dict[str, dict[str, float]]] = None,
    ) -> dict[str, Any]:
        """
        Run a benchmarking cycle and return a summary.

        PRO/ENTERPRISE only.
        """
        self._require_feature(FEATURE_BENCHMARKING, "Benchmark Cycle")
        return self._benchmark.run_daily_cycle(custom_scores)

    def benchmark_summary(self) -> dict[str, Any]:
        """Return the current benchmark summary (PRO/ENTERPRISE)."""
        self._require_feature(FEATURE_BENCHMARKING, "Benchmark Summary")
        return self._benchmark.summary()

    def top_models_by_dimension(self, dimension: str, n: int = 10) -> list[tuple[str, float]]:
        """Rank models by a specific benchmark dimension (PRO/ENTERPRISE)."""
        self._require_feature(FEATURE_BENCHMARKING, "Dimension Ranking")
        return self._benchmark.rank_by_dimension(dimension, n)

    # =========================================================================
    # Layer 6 — Buddy Marketplace
    # =========================================================================

    def marketplace_catalog(self) -> dict[str, Any]:
        """
        Return the marketplace catalog of use-case templates and bot categories.
        """
        categories: dict[str, list[dict]] = {}
        for uc in TOP_100_USE_CASES:
            primary_tag = uc.tags[0] if uc.tags else "general"
            categories.setdefault(primary_tag, []).append({
                "id": uc.id,
                "name": uc.name,
                "description": uc.description,
                "top_models": uc.top_models[:3],
            })
        return {
            "marketplace_version": "1.0",
            "total_use_cases": len(TOP_100_USE_CASES),
            "total_models": len(TOP_100_AI_MODELS),
            "categories": categories,
        }

    # =========================================================================
    # Layer 7 — Self-Improvement Engine
    # =========================================================================

    def discover_model(self, model_id: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Queue a newly discovered model for sandbox testing (PRO/ENTERPRISE).

        Step 1 of the autonomous upgrade loop:
        discover → sandbox_test → benchmark → compare → deploy if superior
        """
        self._require_feature(FEATURE_AUTONOMOUS_UPGRADE, "Model Discovery")
        entry = {
            "model_id": model_id,
            "metadata": metadata,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending_sandbox",
        }
        self._pending_discovery.append(entry)
        return {"queued": True, "entry": entry}

    def sandbox_test_pending(self) -> list[dict[str, Any]]:
        """
        Run sandbox tests on all pending discovered models (ENTERPRISE).

        In production this calls the GlobalAISourcesFlow sandbox stage.
        Returns the list of processed entries.
        """
        self._require_feature(FEATURE_AUTONOMOUS_UPGRADE, "Sandbox Testing")
        processed = []
        still_pending = []
        for entry in self._pending_discovery:
            # Route through the framework's sandbox stage
            sandbox_result = self._flow.sandbox.run_tests(
                {"model_id": entry["model_id"], "metadata": entry["metadata"]}
            )
            if sandbox_result.get("passed", False):
                entry["status"] = "sandbox_passed"
                # Register preliminary benchmark scores
                self._benchmark.update(entry["model_id"], {
                    "accuracy": 0.5, "speed": 0.5, "cost_score": 0.5,
                    "creativity": 0.5, "reliability": 0.5,
                    "context_score": 0.5, "safety": 0.5,
                })
                processed.append(entry)
            else:
                entry["status"] = "sandbox_failed"
                still_pending.append(entry)
        self._pending_discovery = still_pending
        return processed

    def pending_discoveries(self) -> list[dict[str, Any]]:
        """Return list of models awaiting sandbox testing."""
        self._require_feature(FEATURE_AUTONOMOUS_UPGRADE, "Pending Discoveries")
        return list(self._pending_discovery)

    # =========================================================================
    # Layer 8 — Multi-Agent Workforce
    # =========================================================================

    def multi_agent_workforce(self) -> dict[str, Any]:
        """
        Return the multi-agent workforce configuration (ENTERPRISE).

        Each department has a specialized model, shared memory pointer, and
        reporting line to the orchestration layer.
        """
        self._require_feature(FEATURE_MULTI_AGENT, "Multi-Agent Workforce")
        return {
            "workforce_active": True,
            "departments": DEPARTMENTS,
            "shared_memory": "Pinecone + PostgreSQL",
            "orchestration_layer": "LangGraph + CrewAI",
            "reporting": "all departments → GlobalSourcesAIBot orchestrator",
        }

    def dispatch_to_department(self, department: str, task: str) -> dict[str, Any]:
        """
        Route *task* to the appropriate department agent (ENTERPRISE).

        The department's primary model is used as the routing anchor, but the
        full scoring engine still runs to confirm or override the selection.
        """
        self._require_feature(FEATURE_MULTI_AGENT, "Department Dispatch")
        if department not in DEPARTMENTS:
            raise GlobalSourcesBotError(
                f"Unknown department '{department}'. "
                f"Valid: {list(DEPARTMENTS.keys())}"
            )
        dept = DEPARTMENTS[department]
        # Route the task using the full engine (may choose a different model
        # if it scores higher than the department default)
        routing = self.route_task(f"{department} task: {task}")
        routing["department"] = dept["name"]
        routing["department_default_model"] = dept["primary_model"]
        return routing

    # =========================================================================
    # Layer 9 — Universal API Hub
    # =========================================================================

    def api_hub_info(self) -> dict[str, Any]:
        """
        Return the Universal API Hub endpoint catalogue (ENTERPRISE).
        """
        self._require_feature(FEATURE_API_ACCESS, "Universal API Hub")
        return {
            "api_version": "1.0",
            "base_url": "https://api.dreamcobots.ai/v1",
            "endpoints": {
                "POST /route":             "Route a task to the best model",
                "POST /route/batch":       "Route multiple tasks",
                "GET  /models":            "List all 100 registered AI models",
                "GET  /use-cases":         "List all 100 use-case categories",
                "GET  /benchmarks":        "Current benchmark scores",
                "POST /benchmarks/cycle":  "Trigger a benchmark cycle",
                "GET  /collaboration":     "Cross-ecosystem partner catalog",
                "GET  /marketplace":       "Use-case marketplace catalog",
                "POST /discover":          "Queue a new model for discovery",
                "GET  /workforce":         "Multi-agent workforce config",
                "POST /workforce/dispatch":"Dispatch task to a department",
                "GET  /memory":            "Routing memory summary",
                "GET  /status":            "System status",
            },
            "auth": "Bearer token (API key from DeveloperSettings)",
            "rate_limits": {
                "FREE": "100 requests/day",
                "PRO": "10,000 requests/day",
                "ENTERPRISE": "unlimited",
            },
        }

    # =========================================================================
    # Layer 10 — DreamCo Ecosystem Integration
    # =========================================================================

    def ecosystem_status(self) -> dict[str, Any]:
        """
        Return the integration status with all DreamCo products.
        """
        return {
            "products": {
                "DreamSalesPro":       {"model_router": True,  "agent": "sales"},
                "DreamRealEstate":     {"model_router": True,  "agent": "ceo"},
                "DreamFinance":        {"model_router": True,  "agent": "finance"},
                "AutoBotFactory":      {"model_router": True,  "agent": "cto"},
                "AIMarketplace":       {"model_router": True,  "catalog": "marketplace_catalog"},
                "DivisionDashboard":   {"model_router": True,  "benchmarks": "benchmark_summary"},
                "BusinessLaunchPad":   {"model_router": True,  "agent": "ceo"},
                "ControlTower":        {"model_router": True,  "status": "ecosystem_status"},
                "GlobalAILearning":    {"model_router": True,  "benchmarks": True},
                "GlobalBotNetwork":    {"model_router": True,  "collaboration": True},
            },
            "framework_version": "GlobalAISourcesFlow v1.0.0",
            "tier": self._tier.value,
            "active_since": datetime.now(timezone.utc).isoformat(),
        }

    # =========================================================================
    # Convenience / status
    # =========================================================================

    def list_all_models(self) -> list[dict[str, Any]]:
        """Return metadata for all 100 registered AI models."""
        return [
            {
                "model_id": m.model_id,
                "name": m.display_name,
                "provider": m.provider,
                "type": m.model_type,
                "strengths": m.strengths,
                "cost_tier": m.cost_tier,
                "open_source": m.is_open_source,
                "api_endpoint": m.api_endpoint_hint,
            }
            for m in TOP_100_AI_MODELS.values()
        ]

    def list_all_use_cases(self) -> list[dict[str, Any]]:
        """Return all 100 use-case categories."""
        return [
            {
                "id": uc.id,
                "name": uc.name,
                "description": uc.description,
                "tags": uc.tags,
                "top_models": uc.top_models,
            }
            for uc in TOP_100_USE_CASES
        ]

    def status(self) -> dict[str, Any]:
        """High-level system status."""
        return {
            "bot": "GlobalSourcesAIBot",
            "tier": self._tier.value,
            "tier_price_usd_monthly": self._tier_config.price_usd_monthly,
            "registered_models": len(TOP_100_AI_MODELS),
            "use_cases": len(TOP_100_USE_CASES),
            "routing_memory_size": len(self._memory),
            "pending_discoveries": len(self._pending_discovery),
            "pipeline": "GlobalAISourcesFlow v1.0.0 — 8 stages active",
            "strategic_rules": [
                "Never rely on one AI provider",
                "Always benchmark",
                "Open ecosystem > closed ecosystem",
                "Best model handles the task",
                "Memory compounds value",
                "Automate improvement itself",
                "Collaborate before competing",
            ],
        }

    def __repr__(self) -> str:
        return (
            f"GlobalSourcesAIBot(tier={self._tier.value!r}, "
            f"models={len(TOP_100_AI_MODELS)}, "
            f"use_cases={len(TOP_100_USE_CASES)})"
        )
