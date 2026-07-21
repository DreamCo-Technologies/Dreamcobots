"""
DreamCo Self-Evolution Engine — Makes every bot a self-evolving AI system.

Aligned with DreamCo's 3-Phase LLM Roadmap:

  Phase 1 — AI Operating System
    Multi-agent orchestration, workflow automation, app builders,
    AI business systems, autonomous coding assistants.

  Phase 2 — Fine-Tuned Models
    Use existing open-source models (Meta Llama, Mistral AI, DeepSeek, Qwen)
    and fine-tune them for DreamCo domains:
      • DreamCo Finance AI
      • DreamCo Real Estate AI
      • DreamCo Coding AI
      • DreamCo Trading AI

  Phase 3 — Proprietary DreamCo Models
    Train specialized models on curated DreamCo datasets.
    Build custom orchestration layers and optimize inference.
    Develop fully proprietary DreamCo AI agents.

Every bot that inherits from ``BaseBot`` automatically has a
``SelfEvolutionEngine`` instance at ``self.self_evolution``.  The engine:

* Records every run outcome (success / failure, revenue).
* Analyses performance and adapts its internal strategy each cycle.
* Promotes the bot to the next LLM phase when readiness thresholds
  are met (runs completed + sustained efficiency).
* Recommends the best LLM provider for the bot's category and phase.

Usage
-----
    from core.base_bot import BaseBot

    class MyBot(BaseBot):
        bot_id = "my_bot"
        name   = "My Bot"
        category = "finance"

        def run(self, task: dict) -> dict:
            # ... business logic ...
            return self._success(data={"result": "value"})

    bot = MyBot()
    result = bot.run({"action": "analyze"})

    # Trigger an evolution cycle manually
    record = bot.evolve()
    print(bot.evolution_status())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# LLM Provider registry — Phase 1, 2 and 3 providers
# ---------------------------------------------------------------------------

class LLMProvider(str, Enum):
    """
    All LLM providers available across DreamCo's 3-phase roadmap.

    Phase 1 — AI Operating System
        Use commercial or open-source providers as the AI back-end while
        building multi-agent orchestration and automation infrastructure.

    Phase 2 — Fine-Tuned Models
        Fine-tune open-source base models (Llama, Mistral, DeepSeek, Qwen)
        for DreamCo domain verticals.

    Phase 3 — Proprietary DreamCo Models
        Fully custom-trained DreamCo models with proprietary datasets.
    """

    # ── Phase 1: Commercial providers ──────────────────────────────────────
    OPENAI = "openai"            # OpenAI GPT-4 / GPT-4o
    ANTHROPIC = "anthropic"      # Anthropic Claude
    GOOGLE = "google"            # Google Gemini

    # ── Phase 2: Open-source / fine-tunable base models ────────────────────
    LLAMA = "llama"              # Meta Llama (default Phase 1/2 open model)
    MISTRAL = "mistral"          # Mistral AI
    DEEPSEEK = "deepseek"        # DeepSeek
    QWEN = "qwen"                # Alibaba Qwen

    # ── Phase 2: DreamCo domain-specific fine-tuned models ─────────────────
    DREAMCO_FINANCE = "dreamco_finance"            # Fine-tuned for finance & trading
    DREAMCO_REAL_ESTATE = "dreamco_real_estate"    # Fine-tuned for real estate
    DREAMCO_CODING = "dreamco_coding"              # Fine-tuned for code generation
    DREAMCO_TRADING = "dreamco_trading"            # Fine-tuned for algorithmic trading

    # ── Phase 3: Proprietary DreamCo model ─────────────────────────────────
    DREAMCO_PROPRIETARY = "dreamco_proprietary"    # Fully proprietary DreamCo LLM


# ---------------------------------------------------------------------------
# Evolution phases (mirrors the 3-phase LLM roadmap)
# ---------------------------------------------------------------------------

class EvolutionPhase(str, Enum):
    """Bot evolution phase aligned with DreamCo's LLM roadmap."""

    PHASE_1_AI_OS = "phase_1_ai_os"
    """Phase 1 — AI Operating System: orchestration, automation, app builders."""

    PHASE_2_FINE_TUNED = "phase_2_fine_tuned"
    """Phase 2 — Fine-Tuned Models: domain-specific open-source LLMs."""

    PHASE_3_PROPRIETARY = "phase_3_proprietary"
    """Phase 3 — Proprietary DreamCo Models: custom training & inference."""


# ---------------------------------------------------------------------------
# Thresholds for phase promotion
# ---------------------------------------------------------------------------

PHASE_2_MIN_RUNS: int = 50
PHASE_2_MIN_EFFICIENCY: float = 0.70

PHASE_3_MIN_RUNS: int = 200
PHASE_3_MIN_EFFICIENCY: float = 0.85


# ---------------------------------------------------------------------------
# Category → ideal Phase-2 fine-tuned LLM map
# ---------------------------------------------------------------------------

CATEGORY_LLM_MAP: Dict[str, LLMProvider] = {
    "finance": LLMProvider.DREAMCO_FINANCE,
    "real_estate": LLMProvider.DREAMCO_REAL_ESTATE,
    "trading": LLMProvider.DREAMCO_TRADING,
    "coding": LLMProvider.DREAMCO_CODING,
    "ai": LLMProvider.LLAMA,
    "sales": LLMProvider.MISTRAL,
    "marketing": LLMProvider.MISTRAL,
    "legal": LLMProvider.DEEPSEEK,
    "healthcare": LLMProvider.QWEN,
    "crypto": LLMProvider.DREAMCO_TRADING,
    "saas": LLMProvider.MISTRAL,
    "ecommerce": LLMProvider.MISTRAL,
    "education": LLMProvider.QWEN,
}


# ---------------------------------------------------------------------------
# EvolutionRecord — one record per completed evolution cycle
# ---------------------------------------------------------------------------

@dataclass
class EvolutionRecord:
    """Immutable snapshot of one evolution cycle."""

    cycle: int
    """Monotonically increasing cycle counter."""

    timestamp: str
    """ISO-8601 UTC timestamp of when the cycle ran."""

    phase: EvolutionPhase
    """Evolution phase active at the end of this cycle."""

    llm_provider: LLMProvider
    """LLM provider selected at the end of this cycle."""

    performance_before: Dict[str, float]
    """Performance snapshot captured before strategy mutation."""

    performance_after: Dict[str, float]
    """Performance snapshot captured after strategy mutation."""

    strategy_delta: Dict[str, float]
    """Change in strategy parameters produced by this cycle."""

    fitness_improvement: float
    """Δ efficiency between the before and after snapshots."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Optional extra context (e.g. phase transition flags)."""


# ---------------------------------------------------------------------------
# SelfEvolutionEngine
# ---------------------------------------------------------------------------

class SelfEvolutionEngine:
    """
    Autonomous self-evolution engine for a single DreamCo bot.

    Responsibilities
    ----------------
    1. **Performance tracking** — records every run's success/failure and
       revenue so that efficiency can be measured over time.
    2. **Strategy adaptation** — each ``evolve()`` call mutates the internal
       strategy parameters (learning rate, exploration rate, confidence
       threshold) based on recent performance.
    3. **Phase promotion** — automatically advances the bot from Phase 1
       through Phase 2 to Phase 3 when run count and efficiency thresholds
       are met, switching the recommended LLM provider accordingly.
    4. **LLM provider recommendation** — ``suggest_llm_provider()`` returns
       the most appropriate LLM given the bot's category and current phase.

    Parameters
    ----------
    bot_id : str
        Unique bot identifier (mirrors ``BaseBot.bot_id``).
    category : str
        Functional category used to select the Phase-2 fine-tuned model.
    llm_provider : LLMProvider | None
        Explicit initial provider override.  If ``None``, a default is
        derived from *category*.
    """

    def __init__(
        self,
        bot_id: str,
        category: str = "general",
        llm_provider: Optional[LLMProvider] = None,
    ) -> None:
        self.bot_id: str = bot_id
        self.category: str = category
        self.llm_provider: LLMProvider = (
            llm_provider if llm_provider is not None
            else self._default_provider(category)
        )
        self.phase: EvolutionPhase = EvolutionPhase.PHASE_1_AI_OS

        self._total_runs: int = 0
        self._successful_runs: int = 0
        self._total_revenue: float = 0.0
        self._evolution_cycle: int = 0
        self._evolution_history: List[EvolutionRecord] = []
        self._strategy: Dict[str, float] = self._initial_strategy()

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _default_provider(category: str) -> LLMProvider:
        """Return the default Phase-1 provider (Llama for most categories)."""
        return CATEGORY_LLM_MAP.get(category, LLMProvider.LLAMA)

    @staticmethod
    def _initial_strategy() -> Dict[str, float]:
        """Return the starting strategy parameters."""
        return {
            "learning_rate": 0.10,
            "exploration_rate": 0.50,
            "confidence_threshold": 0.70,
            "retry_budget": 3.0,
            "adaptive_timeout_s": 30.0,
        }

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def record_run(self, success: bool, revenue: float = 0.0) -> None:
        """
        Record the outcome of a single bot run.

        Parameters
        ----------
        success : bool
            Whether the run completed without error.
        revenue : float
            Revenue generated (USD) during the run.
        """
        self._total_runs += 1
        if success:
            self._successful_runs += 1
        self._total_revenue = round(self._total_revenue + revenue, 6)

    @property
    def efficiency(self) -> float:
        """Success rate as a fraction in ``[0, 1]``."""
        if self._total_runs == 0:
            return 1.0
        return self._successful_runs / self._total_runs

    def _performance_snapshot(self) -> Dict[str, float]:
        """Return current performance as a plain dict."""
        return {
            "efficiency": round(self.efficiency, 4),
            "total_runs": float(self._total_runs),
            "successful_runs": float(self._successful_runs),
            "success_rate_pct": round(self.efficiency * 100, 2),
            "total_revenue_usd": round(self._total_revenue, 2),
            "evolution_cycle": float(self._evolution_cycle),
        }

    # ------------------------------------------------------------------
    # Phase management
    # ------------------------------------------------------------------

    def _try_advance_phase(self) -> bool:
        """
        Promote the bot to the next evolution phase if thresholds are met.

        Returns ``True`` if a phase transition occurred.
        """
        if (
            self.phase == EvolutionPhase.PHASE_1_AI_OS
            and self._total_runs >= PHASE_2_MIN_RUNS
            and self.efficiency >= PHASE_2_MIN_EFFICIENCY
        ):
            self.phase = EvolutionPhase.PHASE_2_FINE_TUNED
            self.llm_provider = CATEGORY_LLM_MAP.get(
                self.category, LLMProvider.LLAMA
            )
            return True

        if (
            self.phase == EvolutionPhase.PHASE_2_FINE_TUNED
            and self._total_runs >= PHASE_3_MIN_RUNS
            and self.efficiency >= PHASE_3_MIN_EFFICIENCY
        ):
            self.phase = EvolutionPhase.PHASE_3_PROPRIETARY
            self.llm_provider = LLMProvider.DREAMCO_PROPRIETARY
            return True

        return False

    # ------------------------------------------------------------------
    # Core evolution
    # ------------------------------------------------------------------

    def evolve(self) -> EvolutionRecord:
        """
        Execute one evolution cycle.

        The cycle:
        1. Captures a *before* performance snapshot.
        2. Mutates strategy parameters based on efficiency trend.
        3. Checks for phase promotion.
        4. Captures an *after* snapshot and records the full cycle.

        Returns
        -------
        EvolutionRecord
            Immutable record of the cycle that just completed.
        """
        self._evolution_cycle += 1
        snapshot_before = self._performance_snapshot()

        # ── Strategy mutation ───────────────────────────────────────────
        new_strategy = dict(self._strategy)
        eff = self.efficiency

        if eff < 0.50:
            # Underperforming: increase exploration, lower confidence bar,
            # boost learning rate so the bot adapts faster.
            new_strategy["exploration_rate"] = min(
                0.90, self._strategy["exploration_rate"] + 0.10
            )
            new_strategy["confidence_threshold"] = max(
                0.50, self._strategy["confidence_threshold"] - 0.05
            )
            new_strategy["learning_rate"] = min(
                0.50, self._strategy["learning_rate"] + 0.05
            )
            new_strategy["retry_budget"] = min(
                10.0, self._strategy["retry_budget"] + 1.0
            )
        elif eff >= 0.85:
            # High performer: reduce exploration (exploit what works),
            # raise the confidence bar, reduce learning rate to stabilise.
            new_strategy["exploration_rate"] = max(
                0.10, self._strategy["exploration_rate"] - 0.05
            )
            new_strategy["confidence_threshold"] = min(
                0.95, self._strategy["confidence_threshold"] + 0.03
            )
            new_strategy["learning_rate"] = max(
                0.01, self._strategy["learning_rate"] - 0.01
            )
        # else: moderate performer → no strategy change this cycle

        strategy_delta: Dict[str, float] = {
            k: round(new_strategy[k] - self._strategy.get(k, 0.0), 6)
            for k in new_strategy
        }
        self._strategy = new_strategy

        # ── Phase promotion ─────────────────────────────────────────────
        phase_transition = self._try_advance_phase()

        snapshot_after = self._performance_snapshot()
        fitness_improvement = round(
            snapshot_after["efficiency"] - snapshot_before["efficiency"], 6
        )

        record = EvolutionRecord(
            cycle=self._evolution_cycle,
            timestamp=datetime.now(timezone.utc).isoformat(),
            phase=self.phase,
            llm_provider=self.llm_provider,
            performance_before=snapshot_before,
            performance_after=snapshot_after,
            strategy_delta=strategy_delta,
            fitness_improvement=fitness_improvement,
            metadata={"phase_transition": phase_transition},
        )
        self._evolution_history.append(record)
        return record

    # ------------------------------------------------------------------
    # LLM recommendation
    # ------------------------------------------------------------------

    def suggest_llm_provider(self) -> LLMProvider:
        """
        Return the most appropriate LLM provider for this bot right now.

        * Phase 3 → always ``DREAMCO_PROPRIETARY``
        * Phase 2 → category-specific fine-tuned model
        * Phase 1 → Llama (sensible open-source default)
        """
        if self.phase == EvolutionPhase.PHASE_3_PROPRIETARY:
            return LLMProvider.DREAMCO_PROPRIETARY
        if self.phase == EvolutionPhase.PHASE_2_FINE_TUNED:
            return CATEGORY_LLM_MAP.get(self.category, LLMProvider.LLAMA)
        return LLMProvider.LLAMA

    # ------------------------------------------------------------------
    # Status / history
    # ------------------------------------------------------------------

    def evolution_status(self) -> Dict[str, Any]:
        """
        Return a comprehensive, serialisable status dictionary.

        Includes: bot identity, current phase, active LLM provider,
        suggested LLM, all performance metrics, and current strategy.
        """
        return {
            "bot_id": self.bot_id,
            "category": self.category,
            "phase": self.phase.value,
            "llm_provider": self.llm_provider.value,
            "suggested_llm": self.suggest_llm_provider().value,
            "evolution_cycle": self._evolution_cycle,
            "performance": self._performance_snapshot(),
            "strategy": dict(self._strategy),
            "history_count": len(self._evolution_history),
        }

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Return all past evolution records as serialisable dicts."""
        return [
            {
                "cycle": r.cycle,
                "timestamp": r.timestamp,
                "phase": r.phase.value,
                "llm_provider": r.llm_provider.value,
                "performance_before": r.performance_before,
                "performance_after": r.performance_after,
                "strategy_delta": r.strategy_delta,
                "fitness_improvement": r.fitness_improvement,
                "metadata": r.metadata,
            }
            for r in self._evolution_history
        ]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SelfEvolutionEngine("
            f"bot_id={self.bot_id!r}, "
            f"phase={self.phase.value!r}, "
            f"llm={self.llm_provider.value!r}, "
            f"runs={self._total_runs}, "
            f"efficiency={self.efficiency:.2%})"
        )
