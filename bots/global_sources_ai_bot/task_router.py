"""
GlobalSourcesAIBot — Task Router

Selects the best AI model(s) for any given task using a multi-signal scoring
algorithm that weighs:
  - Tag overlap (primary signal)
  - Benchmark scores (accuracy, speed, cost, creativity)
  - Cost tier preference
  - Open-source preference
  - Context-window requirements

GLOBAL AI SOURCES FLOW: This module adheres to the Dreamcobots GLOBAL AI
SOURCES FLOW framework pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from bots.global_sources_ai_bot.model_registry import (
    AIModel,
    UseCase,
    TOP_100_AI_MODELS,
    TOP_100_USE_CASES,
)


# ---------------------------------------------------------------------------
# Routing result
# ---------------------------------------------------------------------------

@dataclass
class RoutingResult:
    """Outcome of a routing decision."""
    task_description: str
    matched_use_cases: list[UseCase]
    ranked_models: list[tuple[str, float]]   # (model_id, score)
    primary_model: Optional[AIModel]
    reasoning: str
    tags_used: list[str]


# ---------------------------------------------------------------------------
# Routing config
# ---------------------------------------------------------------------------

@dataclass
class RoutingConfig:
    """Tunable weights used when scoring models."""
    tag_weight: float = 3.0
    benchmark_accuracy_weight: float = 2.0
    benchmark_speed_weight: float = 1.0
    benchmark_cost_weight: float = 1.0
    open_source_bonus: float = 0.5
    # Cost-tier preferences: higher value → preferred
    cost_tier_preference: dict = field(default_factory=lambda: {
        "free": 1.2,
        "low": 1.1,
        "medium": 1.0,
        "high": 0.85,
        "enterprise": 0.7,
    })
    prefer_open_source: bool = False
    top_k: int = 5


# ---------------------------------------------------------------------------
# Task Router
# ---------------------------------------------------------------------------

class TaskRouter:
    """
    Routes a free-text task description to the best AI model(s).

    The router:
      1. Tokenises the task description into lowercase keywords.
      2. Matches those keywords against use-case tags to find the most
         relevant use-cases.
      3. Collects candidate models from those use-cases plus any model
         whose strengths overlap with the extracted keywords.
      4. Scores every candidate with a weighted formula.
      5. Returns a RoutingResult with a ranked list and a primary selection.
    """

    # Explicit routing table: keyword → list[model_id]
    # These hard-coded overrides take precedence for well-known task types.
    EXPLICIT_ROUTES: dict[str, list[str]] = {
        "code":        ["claude_code", "github_copilot", "cursor", "chatgpt", "gemini_code"],
        "coding":      ["claude_code", "github_copilot", "cursor", "chatgpt", "gemini_code"],
        "debug":       ["claude_code", "cursor", "github_copilot", "chatgpt"],
        "image":       ["midjourney", "dalle3", "flux", "stable_diffusion", "firefly"],
        "photo":       ["midjourney", "dalle3", "firefly", "stable_diffusion"],
        "logo":        ["midjourney", "canva_ai", "looka", "firefly", "dalle3"],
        "video":       ["sora", "runway", "pika", "veo", "dream_machine"],
        "music":       ["suno", "udio", "aiva", "soundraw", "boomy"],
        "voice":       ["elevenlabs", "playht", "hume", "openai_voice", "resemble"],
        "audio":       ["elevenlabs", "playht", "descript", "suno"],
        "speech":      ["whisper", "otter_ai", "fireflies_ai"],
        "transcribe":  ["whisper", "otter_ai", "fireflies_ai", "descript"],
        "translate":   ["deepl", "chatgpt", "gemini", "claude"],
        "research":    ["perplexity", "chatgpt_deep_research", "elicit", "consensus", "gemini"],
        "search":      ["perplexity", "you_ai", "chatgpt", "gemini_search"],
        "legal":       ["harvey_ai", "claude", "chatgpt"],
        "medical":     ["med_palm", "ms_dragon", "chatgpt"],
        "finance":     ["bloomberg_gpt", "chatgpt", "claude"],
        "trading":     ["bloomberg_gpt", "chatgpt", "grok"],
        "crypto":      ["chain_gpt", "grok", "chatgpt"],
        "automate":    ["zapier_ai", "make_ai", "n8n_ai", "uipath"],
        "workflow":    ["zapier_ai", "make_ai", "n8n_ai", "langgraph"],
        "seo":         ["surfer_ai", "jasper", "chatgpt"],
        "marketing":   ["jasper", "copy_ai", "hubspot_breeze", "chatgpt"],
        "design":      ["midjourney", "canva_ai", "figma_ai", "firefly"],
        "uiux":        ["figma_ai", "v0", "framer_ai"],
        "website":     ["v0", "framer_ai", "chatgpt"],
        "app":         ["dreamco_ai", "cursor", "v0", "bolt_new"],
        "agent":       ["crewai", "autogen", "langgraph", "openai_operator"],
        "robot":       ["nvidia_isaac", "figure_ai", "tesla_optimus"],
        "security":    ["crowdstrike_ai", "darktrace", "ms_copilot"],
        "fraud":       ["stripe_radar", "crowdstrike_ai", "darktrace"],
        "analysis":    ["chatgpt", "claude", "gemini", "perplexity"],
        "data":        ["tableau_ai", "power_bi_copilot", "chatgpt", "claude"],
        "predict":     ["datarobot", "h2o_ai", "aws_sagemaker"],
        "write":       ["chatgpt", "claude", "jasper", "copy_ai"],
        "blog":        ["chatgpt", "claude", "jasper", "writesonic"],
        "email":       ["chatgpt", "claude", "ms_copilot"],
        "meeting":     ["otter_ai", "fireflies_ai", "ms_copilot", "notion_ai"],
        "presentation":["gamma", "canva_ai", "ms_copilot"],
        "education":   ["khanmigo", "chatgpt", "gemini", "claude"],
        "tutor":       ["khanmigo", "chatgpt", "claude"],
        "companion":   ["character_ai", "replika", "pi_ai"],
        "wellness":    ["woebot", "replika", "chatgpt"],
        "science":     ["alphafold", "wolfram_ai", "chatgpt", "elicit"],
        "math":        ["wolfram_ai", "chatgpt", "gemini"],
        "simulation":  ["nvidia_omniverse", "alphafold", "wolfram_ai"],
    }

    def __init__(
        self,
        config: Optional[RoutingConfig] = None,
        benchmark_scores: Optional[dict[str, dict[str, float]]] = None,
    ):
        self._config = config or RoutingConfig()
        # benchmark_scores: model_id → {accuracy, speed, cost_score, creativity}
        self._benchmark_scores: dict[str, dict[str, float]] = benchmark_scores or {}
        self._use_cases = TOP_100_USE_CASES
        self._models = TOP_100_AI_MODELS

    # ── Public API ────────────────────────────────────────────────────────

    def route(self, task: str, top_k: Optional[int] = None) -> RoutingResult:
        """
        Route *task* to the best AI model(s).

        Parameters
        ----------
        task : str
            Free-text description of the task.
        top_k : int, optional
            Override the config top_k for this call.

        Returns
        -------
        RoutingResult
        """
        k = top_k or self._config.top_k
        keywords = self._tokenise(task)

        # 1. Check explicit routes first
        explicit_models = self._explicit_route(keywords)

        # 2. Match use-cases
        matched_use_cases = self._match_use_cases(keywords)
        uc_model_ids: list[str] = []
        for uc in matched_use_cases:
            uc_model_ids.extend(uc.top_models)

        # 3. Build candidate set
        candidates: set[str] = set(explicit_models) | set(uc_model_ids)
        # Also add models whose strength tags overlap directly
        for mid, model in self._models.items():
            if any(kw in model.strengths for kw in keywords):
                candidates.add(mid)

        if not candidates:
            candidates = set(self._models.keys())

        # 4. Score candidates
        scored: list[tuple[str, float]] = [
            (mid, self._score(mid, keywords))
            for mid in candidates
            if mid in self._models
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_scored = scored[:k]

        primary_model = self._models.get(top_scored[0][0]) if top_scored else None

        reasoning = self._build_reasoning(keywords, matched_use_cases, primary_model, explicit_models)

        return RoutingResult(
            task_description=task,
            matched_use_cases=matched_use_cases[:3],
            ranked_models=top_scored,
            primary_model=primary_model,
            reasoning=reasoning,
            tags_used=list(keywords),
        )

    def route_batch(self, tasks: list[str], top_k: int = 5) -> list[RoutingResult]:
        """Route multiple tasks, returning one RoutingResult per task."""
        return [self.route(t, top_k=top_k) for t in tasks]

    def update_benchmark_scores(self, model_id: str, scores: dict[str, float]) -> None:
        """Inject live benchmark scores so subsequent routing uses them."""
        self._benchmark_scores[model_id] = scores

    def available_use_cases(self) -> list[UseCase]:
        return list(self._use_cases)

    def available_models(self) -> list[AIModel]:
        return list(self._models.values())

    # ── Internal helpers ──────────────────────────────────────────────────

    # Common English stop words that pollute substring-based tag matching
    _STOP_WORDS: frozenset[str] = frozenset({
        "a", "an", "the", "to", "of", "in", "for", "and", "or",
        "is", "it", "be", "my", "do", "i", "me", "we", "us", "on",
        "at", "by", "up", "so", "no", "if", "as", "he", "she",
    })

    @classmethod
    def _tokenise(cls, text: str) -> set[str]:
        """Lowercase, split, strip punctuation, and remove stop words."""
        import re
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        return {t for t in tokens if len(t) > 2 and t not in cls._STOP_WORDS}

    def _explicit_route(self, keywords: set[str]) -> list[str]:
        """Check explicit routing table for any matching keyword."""
        results: list[str] = []
        for kw, models in self.EXPLICIT_ROUTES.items():
            if kw in keywords:
                results.extend(models)
        return results

    def _match_use_cases(self, keywords: set[str]) -> list[UseCase]:
        """Return use-cases whose tags overlap with the extracted keywords."""
        scored_uc: list[tuple[UseCase, int]] = []
        for uc in self._use_cases:
            overlap = sum(1 for tag in uc.tags if tag in keywords or
                          any(kw in tag or tag in kw for kw in keywords))
            if overlap > 0:
                scored_uc.append((uc, overlap))
        scored_uc.sort(key=lambda x: x[1], reverse=True)
        return [uc for uc, _ in scored_uc]

    def _score(self, model_id: str, keywords: set[str]) -> float:
        """Compute a composite score for *model_id* given *keywords*."""
        model = self._models.get(model_id)
        if model is None:
            return 0.0

        cfg = self._config
        score = 0.0

        # Tag overlap
        tag_overlap = sum(1 for s in model.strengths if s in keywords or
                          any(kw in s or s in kw for kw in keywords))
        score += tag_overlap * cfg.tag_weight

        # Benchmark scores
        bm = self._benchmark_scores.get(model_id, {})
        score += bm.get("accuracy", 0.5) * cfg.benchmark_accuracy_weight
        score += bm.get("speed", 0.5) * cfg.benchmark_speed_weight
        score += bm.get("cost_score", 0.5) * cfg.benchmark_cost_weight

        # Cost tier preference
        cost_factor = cfg.cost_tier_preference.get(model.cost_tier, 1.0)
        score *= cost_factor

        # Open-source bonus
        if cfg.prefer_open_source and model.is_open_source:
            score += cfg.open_source_bonus

        return score

    @staticmethod
    def _build_reasoning(
        keywords: set[str],
        matched_use_cases: list[UseCase],
        primary_model: Optional[AIModel],
        explicit_models: list[str],
    ) -> str:
        parts = [f"Task keywords: {sorted(keywords)}"]
        if matched_use_cases:
            uc_names = [uc.name for uc in matched_use_cases[:3]]
            parts.append(f"Matched use-cases: {uc_names}")
        if explicit_models:
            parts.append(f"Explicit routing hit for: {explicit_models[:3]}")
        if primary_model:
            parts.append(
                f"Primary selection: {primary_model.display_name} "
                f"({primary_model.provider}) — strengths: {primary_model.strengths}"
            )
        return " | ".join(parts)
