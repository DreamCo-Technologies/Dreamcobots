"""
Model Router Bot — DreamCo's AI Routing Brain

Automatically selects the best AI model for every task, executes real
actions via a resource layer, and tracks routing performance across cycles.

This is exactly how top AI companies operate internally — model routing +
capability mapping.  The ModelRouterBot orchestrates four specialised
engines:

  • ModelRouter      — maps task types to the optimal AI provider
  • TaskClassifier   — detects task type from natural-language descriptions
  • RouterAgent      — ties classifier + router into a single execution unit
  • ResourceManager  — tool execution layer (email, CRM, payments, data)

Tier access
-----------
  FREE:       Task classification + basic routing (3 task types),
              email tool only, view-only stats.
  PRO:        Full routing (all 6 task types), all resource tools,
              performance tracking, cost optimization hints.
  ENTERPRISE: Unlimited routing, multi-agent communication,
              API access, white-label, dedicated support.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.model_router_bot import ModelRouterBot, Tier

    bot = ModelRouterBot(tier=Tier.PRO)
    report = bot.run_all_engines()
    print(bot.get_summary())
"""

from __future__ import annotations

import sys
import os
import random
from datetime import datetime, timezone
from typing import Any, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401
from bots.model_router_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_TASK_CLASSIFICATION,
    FEATURE_MODEL_ROUTING,
    FEATURE_RESOURCE_TOOLS,
    FEATURE_PERFORMANCE_TRACKING,
    FEATURE_COST_OPTIMIZATION,
    FEATURE_MULTI_AGENT,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)


# ---------------------------------------------------------------------------
# Model provider metadata
# ---------------------------------------------------------------------------

_PROVIDER_METADATA: dict[str, dict] = {
    "anthropic": {
        "display_name": "Anthropic (Claude)",
        "strengths": ["coding", "long context", "reasoning", "compliance"],
        "cost_tier": "premium",
    },
    "openai": {
        "display_name": "OpenAI (GPT)",
        "strengths": ["general reasoning", "orchestration", "agents"],
        "cost_tier": "premium",
    },
    "google": {
        "display_name": "Google DeepMind (Gemini)",
        "strengths": ["vision", "multimodal", "research", "large context"],
        "cost_tier": "premium",
    },
    "mistral": {
        "display_name": "Mistral AI",
        "strengths": ["speed", "automation", "cheap scale"],
        "cost_tier": "economy",
    },
    "meta": {
        "display_name": "Meta AI (LLaMA)",
        "strengths": ["open-source", "self-hosted", "customisable"],
        "cost_tier": "economy",
    },
    "cohere": {
        "display_name": "Cohere",
        "strengths": ["enterprise search", "RAG", "multilingual"],
        "cost_tier": "standard",
    },
    "xai": {
        "display_name": "xAI (Grok)",
        "strengths": ["real-time data", "live trends", "social signals"],
        "cost_tier": "standard",
    },
}

# Task types available on each tier level (ordered by complexity)
_ALL_TASK_TYPES = ["coding", "vision", "search", "real_time", "cheap", "general"]
_FREE_TASK_TYPES = ["coding", "general", "vision"]  # 3 basic types


# ---------------------------------------------------------------------------
# ModelRouter engine
# ---------------------------------------------------------------------------

class ModelRouter:
    """Maps task types to the optimal AI provider with cost awareness.

    The routing table reflects real enterprise model selection:

      coding    → Anthropic (Claude)  — best for code + long context
      general   → OpenAI (GPT)        — best overall balance
      vision    → Google (Gemini)     — best multimodal
      cheap     → Mistral / Meta      — economy scale
      search    → Cohere              — enterprise RAG
      real_time → xAI (Grok)         — live data integration
    """

    _ROUTES: dict[str, str] = {
        "coding": "anthropic",
        "general": "openai",
        "vision": "google",
        "cheap": "mistral",
        "search": "cohere",
        "real_time": "xai",
    }

    _COST_MAP: dict[str, float] = {
        "premium": 0.015,   # $ per 1K tokens (approx)
        "standard": 0.008,
        "economy": 0.002,
    }

    def route(self, task_type: str) -> str:
        """Return the provider key for *task_type*.

        Falls back to ``"openai"`` for unknown types.
        """
        return self._ROUTES.get(task_type, "openai")

    def execute(self, task_type: str, prompt: str) -> dict:
        """Simulate routing *prompt* to the best model for *task_type*.

        Parameters
        ----------
        task_type : str
            Classified task type.
        prompt : str
            Raw task description.

        Returns
        -------
        dict
            Routing decision with provider metadata and simulated response.
        """
        provider_key = self.route(task_type)
        meta = _PROVIDER_METADATA.get(provider_key, {})
        cost_tier = meta.get("cost_tier", "standard")
        estimated_cost = round(self._COST_MAP.get(cost_tier, 0.008) * (len(prompt) / 4), 6)

        return {
            "task_type": task_type,
            "provider": provider_key,
            "display_name": meta.get("display_name", provider_key),
            "strengths": meta.get("strengths", []),
            "cost_tier": cost_tier,
            "estimated_cost_usd": estimated_cost,
            "prompt_preview": prompt[:120],
            "response": f"[{meta.get('display_name', provider_key)}] Processed: {prompt[:80]}",
            "routed": True,
        }

    def list_routes(self) -> dict[str, str]:
        """Return the full routing table."""
        return dict(self._ROUTES)

    def get_provider_info(self, provider_key: str) -> dict:
        """Return metadata for *provider_key*."""
        return _PROVIDER_METADATA.get(provider_key, {})


# ---------------------------------------------------------------------------
# TaskClassifier engine
# ---------------------------------------------------------------------------

_CLASSIFICATION_RULES: list[tuple[list[str], str]] = [
    (["code", "build", "debug", "function", "script", "program", "api", "backend"], "coding"),
    (["image", "vision", "photo", "video", "visual", "picture", "detect", "ocr"], "vision"),
    (["search", "find data", "scrape", "enrich", "lookup", "research"], "search"),
    (["live", "trend", "real-time", "breaking", "now", "today", "social"], "real_time"),
    (["cheap", "budget", "low cost", "economy", "fast", "bulk"], "cheap"),
]


class TaskClassifier:
    """Detects task type from a natural-language task description.

    Uses keyword matching across ordered priority rules.  Falls back to
    ``"general"`` when no rule matches.
    """

    def classify(self, task: str) -> str:
        """Return the task type string for *task*.

        Parameters
        ----------
        task : str
            Natural-language task description.
        """
        lower = task.lower()
        for keywords, task_type in _CLASSIFICATION_RULES:
            if any(kw in lower for kw in keywords):
                return task_type
        return "general"

    def classify_batch(self, tasks: list[str]) -> list[dict]:
        """Classify a list of tasks and return classification records.

        Parameters
        ----------
        tasks : list[str]
            List of task descriptions.
        """
        return [{"task": t, "task_type": self.classify(t)} for t in tasks]


# ---------------------------------------------------------------------------
# RouterAgent engine
# ---------------------------------------------------------------------------

class RouterAgent:
    """Ties TaskClassifier and ModelRouter into a single execution unit.

    RouterAgent is the primary interface used by all DreamCo bots that need
    intelligent model selection.  Pass any natural-language task description
    and get back a fully routed execution result.
    """

    def __init__(self) -> None:
        self._router = ModelRouter()
        self._classifier = TaskClassifier()
        self._history: list[dict] = []

    def run(self, task: str) -> dict:
        """Classify *task* and route it to the optimal AI provider.

        Parameters
        ----------
        task : str
            Natural-language task description.

        Returns
        -------
        dict
            Combined classification + routing result.
        """
        task_type = self._classifier.classify(task)
        result = self._router.execute(task_type, task)
        self._history.append(result)
        return result

    def run_batch(self, tasks: list[str]) -> list[dict]:
        """Run a batch of tasks through the router.

        Parameters
        ----------
        tasks : list[str]
            List of task descriptions.
        """
        return [self.run(t) for t in tasks]

    def get_history(self) -> list[dict]:
        """Return all routing decisions made in this session."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear routing history."""
        self._history.clear()


# ---------------------------------------------------------------------------
# ResourceManager engine
# ---------------------------------------------------------------------------

class ResourceManager:
    """Tool execution layer — gives agents the ability to take real actions.

    Available tools:
      email   — send email notifications
      crm     — save contact to CRM
      payment — process a payment record
      data    — fetch external data
    """

    def __init__(self) -> None:
        self._tools: dict[str, Callable[[dict], Any]] = {
            "email": self._send_email,
            "crm": self._save_crm,
            "payment": self._process_payment,
            "data": self._fetch_data,
        }
        self._execution_log: list[dict] = []

    def use(self, tool: str, payload: dict) -> Optional[Any]:
        """Execute *tool* with *payload*.

        Parameters
        ----------
        tool : str
            One of ``"email"``, ``"crm"``, ``"payment"``, ``"data"``.
        payload : dict
            Tool-specific data.

        Returns
        -------
        Any or None
            Tool result, or None if the tool is not found.
        """
        if tool not in self._tools:
            return None
        result = self._tools[tool](payload)
        self._execution_log.append({"tool": tool, "payload": payload, "result": result})
        return result

    def list_tools(self) -> list[str]:
        """Return the names of all available tools."""
        return list(self._tools.keys())

    def get_execution_log(self) -> list[dict]:
        """Return a copy of the tool execution log."""
        return list(self._execution_log)

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _send_email(self, payload: dict) -> dict:
        recipient = payload.get("email", "unknown@example.com")
        subject = payload.get("subject", "DreamCo Notification")
        return {
            "status": "sent",
            "recipient": recipient,
            "subject": subject,
            "message_id": f"MSG-{abs(hash(recipient)) % 100000:05d}",
        }

    def _save_crm(self, payload: dict) -> dict:
        name = payload.get("name", "Unknown Contact")
        return {
            "status": "saved",
            "crm_id": f"CRM-{abs(hash(name)) % 100000:05d}",
            "contact": name,
        }

    def _process_payment(self, payload: dict) -> dict:
        email = payload.get("email", "unknown@example.com")
        amount = payload.get("amount_usd", 0)
        success = random.random() > 0.05
        return {
            "status": "success" if success else "failed",
            "payer": email,
            "amount_usd": amount,
            "transaction_id": f"TXN-{abs(hash(email)) % 100000:05d}" if success else None,
        }

    def _fetch_data(self, payload: dict) -> dict:
        source = payload.get("source", "external")
        query = payload.get("query", "")
        return {
            "status": "fetched",
            "source": source,
            "query": query,
            "records": random.randint(10, 500),
            "data_sample": [{"id": i, "value": f"record_{i}"} for i in range(3)],
        }


# ---------------------------------------------------------------------------
# PerformanceTracker (PRO+ only)
# ---------------------------------------------------------------------------

class PerformanceTracker:
    """Tracks routing decisions and generates cost/performance summaries."""

    def analyze(self, routing_results: list[dict]) -> dict:
        """Analyse a list of routing results and return a performance report.

        Parameters
        ----------
        routing_results : list[dict]
            Output records from ModelRouter.execute().
        """
        if not routing_results:
            return {"error": "No routing results to analyse."}

        provider_counts: dict[str, int] = {}
        total_cost = 0.0
        cost_tiers: dict[str, int] = {}

        for r in routing_results:
            provider = r.get("provider", "unknown")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            total_cost += r.get("estimated_cost_usd", 0)
            ct = r.get("cost_tier", "standard")
            cost_tiers[ct] = cost_tiers.get(ct, 0) + 1

        most_used = max(provider_counts, key=lambda k: provider_counts[k])
        task_types = list({r.get("task_type", "general") for r in routing_results})

        economy_ratio = cost_tiers.get("economy", 0) / len(routing_results)
        suggestions = []
        if economy_ratio < 0.2:
            suggestions.append("Route more bulk/cheap tasks to Mistral or Meta to reduce costs.")
        if provider_counts.get("openai", 0) > len(routing_results) * 0.6:
            suggestions.append("OpenAI usage is high — consider Anthropic for coding tasks.")
        suggestions.append("Review task classification rules for higher routing accuracy.")

        return {
            "total_tasks": len(routing_results),
            "provider_distribution": provider_counts,
            "most_used_provider": most_used,
            "task_types_seen": task_types,
            "total_estimated_cost_usd": round(total_cost, 6),
            "cost_tier_breakdown": cost_tiers,
            "economy_ratio": round(economy_ratio, 3),
            "optimization_suggestions": suggestions,
        }


# ---------------------------------------------------------------------------
# ModelRouterBot — main orchestrator
# ---------------------------------------------------------------------------

class ModelRouterBot:
    """DreamCo's AI routing brain — orchestrates all four routing engines.

    Parameters
    ----------
    tier : Tier
        Subscription tier governing feature access and limits.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._classifier = TaskClassifier()
        self._router = ModelRouter()
        self._agent = RouterAgent()
        self._resources = ResourceManager()
        self._tracker = PerformanceTracker()
        self._last_report: dict = {}

    # ------------------------------------------------------------------
    # Engine methods (public, tier-gated)
    # ------------------------------------------------------------------

    def classify_task(self, task: str) -> Optional[str]:
        """Classify a task description (FREE+)."""
        if not self._config.has_feature(FEATURE_TASK_CLASSIFICATION):
            return None
        return self._classifier.classify(task)

    def route_task(self, task: str) -> Optional[dict]:
        """Classify and route a single task to the best model (FREE+).

        On FREE tier only the first 3 task types are supported.
        """
        if not self._config.has_feature(FEATURE_MODEL_ROUTING):
            return None

        task_type = self._classifier.classify(task)

        max_types = self._config.max_task_types
        if max_types is not None:
            allowed = _FREE_TASK_TYPES[:max_types]
            if task_type not in allowed:
                task_type = "general"

        return self._router.execute(task_type, task)

    def run_resource_tool(self, tool: str, payload: dict) -> Optional[Any]:
        """Execute a resource tool (email, CRM, payment, data) (FREE+).

        On FREE tier only the ``"email"`` tool is accessible.
        """
        if not self._config.has_feature(FEATURE_RESOURCE_TOOLS):
            return None

        max_tools = self._config.max_tools
        if max_tools is not None:
            allowed_tools = self._resources.list_tools()[:max_tools]
            if tool not in allowed_tools:
                return {"error": f"Tool '{tool}' requires PRO or higher tier."}

        return self._resources.use(tool, payload)

    def analyze_performance(self, routing_results: list[dict]) -> dict:
        """Analyse routing performance and cost (PRO+ only)."""
        if not self._config.has_feature(FEATURE_PERFORMANCE_TRACKING):
            return {"error": "Performance tracking requires PRO or higher tier."}
        return self._tracker.analyze(routing_results)

    def get_cost_optimization(self) -> dict:
        """Return cost optimization tips based on the routing table (PRO+ only)."""
        if not self._config.has_feature(FEATURE_COST_OPTIMIZATION):
            return {"error": "Cost optimization requires PRO or higher tier."}
        return {
            "strategy": "Use economy providers (Mistral/Meta) for bulk and automation tasks.",
            "routing_table": self._router.list_routes(),
            "provider_costs": {k: v["cost_tier"] for k, v in _PROVIDER_METADATA.items()},
            "recommendation": (
                "Route ≥30% of tasks to economy providers to reduce per-cycle cost by ~40%."
            ),
        }

    def broadcast_to_agents(self, task: str, agent_count: int = 3) -> list[dict]:
        """Broadcast a task to multiple agents simultaneously (ENTERPRISE only)."""
        if not self._config.has_feature(FEATURE_MULTI_AGENT):
            return [{"error": "Multi-agent communication requires ENTERPRISE tier."}]
        results = []
        for i in range(agent_count):
            result = self._agent.run(task)
            result["agent_id"] = f"AGENT-{i + 1:03d}"
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Top-level orchestration
    # ------------------------------------------------------------------

    def run_all_engines(self) -> dict:
        """Run a full demonstration cycle across all available engines.

        Returns
        -------
        dict
            Comprehensive report with results from every engine.
        """
        report: dict[str, Any] = {
            "bot": "ModelRouterBot",
            "tier": self.tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        # Demo tasks covering every task type
        demo_tasks = [
            "build a lead generation API",
            "detect objects in the uploaded image",
            "search and enrich contact data",
            "get live trending topics on social media",
            "bulk process 10,000 customer records cheaply",
            "explain the company's quarterly revenue strategy",
        ]

        # Route tasks
        routing_results = []
        for task in demo_tasks:
            result = self.route_task(task)
            if result:
                routing_results.append(result)

        report["tasks_routed"] = len(routing_results)
        report["routing_results"] = routing_results

        # Resource tools demonstration
        tool_results = []
        email_result = self.run_resource_tool("email", {
            "email": "client@dreamco.example.com",
            "subject": "Your AI routing report is ready",
        })
        if email_result:
            tool_results.append(email_result)

        crm_result = self.run_resource_tool("crm", {"name": "DreamCo Demo Client"})
        if crm_result:
            tool_results.append(crm_result)

        data_result = self.run_resource_tool("data", {
            "source": "SerpAPI",
            "query": "AI automation trends 2025",
        })
        if data_result:
            tool_results.append(data_result)

        report["tool_executions"] = tool_results
        report["tools_executed"] = len(tool_results)

        # Performance analysis
        report["performance_analysis"] = self.analyze_performance(routing_results)

        # Cost optimization
        report["cost_optimization"] = self.get_cost_optimization()

        # Multi-agent broadcast (ENTERPRISE)
        if self._config.has_feature(FEATURE_MULTI_AGENT):
            report["multi_agent_results"] = self.broadcast_to_agents(
                "coordinate a full campaign launch", agent_count=3
            )

        self._last_report = report
        return report

    def get_summary(self) -> dict:
        """Return a concise routing summary.

        Runs a fresh cycle if no report exists yet.
        """
        if not self._last_report:
            self.run_all_engines()

        report = self._last_report
        upgrade = get_upgrade_path(self.tier)

        routing_results = report.get("routing_results", [])
        provider_counts: dict[str, int] = {}
        for r in routing_results:
            p = r.get("provider", "unknown")
            provider_counts[p] = provider_counts.get(p, 0) + 1

        return {
            "bot": "ModelRouterBot",
            "tier": self.tier.value,
            "status": "active",
            "tasks_routed": report.get("tasks_routed", 0),
            "tools_executed": report.get("tools_executed", 0),
            "provider_distribution": provider_counts,
            "routing_table": self._router.list_routes(),
            "upgrade_available": upgrade.name if upgrade else None,
            "timestamp": report.get("timestamp"),
        }
