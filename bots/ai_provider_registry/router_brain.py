"""
router_brain.py — AI Router Brain: 4 core intelligence engines.

Engines:
  1. ProviderSelectorEngine  — choose best provider(s) for a task
  2. CostOptimizerEngine     — select cheapest viable path
  3. CapabilityGraphEngine   — map provider relationships and gaps
  4. FailureRedundancyEngine — automatic fallback chains
"""

from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

from dataclasses import dataclass, field
from typing import Optional

from bots.ai_provider_registry.provider_schema import AIProviderObject
from bots.ai_provider_registry.provider_catalog import PROVIDER_CATALOG, PROVIDER_CATALOG_BY_ID
from bots.ai_provider_registry.taxonomy import (
    CATEGORY_TAXONOMY,
    AI_CLUSTERS,
    PRICING_TIERS,
)

# ---------------------------------------------------------------------------
# Task → required capability mapping
# ---------------------------------------------------------------------------
TASK_CAPABILITY_MAP: dict[str, list[str]] = {
    # Sales & Marketing
    "marketing_funnel": ["sales_marketing", "content_ai", "automation", "analytics"],
    "copywriting": ["content_ai", "sales_marketing"],
    "social_media": ["marketing_ai", "content_ai"],
    "lead_generation": ["sales_ai", "data_labeling"],
    "email_campaign": ["sales_ai", "content_ai"],
    # Developer tasks
    "coding": ["dev_tools", "llm_core"],
    "code_review": ["dev_tools"],
    "app_deployment": ["dev_tools", "cloud"],
    "ml_experiment": ["mlops", "data_platforms"],
    "api_integration": ["dev_tools", "model_hosting"],
    # Data tasks
    "data_labeling": ["data_labeling"],
    "vector_search": ["vector_db"],
    "analytics_report": ["analytics", "bi"],
    "data_pipeline": ["data_platforms"],
    # Creative tasks
    "image_generation": ["image_gen"],
    "video_creation": ["video_gen"],
    "voice_synthesis": ["tts"],
    "music_composition": ["audio_gen"],
    "presentation": ["content_ai", "design_tools"],
    # Enterprise / operations
    "workflow_automation": ["rpa", "automation"],
    "knowledge_management": ["search", "productivity"],
    "hr_operations": ["hrtech"],
    "legal_review": ["legaltech"],
    "financial_analysis": ["fintech"],
    # Infrastructure
    "model_training": ["cloud", "hardware"],
    "model_serving": ["model_hosting", "cloud"],
    "edge_deployment": ["hardware"],
    # Security
    "threat_detection": ["security"],
    "code_security": ["security", "dev_tools"],
    # Healthcare
    "medical_imaging": ["healthtech"],
    "drug_discovery": ["drug_discovery"],
    # Research
    "research": ["research", "llm_core"],
}

# Pricing tier ordering (cheapest first)
_PRICING_ORDER = ["free", "open_source", "freemium", "paid", "enterprise"]

# Fallback cluster chains: if primary cluster fails, try secondary
_CLUSTER_FALLBACKS: dict[str, list[str]] = {
    "llm_core":     ["llm_core"],          # OpenAI → Anthropic → Mistral → Cohere
    "image_gen":    ["image_gen"],
    "video_gen":    ["video_gen"],
    "tts":          ["tts", "stt"],
    "vector_db":    ["vector_db", "search"],
    "dev_tools":    ["dev_tools"],
    "analytics":    ["analytics", "data_platforms"],
    "security":     ["security"],
    "healthtech":   ["healthtech"],
    "fintech":      ["fintech"],
    "legaltech":    ["legaltech"],
    "edtech":       ["edtech"],
    "hrtech":       ["hrtech"],
    "cloud":        ["cloud", "model_hosting"],
    "sales_ai":     ["sales_ai", "content_ai"],
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class RouterResult:
    task: str
    selected: list[AIProviderObject]
    reasoning: str
    cost_tier: str
    fallback_chain: list[AIProviderObject]


@dataclass
class CapabilityEdge:
    source_id: str
    target_id: str
    relationship: str   # "complements" | "competes" | "depends_on"
    strength: float     # 0.0–1.0


# ---------------------------------------------------------------------------
# 1. Provider Selector Engine
# ---------------------------------------------------------------------------
class ProviderSelectorEngine:
    """Choose the best provider(s) for a given task description."""

    def __init__(self, catalog: Optional[list[AIProviderObject]] = None) -> None:
        self._catalog = catalog or PROVIDER_CATALOG

    def select(
        self,
        task: str,
        *,
        max_results: int = 5,
        pricing_filter: Optional[list[str]] = None,
        tier_filter: Optional[list[str]] = None,
        require_api: bool = True,
        require_embedding: bool = False,
    ) -> list[AIProviderObject]:
        """Return ranked list of best providers for the task."""
        task_key = task.lower().replace(" ", "_")
        required_clusters = TASK_CAPABILITY_MAP.get(task_key, [])

        candidates: list[tuple[int, AIProviderObject]] = []
        for p in self._catalog:
            # Hard filters
            if require_api and not p.api_access:
                continue
            if require_embedding and not p.embedding_ready:
                continue
            if pricing_filter and p.pricing not in pricing_filter:
                continue
            if tier_filter and p.tier not in tier_filter:
                continue

            # Score: +3 per matching cluster, +1 if embedding_ready, +1 if api
            score = 0
            if p.competition_cluster in required_clusters:
                score += 3
            score += sum(1 for kw in required_clusters if kw in p.core_skill.lower())
            score += sum(1 for kw in required_clusters if kw in p.best_at.lower())
            if p.embedding_ready:
                score += 1
            if p.open_source:
                score += 1 if "free" in (pricing_filter or []) else 0
            candidates.append((score, p))

        candidates.sort(key=lambda x: (-x[0], x[1].name))
        return [p for _, p in candidates[:max_results]]

    def select_for_workflow(self, workflow_steps: list[str]) -> dict[str, list[AIProviderObject]]:
        """Map each workflow step to its best providers."""
        return {step: self.select(step, max_results=3) for step in workflow_steps}


# ---------------------------------------------------------------------------
# 2. Cost Optimizer Engine
# ---------------------------------------------------------------------------
class CostOptimizerEngine:
    """Select the cheapest viable path for a task."""

    def __init__(self, catalog: Optional[list[AIProviderObject]] = None) -> None:
        self._catalog = catalog or PROVIDER_CATALOG
        self._selector = ProviderSelectorEngine(catalog)

    def cheapest_path(
        self,
        task: str,
        priority: str = "balanced",
        max_results: int = 3,
    ) -> list[AIProviderObject]:
        """
        priority:
          "low_priority"  → free/open_source only
          "production"    → paid/enterprise, highest accuracy
          "balanced"      → freemium + paid
        """
        if priority == "low_priority":
            pricing = ["free", "open_source", "freemium"]
        elif priority == "production":
            pricing = ["paid", "enterprise"]
        else:
            pricing = ["freemium", "paid"]

        candidates = self._selector.select(task, max_results=20, pricing_filter=pricing)
        if not candidates:
            candidates = self._selector.select(task, max_results=max_results)

        # Sort by pricing tier index (cheapest first), then score
        def _key(p: AIProviderObject) -> tuple[int, str]:
            try:
                return (_PRICING_ORDER.index(p.pricing), p.name)
            except ValueError:
                return (99, p.name)

        candidates.sort(key=_key)
        return candidates[:max_results]

    def budget_recommendation(self, task: str) -> dict:
        """Return a three-tier cost recommendation for a task."""
        return {
            "free_path": self.cheapest_path(task, "low_priority", 2),
            "balanced_path": self.cheapest_path(task, "balanced", 2),
            "production_path": self.cheapest_path(task, "production", 2),
        }


# ---------------------------------------------------------------------------
# 3. Capability Graph Engine
# ---------------------------------------------------------------------------
class CapabilityGraphEngine:
    """Map what each AI can do in relation to others."""

    def __init__(self, catalog: Optional[list[AIProviderObject]] = None) -> None:
        self._catalog = catalog or PROVIDER_CATALOG
        self._by_id: dict[str, AIProviderObject] = {p.id: p for p in self._catalog}
        self._edges: list[CapabilityEdge] = []
        self._build_graph()

    def _build_graph(self) -> None:
        """Derive edges from shared clusters / categories."""
        cluster_groups: dict[str, list[AIProviderObject]] = {}
        for p in self._catalog:
            cluster_groups.setdefault(p.competition_cluster, []).append(p)

        for cluster, members in cluster_groups.items():
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    # Same cluster → they compete
                    self._edges.append(
                        CapabilityEdge(a.id, b.id, "competes", 0.8)
                    )
                    self._edges.append(
                        CapabilityEdge(b.id, a.id, "competes", 0.8)
                    )

        # Complementary relationships
        _complements = [
            ("pinecone_co", "openai", "depends_on", 0.9),   # RAG: vector + LLM
            ("weaviate_co", "openai", "depends_on", 0.9),
            ("langchain_ai", "openai", "depends_on", 0.95),
            ("langchain_ai", "anthropic", "depends_on", 0.9),
            ("elevenlabs_co", "openai", "complements", 0.7),
            ("runway_co", "openai", "complements", 0.6),
            ("canva_ai_co", "copy_ai_co", "complements", 0.8),
            ("clay_ai", "zoominfo_ai", "complements", 0.85),
            ("clay_ai", "apollo_io_ai", "competes", 0.9),
            ("databricks_co", "snowflake_ai_co", "competes", 0.9),
            ("uipath_co", "automation_anywhere", "competes", 0.95),
            ("snyk_ai", "github_copilot_co", "complements", 0.7),
        ]
        for src, tgt, rel, strength in _complements:
            if src in self._by_id and tgt in self._by_id:
                self._edges.append(CapabilityEdge(src, tgt, rel, strength))

    def neighbors(
        self,
        provider_id: str,
        relationship: Optional[str] = None,
    ) -> list[tuple[str, str, float]]:
        """Return (target_id, relationship, strength) tuples for a provider."""
        return [
            (e.target_id, e.relationship, e.strength)
            for e in self._edges
            if e.source_id == provider_id
            and (relationship is None or e.relationship == relationship)
        ]

    def cluster_map(self) -> dict[str, list[str]]:
        """Return {cluster → [provider_ids]} mapping."""
        result: dict[str, list[str]] = {}
        for p in self._catalog:
            result.setdefault(p.competition_cluster, []).append(p.id)
        return result

    def what_can(self, provider_id: str) -> Optional[str]:
        """Return the core skill summary for a provider."""
        p = self._by_id.get(provider_id)
        return p.core_skill if p else None

    def complementary_stack(self, provider_id: str) -> list[AIProviderObject]:
        """Return providers that complement (not compete with) this provider."""
        ids = {
            e.target_id
            for e in self._edges
            if e.source_id == provider_id and e.relationship == "complements"
        }
        return [self._by_id[i] for i in ids if i in self._by_id]

    def edge_count(self) -> int:
        return len(self._edges)


# ---------------------------------------------------------------------------
# 4. Failure Redundancy Engine
# ---------------------------------------------------------------------------
class FailureRedundancyEngine:
    """Build and execute automatic fallback chains."""

    def __init__(self, catalog: Optional[list[AIProviderObject]] = None) -> None:
        self._catalog = catalog or PROVIDER_CATALOG
        self._by_id: dict[str, AIProviderObject] = {p.id: p for p in self._catalog}
        self._selector = ProviderSelectorEngine(catalog)
        # Track simulated failures in-session
        self._failed: set[str] = set()

    def build_chain(self, task: str, chain_length: int = 5) -> list[AIProviderObject]:
        """
        Build a fallback chain for a task.
        Prioritizes: enterprise/paid → freemium → free/open-source.
        """
        enterprise = self._selector.select(task, max_results=chain_length,
                                           tier_filter=["enterprise"])
        paid = self._selector.select(task, max_results=chain_length,
                                     pricing_filter=["paid"])
        free_oss = self._selector.select(task, max_results=chain_length,
                                         pricing_filter=["free", "open_source",
                                                         "freemium"])

        seen: set[str] = set()
        chain: list[AIProviderObject] = []
        for p in enterprise + paid + free_oss:
            if p.id not in seen:
                seen.add(p.id)
                chain.append(p)
            if len(chain) >= chain_length:
                break
        return chain

    def mark_failed(self, provider_id: str) -> None:
        """Mark a provider as unavailable this session."""
        self._failed.add(provider_id)

    def reset_failures(self) -> None:
        self._failed.clear()

    def next_available(self, chain: list[AIProviderObject]) -> Optional[AIProviderObject]:
        """Return the first non-failed provider in the chain."""
        for p in chain:
            if p.id not in self._failed:
                return p
        return None

    def llm_fallback_chain(self) -> list[AIProviderObject]:
        """Standard LLM fallback: OpenAI → Claude → Mistral → Cohere → open-source."""
        preferred = ["openai", "anthropic", "mistral_ai", "cohere",
                     "google_ai_platform", "xai"]
        chain = [self._by_id[i] for i in preferred if i in self._by_id]
        # Append any open-source LLM not already in chain
        oss = [p for p in self._catalog
               if p.open_source and p.competition_cluster == "llm_core"
               and p.id not in {c.id for c in chain}]
        return chain + oss[:3]

    def failover(
        self,
        primary_id: str,
        task: str,
        chain_length: int = 5,
    ) -> list[AIProviderObject]:
        """Given a failed primary, return ordered fallback providers."""
        self.mark_failed(primary_id)
        chain = self.build_chain(task, chain_length)
        return [p for p in chain if p.id not in self._failed]


# ---------------------------------------------------------------------------
# Main Router Brain (orchestrates all 4 engines)
# ---------------------------------------------------------------------------
class RouterBrain:
    """
    Unified entry point for the AI Routing Brain.

    Usage:
        brain = RouterBrain()
        result = brain.route("Build a marketing funnel for my Shopify store")
    """

    def __init__(self, catalog: Optional[list[AIProviderObject]] = None) -> None:
        cat = catalog or PROVIDER_CATALOG
        self.selector = ProviderSelectorEngine(cat)
        self.cost = CostOptimizerEngine(cat)
        self.graph = CapabilityGraphEngine(cat)
        self.redundancy = FailureRedundancyEngine(cat)

    def route(
        self,
        user_request: str,
        *,
        priority: str = "balanced",
        max_agents: int = 5,
    ) -> RouterResult:
        """
        Route a natural-language request to the best agent stack.

        Returns a RouterResult with selected providers, reasoning, and fallbacks.
        """
        # Normalize request to task key
        task_key = self._classify(user_request)
        selected = self.cost.cheapest_path(task_key, priority, max_agents)

        # If we got nothing useful, fall back to full selector
        if not selected:
            selected = self.selector.select(task_key, max_results=max_agents)

        fallback_chain = self.redundancy.build_chain(task_key, chain_length=8)
        # Remove already-selected providers from fallback for clarity
        selected_ids = {p.id for p in selected}
        fallback_only = [p for p in fallback_chain if p.id not in selected_ids][:5]

        cost_tiers = list({p.pricing for p in selected})
        reasoning = (
            f"Task classified as '{task_key}'. "
            f"Selected {len(selected)} provider(s) matching capabilities. "
            f"Priority: {priority}. "
            f"Cost tiers in use: {', '.join(cost_tiers)}."
        )

        return RouterResult(
            task=task_key,
            selected=selected,
            reasoning=reasoning,
            cost_tier=priority,
            fallback_chain=fallback_only,
        )

    def _classify(self, request: str) -> str:
        """Map a free-text request to the closest task key."""
        r = request.lower()
        # Simple keyword matching — replace with embedding-based lookup in prod
        keyword_map = [
            (["marketing", "funnel", "shopify", "ecommerce"], "marketing_funnel"),
            (["copy", "copywriting", "ad copy"], "copywriting"),
            (["social", "instagram", "tweet", "linkedin"], "social_media"),
            (["lead", "leads", "outreach", "prospect"], "lead_generation"),
            (["email", "newsletter"], "email_campaign"),
            (["code", "coding", "programming", "function"], "coding"),
            (["legal", "contract", "law", "compliance"], "legal_review"),
            (["image", "picture", "art", "illustration"], "image_generation"),
            (["review", "pr", "pull request"], "code_review"),
            (["deploy", "deployment", "server"], "app_deployment"),
            (["experiment", "training", "train model"], "ml_experiment"),
            (["video", "clip", "reel"], "video_creation"),
            (["voice", "speech", "audio", "speak"], "voice_synthesis"),
            (["music", "song", "melody"], "music_composition"),
            (["slide", "presentation", "deck"], "presentation"),
            (["automate", "workflow", "rpa", "bot"], "workflow_automation"),
            (["knowledge", "wiki", "document"], "knowledge_management"),
            (["hr", "employee", "payroll", "hire"], "hr_operations"),
            (["finance", "money", "invest", "risk"], "financial_analysis"),
            (["label", "annotate", "dataset"], "data_labeling"),
            (["search", "vector", "retrieval", "rag"], "vector_search"),
            (["analytics", "dashboard", "report", "bi"], "analytics_report"),
            (["pipeline", "etl", "data engineering"], "data_pipeline"),
            (["threat", "security", "cyber", "attack"], "threat_detection"),
            (["medical", "clinical", "hospital", "radiology"], "medical_imaging"),
            (["drug", "molecule", "pharma"], "drug_discovery"),
            (["research", "paper", "study"], "research"),
        ]
        for keywords, task_key in keyword_map:
            if any(kw in r for kw in keywords):
                return task_key
        return "research"  # default

    def explain(self, provider_id: str) -> str:
        """Return a plain-English explanation of a provider's role."""
        p = PROVIDER_CATALOG_BY_ID.get(provider_id)
        if not p:
            return f"Provider '{provider_id}' not found in catalog."
        neighbors = self.graph.neighbors(provider_id)
        nb_summary = ", ".join(
            f"{n[0]} ({n[1]})" for n in neighbors[:5]
        )
        return (
            f"**{p.name}** — {p.agent_role}\n"
            f"  Core: {p.core_skill}\n"
            f"  Best at: {p.best_at}\n"
            f"  Pricing: {p.pricing} | Tier: {p.tier}\n"
            f"  Bundles: {', '.join(p.bundle_fit) or 'N/A'}\n"
            f"  Related providers: {nb_summary or 'none mapped'}"
        )


__all__ = [
    "ProviderSelectorEngine",
    "CostOptimizerEngine",
    "CapabilityGraphEngine",
    "FailureRedundancyEngine",
    "RouterBrain",
    "RouterResult",
    "TASK_CAPABILITY_MAP",
]
