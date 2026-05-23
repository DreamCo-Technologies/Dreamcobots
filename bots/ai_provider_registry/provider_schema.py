"""
AI Provider Registry — Provider Schema

Defines the normalized AIProviderObject: the standard machine-readable
representation of every AI provider inside DreamCo OS.  Every provider in the
catalog conforms to this schema so the Router Brain, Cost Optimizer, Capability
Graph, and Bot-Provider Mapper can operate on them uniformly.

GLOBAL AI SOURCES FLOW: This module adheres to the Dreamcobots GLOBAL AI
SOURCES FLOW framework pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Pricing tiers (normalized)
# ---------------------------------------------------------------------------

PRICING_FREE        = "free"
PRICING_FREEMIUM    = "freemium"
PRICING_PAID        = "paid"
PRICING_ENTERPRISE  = "enterprise"
PRICING_OPEN_SOURCE = "open_source"

VALID_PRICING = {PRICING_FREE, PRICING_FREEMIUM, PRICING_PAID, PRICING_ENTERPRISE, PRICING_OPEN_SOURCE}

# Cost-rank order (lower is cheaper) — used by Cost Optimizer
PRICING_COST_RANK: dict[str, int] = {
    PRICING_FREE:        0,
    PRICING_OPEN_SOURCE: 1,
    PRICING_FREEMIUM:    2,
    PRICING_PAID:        3,
    PRICING_ENTERPRISE:  4,
}


# ---------------------------------------------------------------------------
# Risk levels
# ---------------------------------------------------------------------------

RISK_LOW    = "low"
RISK_MEDIUM = "medium"
RISK_HIGH   = "high"

VALID_RISK_LEVELS = {RISK_LOW, RISK_MEDIUM, RISK_HIGH}


# ---------------------------------------------------------------------------
# Core AIProviderObject
# ---------------------------------------------------------------------------

@dataclass
class AIProviderObject:
    """
    Normalized machine-readable representation of an AI provider.

    This is the backbone of the DreamCo AI Ecosystem.  Every provider—whether
    it is an LLM, image generator, automation platform, or robotics company—
    is described by the same fields so they can be routed, compared, swapped,
    and composed uniformly.

    Field guide
    -----------
    id                  Unique snake_case identifier (e.g. "openai").
    name                Human-readable display name.
    pricing             One of VALID_PRICING constants.
    categories          List of taxonomy category IDs (see taxonomy.py).
    core_skill          One-sentence summary of what this provider does best.
    best_at             Comma-separated list of top task types.
    agent_role          How this provider is deployed as a DreamCo agent
                        (e.g. "Core LLM Agent", "Compute Acceleration Agent").
    bundle_fit          Which DreamCo bundle packs this provider belongs to.
    tier                Internal cost tier: free|low|medium|high|enterprise.
    api_access          Whether a programmatic API is publicly available.
    embedding_ready     Whether this provider produces embeddings / vectors.
    risk_level          Operational risk: low|medium|high.
    competition_cluster Which AI cluster this provider belongs to for
                        swap-in/swap-out purposes.
    layer               Top-level taxonomy layer (see taxonomy.py LAYERS).
    sub_layer           Sub-category within the layer.
    fallback_to         Ordered list of provider IDs to try if this one fails.
    open_source         Whether the core model/platform is open-source.
    api_endpoint        Canonical API URL hint (empty string if N/A).
    provider_company    Legal company name behind this provider.
    tags                Additional routing/search tags.
    notes               Free-form notes for human reviewers.
    """

    # ── Required identity fields ──────────────────────────────────────────
    id: str
    name: str
    pricing: str
    categories: list[str]
    core_skill: str
    best_at: str
    agent_role: str
    bundle_fit: list[str]
    tier: str
    api_access: bool
    embedding_ready: bool
    risk_level: str
    competition_cluster: str
    layer: str
    sub_layer: str

    # ── Optional / defaulted fields ───────────────────────────────────────
    fallback_to: list[str]    = field(default_factory=list)
    open_source: bool          = False
    api_endpoint: str          = ""
    provider_company: str      = ""
    tags: list[str]            = field(default_factory=list)
    notes: str                 = ""

    # ── Post-init validation ──────────────────────────────────────────────

    def __post_init__(self) -> None:
        if not self.id or not self.id.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"AIProviderObject.id must be alphanumeric/underscore: {self.id!r}")
        if self.pricing not in VALID_PRICING:
            raise ValueError(f"Invalid pricing '{self.pricing}' for provider '{self.id}'")
        if self.risk_level not in VALID_RISK_LEVELS:
            raise ValueError(f"Invalid risk_level '{self.risk_level}' for provider '{self.id}'")

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary of this provider."""
        return {
            "id":                  self.id,
            "name":                self.name,
            "pricing":             self.pricing,
            "categories":          self.categories,
            "core_skill":          self.core_skill,
            "best_at":             self.best_at,
            "agent_role":          self.agent_role,
            "bundle_fit":          self.bundle_fit,
            "tier":                self.tier,
            "api_access":          self.api_access,
            "embedding_ready":     self.embedding_ready,
            "risk_level":          self.risk_level,
            "competition_cluster": self.competition_cluster,
            "layer":               self.layer,
            "sub_layer":           self.sub_layer,
            "fallback_to":         self.fallback_to,
            "open_source":         self.open_source,
            "api_endpoint":        self.api_endpoint,
            "provider_company":    self.provider_company,
            "tags":                self.tags,
            "notes":               self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AIProviderObject":
        """Reconstruct an AIProviderObject from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            pricing=data["pricing"],
            categories=data.get("categories", []),
            core_skill=data.get("core_skill", ""),
            best_at=data.get("best_at", ""),
            agent_role=data.get("agent_role", ""),
            bundle_fit=data.get("bundle_fit", []),
            tier=data.get("tier", "medium"),
            api_access=data.get("api_access", True),
            embedding_ready=data.get("embedding_ready", False),
            risk_level=data.get("risk_level", RISK_LOW),
            competition_cluster=data.get("competition_cluster", ""),
            layer=data.get("layer", ""),
            sub_layer=data.get("sub_layer", ""),
            fallback_to=data.get("fallback_to", []),
            open_source=data.get("open_source", False),
            api_endpoint=data.get("api_endpoint", ""),
            provider_company=data.get("provider_company", ""),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
        )

    def cost_rank(self) -> int:
        """Lower integer = cheaper. Used by the Cost Optimizer Engine."""
        return PRICING_COST_RANK.get(self.pricing, 5)

    def __repr__(self) -> str:
        return f"AIProviderObject(id={self.id!r}, layer={self.layer!r}, tier={self.tier!r})"
