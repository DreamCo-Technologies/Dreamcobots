"""
BuddyOrchestrator — Centralized operational hub for all DreamCobots bots and systems.

Buddy orchestrates:
  • Core functions     — register, run, and monitor every bot
  • Data aggregation   — collect and unify data from all active bots
  • Revenue tracking   — aggregate revenue across the bot network
  • GitHub Actions     — read-only monitoring of workflow run status
  • Post-merge recovery — identify incomplete runs, re-trigger them,
                          and verify system consistency after merges
  • Scrape lifecycle   — enforce the June 22, 2026 data-scraping deadline

Design
------
BuddyOrchestrator intentionally avoids hard runtime imports of every bot
module so that it can be used even when optional bot dependencies are absent.
Bots are described via lightweight ``BotSpec`` descriptors and instantiated
lazily on demand.

Build-a-Bot marketplace support
--------------------------------
``list_catalog()`` returns every registered spec with pricing and feature
metadata so it can be rendered by the React Marketplace UI, compared
side-by-side, and sold via the billing layer.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_orchestrator import BuddyOrchestrator

    orch = BuddyOrchestrator()
    orch.register_bot("buddy_bot",    tier="PRO",        category="ai",       price_usd=49.0)
    orch.register_bot("sales_bot",    tier="ENTERPRISE", category="sales",    price_usd=99.0)

    result = orch.run_bot("buddy_bot", task="generate leads")
    summary = orch.aggregate_data()
    health  = orch.github_actions_status()
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.buddy_orchestrator.data_scrape_lifecycle import DataScrapeLifecycle

try:
    from framework import GlobalAISourcesFlow  # noqa: F401
    _FLOW_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FLOW_AVAILABLE = False


SWARM_ARCHITECTURE_BENCHMARKS = [
    {
        "architecture_id": "pso",
        "name": "Particle Swarm Optimization",
        "origin": "United States",
        "discipline": "computational intelligence",
        "coordination_mode": "decentralized",
        "communication_pattern": "velocity and best-position sharing",
        "marl_ready": False,
        "stigmergic": False,
        "benchmark": {
            "adaptation": 8.8,
            "scalability": 9.2,
            "resilience": 8.4,
            "monetization": 8.1,
        },
    },
    {
        "architecture_id": "aco",
        "name": "Ant Colony Optimization",
        "origin": "Italy",
        "discipline": "bio-inspired optimization",
        "coordination_mode": "stigmergic",
        "communication_pattern": "pheromone trail reinforcement",
        "marl_ready": False,
        "stigmergic": True,
        "benchmark": {
            "adaptation": 8.5,
            "scalability": 8.7,
            "resilience": 9.0,
            "monetization": 7.9,
        },
    },
    {
        "architecture_id": "abc",
        "name": "Artificial Bee Colony",
        "origin": "Turkey",
        "discipline": "swarm intelligence",
        "coordination_mode": "decentralized",
        "communication_pattern": "waggle-dance neighborhood signaling",
        "marl_ready": False,
        "stigmergic": False,
        "benchmark": {
            "adaptation": 8.3,
            "scalability": 8.6,
            "resilience": 8.7,
            "monetization": 8.0,
        },
    },
    {
        "architecture_id": "hybrid_llm_marl",
        "name": "Hybrid LLM + MARL",
        "origin": "Global",
        "discipline": "multi-agent reinforcement learning",
        "coordination_mode": "hybrid",
        "communication_pattern": "policy sharing, critics, and tool-mediated messaging",
        "marl_ready": True,
        "stigmergic": False,
        "benchmark": {
            "adaptation": 9.5,
            "scalability": 8.8,
            "resilience": 9.1,
            "monetization": 9.3,
        },
    },
]


# ---------------------------------------------------------------------------
# Bot specification descriptor (lightweight, no heavy imports)
# ---------------------------------------------------------------------------

@dataclass
class BotSpec:
    """
    Describes a bot available in the DreamCobots ecosystem.

    Used by the marketplace UI for comparison, marketing, and selling.
    """

    bot_id: str
    display_name: str
    category: str
    tier: str
    description: str = ""
    price_usd: float = 0.0
    features: list[str] = field(default_factory=list)
    module_path: str = ""
    is_live: bool = False
    coordination_mode: str = "centralized"
    optimization_strategy: str = "rule_based"
    marl_enabled: bool = False
    neighbors: list[str] = field(default_factory=list)
    stigmergic_channels: list[str] = field(default_factory=list)
    local_rules: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal run record
# ---------------------------------------------------------------------------

@dataclass
class BotRunRecord:
    """Records the outcome of a single bot execution."""

    bot_id: str
    task: str
    result: Any
    revenue_usd: float
    ran_at: str
    success: bool


# ---------------------------------------------------------------------------
# Lightweight GitHub Actions helper (no external deps required)
# ---------------------------------------------------------------------------

def _fetch_workflow_runs(
    repo: str,
    token: Optional[str] = None,
    per_page: int = 10,
) -> list[dict]:
    """
    Fetch recent GitHub Actions workflow runs for *repo*.

    Falls back gracefully to an empty list when the ``requests`` library
    is unavailable or the API call fails.
    """
    try:
        import requests as _req
    except ImportError:
        return []

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = _req.get(
            f"https://api.github.com/repos/{repo}/actions/runs",
            headers=headers,
            params={"per_page": min(100, max(1, per_page))},
            timeout=5,
        )
        if resp.status_code == 200:
            return [
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "status": r.get("status"),
                    "conclusion": r.get("conclusion"),
                    "branch": r.get("head_branch"),
                    "event": r.get("event"),
                    "run_started_at": r.get("run_started_at"),
                    "url": r.get("html_url"),
                }
                for r in resp.json().get("workflow_runs", [])
            ]
    except Exception:  # noqa: BLE001
        pass
    return []


def _rerun_workflow_run(
    repo: str,
    run_id: int,
    token: Optional[str] = None,
    failed_jobs_only: bool = True,
) -> dict:
    """
    Trigger a re-run of a GitHub Actions workflow run.

    Uses ``POST /repos/{repo}/actions/runs/{run_id}/rerun-failed-jobs``
    when *failed_jobs_only* is ``True`` (default), or
    ``POST /repos/{repo}/actions/runs/{run_id}/rerun`` for a full restart.

    Requires a GitHub token with ``actions:write`` permission.
    Falls back gracefully when the ``requests`` library is unavailable.

    Returns
    -------
    dict with keys: ``run_id``, ``triggered`` (bool), and optionally
    ``error`` (str) on failure.
    """
    try:
        import requests as _req
    except ImportError:
        return {"triggered": False, "run_id": run_id, "error": "requests library not available"}

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    endpoint = "rerun-failed-jobs" if failed_jobs_only else "rerun"
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/{endpoint}"

    try:
        resp = _req.post(url, headers=headers, timeout=10)
        if resp.status_code in (201, 204):
            return {"triggered": True, "run_id": run_id}
        return {
            "triggered": False,
            "run_id": run_id,
            "error": f"HTTP {resp.status_code}",
        }
    except Exception as exc:  # noqa: BLE001
        return {"triggered": False, "run_id": run_id, "error": str(exc)}


# ---------------------------------------------------------------------------
# BuddyOrchestrator
# ---------------------------------------------------------------------------

class OrchestratorError(Exception):
    """Raised when an orchestration operation cannot be completed."""


class BuddyOrchestrator:
    """
    Central operational hub — integrates every bot and system.

    Parameters
    ----------
    github_repo : str
        ``owner/repo`` slug for GitHub Actions monitoring.
    github_token : str | None
        Optional GitHub personal access token for authenticated API calls.
    scrape_deadline : date | None
        Override the default scraping deadline (June 22, 2026).
    """

    def __init__(
        self,
        github_repo: str = "DreamCo-Technologies/Dreamcobots",
        github_token: Optional[str] = None,
        scrape_deadline=None,
    ) -> None:
        self.github_repo = github_repo
        self._github_token = github_token or os.environ.get("GITHUB_TOKEN")

        # Registered bot catalog
        self._catalog: dict[str, BotSpec] = {}

        # Run history
        self._run_history: list[BotRunRecord] = []

        # Revenue totals per bot
        self._revenue: dict[str, float] = {}

        # Aggregated data store (key → value)
        self._data_store: dict[str, Any] = {}

        # Scraping lifecycle
        self.scrape_lifecycle = (
            DataScrapeLifecycle(deadline=scrape_deadline)
            if scrape_deadline
            else DataScrapeLifecycle()
        )

    # ------------------------------------------------------------------
    # Bot registration (build-a-bot catalog)
    # ------------------------------------------------------------------

    def register_bot(
        self,
        bot_id: str,
        display_name: str = "",
        tier: str = "FREE",
        category: str = "other",
        description: str = "",
        price_usd: float = 0.0,
        features: Optional[list[str]] = None,
        module_path: str = "",
        coordination_mode: str = "centralized",
        optimization_strategy: str = "rule_based",
        marl_enabled: bool = False,
        neighbors: Optional[list[str]] = None,
        stigmergic_channels: Optional[list[str]] = None,
        local_rules: Optional[list[str]] = None,
    ) -> BotSpec:
        """
        Register a bot in the centralized catalog.

        Idempotent — calling again updates the existing spec.

        Returns
        -------
        BotSpec
        """
        spec = BotSpec(
            bot_id=bot_id,
            display_name=display_name or bot_id.replace("_", " ").title(),
            category=category,
            tier=tier,
            description=description,
            price_usd=price_usd,
            features=features or [],
            module_path=module_path,
            coordination_mode=coordination_mode,
            optimization_strategy=optimization_strategy,
            marl_enabled=marl_enabled,
            neighbors=neighbors or [],
            stigmergic_channels=stigmergic_channels or [],
            local_rules=local_rules or [],
        )
        self._catalog[bot_id] = spec
        self.scrape_lifecycle.register_bot(bot_id)
        return spec

    def unregister_bot(self, bot_id: str) -> bool:
        """Remove a bot from the catalog.  Returns True if it existed."""
        if bot_id in self._catalog:
            del self._catalog[bot_id]
            return True
        return False

    def get_bot(self, bot_id: str) -> Optional[BotSpec]:
        """Return the BotSpec for *bot_id*, or None."""
        return self._catalog.get(bot_id)

    def list_catalog(self) -> list[dict]:
        """
        Return the full bot catalog as a list of dicts.

        Suitable for rendering the build-a-bot marketplace UI and driving
        comparisons, pricing pages, and sales flows.
        """
        return [
            {
                "bot_id": spec.bot_id,
                "display_name": spec.display_name,
                "category": spec.category,
                "tier": spec.tier,
                "description": spec.description,
                "price_usd": spec.price_usd,
                "features": spec.features,
                "is_live": spec.is_live,
                "module_path": spec.module_path,
                "coordination_mode": spec.coordination_mode,
                "optimization_strategy": spec.optimization_strategy,
                "marl_enabled": spec.marl_enabled,
                "neighbors": spec.neighbors,
                "stigmergic_channels": spec.stigmergic_channels,
                "local_rules": spec.local_rules,
                "swarm_enabled": (
                    spec.coordination_mode != "centralized"
                    or spec.marl_enabled
                    or bool(spec.stigmergic_channels)
                ),
            }
            for spec in self._catalog.values()
        ]

    # ------------------------------------------------------------------
    # Bot execution
    # ------------------------------------------------------------------

    def run_bot(
        self,
        bot_id: str,
        task: str = "",
        runner: Optional[Callable[[str, str], Any]] = None,
        revenue_usd: float = 0.0,
    ) -> dict:
        """
        Execute a bot task and record the result.

        Parameters
        ----------
        bot_id : str
            The identifier of the bot to run.
        task : str
            Description of the task to perform.
        runner : callable | None
            Optional ``(bot_id, task) → result`` callable.  If None, a
            stub result is generated.
        revenue_usd : float
            Revenue attributed to this run (for tracking purposes).

        Returns
        -------
        dict with keys: ``bot_id``, ``task``, ``result``, ``revenue_usd``,
        ``ran_at``, ``success``.
        """
        if bot_id not in self._catalog:
            raise OrchestratorError(f"Bot '{bot_id}' is not registered.")

        try:
            result = runner(bot_id, task) if runner else {"status": "stub_run", "task": task}
            success = True
        except Exception as exc:  # noqa: BLE001
            result = {"error": str(exc)}
            success = False

        ran_at = datetime.now(tz=timezone.utc).isoformat()
        record = BotRunRecord(
            bot_id=bot_id,
            task=task,
            result=result,
            revenue_usd=revenue_usd,
            ran_at=ran_at,
            success=success,
        )
        self._run_history.append(record)

        # Revenue tracking
        self._revenue[bot_id] = self._revenue.get(bot_id, 0.0) + revenue_usd

        # Record scrape activity
        if success:
            self.scrape_lifecycle.record_scrape(bot_id)

        return {
            "bot_id": bot_id,
            "task": task,
            "result": result,
            "revenue_usd": revenue_usd,
            "ran_at": ran_at,
            "success": success,
        }

    def run_all(self, runner: Optional[Callable[[str, str], Any]] = None) -> list[dict]:
        """Run every registered bot with no specific task.  Returns a list of results."""
        return [self.run_bot(bot_id, runner=runner) for bot_id in list(self._catalog)]

    # ------------------------------------------------------------------
    # Data aggregation
    # ------------------------------------------------------------------

    def ingest(self, key: str, value: Any) -> None:
        """Store an arbitrary data point in the central data store."""
        self._data_store[key] = value

    def aggregate_data(self) -> dict:
        """
        Return a unified data snapshot across all systems.

        Includes:
          - Bot catalog size and live count
          - Run history summary
          - Revenue totals
          - Scraping lifecycle status
          - Arbitrary ingested data
        """
        total_runs = len(self._run_history)
        successful_runs = sum(1 for r in self._run_history if r.success)
        total_revenue = sum(self._revenue.values())
        live_bots = sum(1 for s in self._catalog.values() if s.is_live)
        coordination_modes: dict[str, int] = {}
        marl_enabled_bots = 0
        stigmergic_bots = 0
        swarm_enabled_bots = 0
        for spec in self._catalog.values():
            coordination_modes[spec.coordination_mode] = (
                coordination_modes.get(spec.coordination_mode, 0) + 1
            )
            if spec.marl_enabled:
                marl_enabled_bots += 1
            if spec.stigmergic_channels:
                stigmergic_bots += 1
            if (
                spec.coordination_mode != "centralized"
                or spec.marl_enabled
                or spec.stigmergic_channels
            ):
                swarm_enabled_bots += 1

        return {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "bots": {
                "registered": len(self._catalog),
                "live": live_bots,
            },
            "runs": {
                "total": total_runs,
                "successful": successful_runs,
                "failed": total_runs - successful_runs,
            },
            "revenue": {
                "total_usd": round(total_revenue, 2),
                "by_bot": {k: round(v, 2) for k, v in self._revenue.items()},
            },
            "scraping": self.scrape_lifecycle.summary(),
            "swarm": {
                "governance_model": "BuddyAI command center with decentralized execution",
                "coordination_modes": coordination_modes,
                "swarm_enabled_bots": swarm_enabled_bots,
                "marl_enabled_bots": marl_enabled_bots,
                "stigmergic_bots": stigmergic_bots,
                "benchmark_report": self.swarm_benchmark_report(),
            },
            "data_store": dict(self._data_store),
        }

    def swarm_benchmark_report(self) -> dict:
        """Return benchmark metadata for the supported swarm architectures."""
        ranked = []
        for architecture in SWARM_ARCHITECTURE_BENCHMARKS:
            benchmark = architecture.get("benchmark", {})
            values = [value for value in benchmark.values() if isinstance(value, (int, float))]
            overall_score = round(sum(values) / len(values), 2) if values else 0.0
            ranked.append({
                **architecture,
                "overall_score": overall_score,
            })
        ranked.sort(key=lambda item: item["overall_score"], reverse=True)
        return {
            "architectures": ranked,
            "best_overall": ranked[0]["architecture_id"] if ranked else None,
            "marl_ready_architectures": [
                item["architecture_id"] for item in ranked if item["marl_ready"]
            ],
            "stigmergic_architectures": [
                item["architecture_id"] for item in ranked if item["stigmergic"]
            ],
            "evaluation_dimensions": [
                "adaptation",
                "scalability",
                "resilience",
                "monetization",
            ],
        }

    # ------------------------------------------------------------------
    # Revenue optimisation
    # ------------------------------------------------------------------

    def top_revenue_bots(self, n: int = 5) -> list[dict]:
        """Return the *n* bots with the highest total revenue, descending."""
        ranked = sorted(self._revenue.items(), key=lambda kv: kv[1], reverse=True)
        return [
            {"bot_id": bot_id, "revenue_usd": round(rev, 2)}
            for bot_id, rev in ranked[:n]
        ]

    def optimise_revenue(self) -> dict:
        """
        Analyse revenue data and return actionable optimisation suggestions.

        Returns
        -------
        dict with keys: ``top_bots``, ``suggestions``, ``total_revenue_usd``.
        """
        top = self.top_revenue_bots()
        total = round(sum(self._revenue.values()), 2)
        zero_revenue = [bid for bid, rev in self._revenue.items() if rev == 0]
        inactive = [bid for bid, spec in self._catalog.items() if not spec.is_live]

        suggestions = []
        if top:
            suggestions.append(
                f"Double down on '{top[0]['bot_id']}' — highest revenue generator."
            )
        if zero_revenue:
            suggestions.append(
                f"{len(zero_revenue)} bot(s) have zero revenue — review their configurations."
            )
        if inactive:
            suggestions.append(
                f"{len(inactive)} bot(s) are not live — deploy them to start earning."
            )
        if not suggestions:
            suggestions.append("All bots are performing well — consider adding new bots.")

        return {
            "total_revenue_usd": total,
            "top_bots": top,
            "suggestions": suggestions,
        }

    # ------------------------------------------------------------------
    # GitHub Actions monitoring
    # ------------------------------------------------------------------

    def github_actions_status(self, per_page: int = 10) -> dict:
        """
        Return recent GitHub Actions workflow runs for the configured repo.

        Read-only — never triggers or modifies any workflow.

        Returns
        -------
        dict with keys: ``repo``, ``runs`` (list), ``source``.
        """
        runs = _fetch_workflow_runs(
            repo=self.github_repo,
            token=self._github_token,
            per_page=per_page,
        )
        source = "github_api" if runs else "unavailable"
        return {
            "repo": self.github_repo,
            "runs": runs,
            "source": source,
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Post-merge recovery — identify, re-trigger, and verify
    # ------------------------------------------------------------------

    def find_incomplete_runs(self, per_page: int = 30) -> dict:
        """
        Identify GitHub Actions workflow runs that did not complete successfully.

        A run is considered incomplete when its conclusion is one of:
        ``failure``, ``cancelled``, ``timed_out``, ``action_required``, or
        the run is still active (``in_progress``, ``queued``, ``requested``,
        ``waiting``).

        Returns
        -------
        dict with keys: ``repo``, ``incomplete_runs`` (list),
        ``total_checked`` (int), ``fetched_at`` (ISO-8601 str).
        """
        runs = _fetch_workflow_runs(
            repo=self.github_repo,
            token=self._github_token,
            per_page=per_page,
        )
        incomplete_conclusions = {"failure", "cancelled", "timed_out", "action_required"}
        incomplete_statuses = {"in_progress", "queued", "requested", "waiting"}
        incomplete = [
            r for r in runs
            if r.get("conclusion") in incomplete_conclusions
            or r.get("status") in incomplete_statuses
        ]
        return {
            "repo": self.github_repo,
            "incomplete_runs": incomplete,
            "total_checked": len(runs),
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    def rerun_workflow_run(self, run_id: int, failed_jobs_only: bool = True) -> dict:
        """
        Trigger a re-run of a specific GitHub Actions workflow run.

        When *failed_jobs_only* is ``True`` (default), only the failed jobs
        are re-executed; otherwise the entire run restarts from scratch.

        Requires ``actions:write`` permission on the configured token.

        Returns
        -------
        dict with keys: ``run_id``, ``triggered`` (bool), and optionally
        ``error`` (str) on failure.
        """
        return _rerun_workflow_run(
            repo=self.github_repo,
            run_id=run_id,
            token=self._github_token,
            failed_jobs_only=failed_jobs_only,
        )

    def post_merge_recovery(self, per_page: int = 30) -> dict:
        """
        Orchestrate full post-merge recovery.

        Steps
        -----
        1. Fetch recent workflow runs and identify incomplete ones.
        2. Trigger re-runs for every incomplete run via the GitHub API.
        3. Return a summary of all actions taken.

        Returns
        -------
        dict with keys: ``repo``, ``total_checked`` (int),
        ``incomplete_found`` (int), ``rerun_results`` (list of per-run
        outcome dicts), ``fetched_at`` (ISO-8601 str).
        """
        report = self.find_incomplete_runs(per_page=per_page)
        incomplete = report["incomplete_runs"]
        rerun_results = [
            self.rerun_workflow_run(r["id"])
            for r in incomplete
            if r.get("id") is not None
        ]
        return {
            "repo": self.github_repo,
            "total_checked": report["total_checked"],
            "incomplete_found": len(incomplete),
            "rerun_results": rerun_results,
            "fetched_at": report["fetched_at"],
        }

    # ------------------------------------------------------------------
    # Activate / deactivate bots (go-live)
    # ------------------------------------------------------------------

    def go_live(self, bot_id: str) -> dict:
        """Mark a bot as live (deployed and earning)."""
        if bot_id not in self._catalog:
            raise OrchestratorError(f"Bot '{bot_id}' is not registered.")
        self._catalog[bot_id].is_live = True
        return {"bot_id": bot_id, "is_live": True}

    def deactivate(self, bot_id: str) -> dict:
        """Mark a bot as not live."""
        if bot_id not in self._catalog:
            raise OrchestratorError(f"Bot '{bot_id}' is not registered.")
        self._catalog[bot_id].is_live = False
        return {"bot_id": bot_id, "is_live": False}

    # ------------------------------------------------------------------
    # Status snapshot
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a high-level orchestrator health snapshot."""
        swarm_enabled_bots = sum(
            1
            for spec in self._catalog.values()
            if (
                spec.coordination_mode != "centralized"
                or spec.marl_enabled
                or spec.stigmergic_channels
            )
        )
        return {
            "orchestrator": "BuddyOrchestrator",
            "github_repo": self.github_repo,
            "catalog_size": len(self._catalog),
            "scraping_active": self.scrape_lifecycle.scraping_active(),
            "scrape_deadline": self.scrape_lifecycle.deadline_iso(),
            "days_until_deadline": self.scrape_lifecycle.days_remaining(),
            "total_runs": len(self._run_history),
            "total_revenue_usd": round(sum(self._revenue.values()), 2),
            "swarm_enabled_bots": swarm_enabled_bots,
            "best_swarm_architecture": self.swarm_benchmark_report()["best_overall"],
        }
