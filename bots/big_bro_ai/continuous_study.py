"""
Big Bro AI — Continuous Study Engine

Adds modular knowledge crawlers (pattern searchers) that continuously scan
new areas of applied AI, industrial software, monetisation opportunities,
and competing systems so Big Bro is always the most informed in the room.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Knowledge domains
# ---------------------------------------------------------------------------

class KnowledgeDomain(Enum):
    AI_TOOLS = "ai_tools"
    AUTOMATION = "automation"
    MONETIZATION = "monetization"
    RELATIONSHIPS = "relationships"
    FINANCE = "finance"
    TECH_TRENDS = "tech_trends"
    BUSINESS_IDEAS = "business_ideas"
    HEALTH_WELLNESS = "health_wellness"
    STOICISM = "stoicism"
    COMMUNITY_BUILDING = "community_building"
    SALES = "sales"
    CODING = "coding"


# ---------------------------------------------------------------------------
# Pattern — a discovered knowledge item
# ---------------------------------------------------------------------------

@dataclass
class KnowledgePattern:
    """
    A discovered pattern or insight.

    Attributes
    ----------
    pattern_id : str
        Unique identifier.
    domain : KnowledgeDomain
        Which domain this pattern belongs to.
    title : str
        Short title of the insight.
    summary : str
        Concise explanation of the pattern.
    source : str
        Where this pattern was discovered.
    confidence : float
        0.0 – 1.0 confidence score.
    tags : list[str]
        Searchable tags.
    monetization_potential : bool
        Whether this pattern has revenue potential.
    discovered_at : str
        ISO timestamp of discovery.
    """

    pattern_id: str
    domain: KnowledgeDomain
    title: str
    summary: str
    source: str
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    monetization_potential: bool = False
    discovered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "domain": self.domain.value,
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "confidence": self.confidence,
            "tags": self.tags,
            "monetization_potential": self.monetization_potential,
            "discovered_at": self.discovered_at,
        }


# ---------------------------------------------------------------------------
# Study module (a pluggable crawler / scanner)
# ---------------------------------------------------------------------------

@dataclass
class StudyModule:
    """
    A pluggable pattern-searcher for a specific domain.

    Attributes
    ----------
    module_id : str
        Unique identifier.
    name : str
        Human-readable name.
    domain : KnowledgeDomain
        Domain this module specialises in.
    description : str
        What this module scans.
    active : bool
        Whether this module is currently running.
    scan_count : int
        Total scans performed.
    """

    module_id: str
    name: str
    domain: KnowledgeDomain
    description: str
    active: bool = True
    scan_count: int = 0

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "domain": self.domain.value,
            "description": self.description,
            "active": self.active,
            "scan_count": self.scan_count,
        }


# ---------------------------------------------------------------------------
# Built-in study modules
# ---------------------------------------------------------------------------

BUILTIN_MODULES: list[dict] = [
    {
        "module_id": "sm_ai_tools",
        "name": "AI Tools Scanner",
        "domain": KnowledgeDomain.AI_TOOLS,
        "description": (
            "Scans top-20 AI model capabilities, new tool releases, "
            "and competitive feature comparisons."
        ),
    },
    {
        "module_id": "sm_monetization",
        "name": "Monetization Pattern Finder",
        "domain": KnowledgeDomain.MONETIZATION,
        "description": (
            "Crawls business models, SaaS pricing strategies, "
            "and revenue opportunities across every industry."
        ),
    },
    {
        "module_id": "sm_business_ideas",
        "name": "Business Idea Evaluator",
        "domain": KnowledgeDomain.BUSINESS_IDEAS,
        "description": (
            "Evaluates home-based and online business ideas for legitimacy, "
            "ROI, and automation potential."
        ),
    },
    {
        "module_id": "sm_finance",
        "name": "Finance & Trading Engine",
        "domain": KnowledgeDomain.FINANCE,
        "description": (
            "Monitors compound interest strategies, day-trading patterns, "
            "broker services, and investment vehicles."
        ),
    },
    {
        "module_id": "sm_sales",
        "name": "Sales Master Scanner",
        "domain": KnowledgeDomain.SALES,
        "description": (
            "Tracks top sales techniques, relationship-based selling, "
            "and objection-handling frameworks."
        ),
    },
    {
        "module_id": "sm_tech_trends",
        "name": "Tech Trends Radar",
        "domain": KnowledgeDomain.TECH_TRENDS,
        "description": (
            "Identifies emerging tech stacks, frameworks, and platforms "
            "with high-growth potential."
        ),
    },
    {
        "module_id": "sm_stoicism",
        "name": "Stoic & Mindset Library",
        "domain": KnowledgeDomain.STOICISM,
        "description": (
            "Curates stoic philosophy, church wisdom, relationship advice, "
            "and mental discipline frameworks."
        ),
    },
    {
        "module_id": "sm_community",
        "name": "Community & Influence Scanner",
        "domain": KnowledgeDomain.COMMUNITY_BUILDING,
        "description": (
            "Studies top influencers, streamers, podcasters, and community "
            "builders to extract replicable personality traits."
        ),
    },
]


# ---------------------------------------------------------------------------
# Continuous Study Engine
# ---------------------------------------------------------------------------

class ContinuousStudyError(Exception):
    """Raised when a study operation fails."""


class ContinuousStudyEngine:
    """
    Manages modular knowledge crawlers that keep Big Bro's knowledge
    base current and comprehensive.

    Parameters
    ----------
    enabled : bool
        Whether the study engine is active.
    """

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._modules: dict[str, StudyModule] = {}
        self._patterns: dict[str, KnowledgePattern] = {}
        self._pattern_counter: int = 0
        self._load_builtin_modules()

    # ------------------------------------------------------------------
    # Module management
    # ------------------------------------------------------------------

    def _load_builtin_modules(self) -> None:
        for m in BUILTIN_MODULES:
            module = StudyModule(
                module_id=m["module_id"],
                name=m["name"],
                domain=m["domain"],
                description=m["description"],
            )
            self._modules[module.module_id] = module

    def add_module(
        self,
        name: str,
        domain: KnowledgeDomain,
        description: str,
    ) -> StudyModule:
        """Register a new custom study module."""
        module_id = f"sm_custom_{len(self._modules) + 1:04d}"
        module = StudyModule(
            module_id=module_id,
            name=name,
            domain=domain,
            description=description,
        )
        self._modules[module_id] = module
        return module

    def activate_module(self, module_id: str) -> StudyModule:
        """Activate a paused study module."""
        return self._toggle_module(module_id, True)

    def deactivate_module(self, module_id: str) -> StudyModule:
        """Pause a study module."""
        return self._toggle_module(module_id, False)

    def list_modules(self, active_only: bool = False) -> list[StudyModule]:
        """Return all study modules, optionally filtering to active only."""
        modules = list(self._modules.values())
        if active_only:
            modules = [m for m in modules if m.active]
        return sorted(modules, key=lambda m: m.module_id)

    # ------------------------------------------------------------------
    # Pattern management
    # ------------------------------------------------------------------

    def ingest_pattern(
        self,
        domain: KnowledgeDomain,
        title: str,
        summary: str,
        source: str,
        confidence: float = 1.0,
        tags: Optional[list[str]] = None,
        monetization_potential: bool = False,
    ) -> KnowledgePattern:
        """
        Ingest a newly discovered knowledge pattern.

        Parameters
        ----------
        domain : KnowledgeDomain
            Domain the pattern belongs to.
        title : str
            Short title.
        summary : str
            Concise explanation.
        source : str
            Discovery source.
        confidence : float
            0.0 – 1.0 confidence score.
        tags : list[str] | None
            Searchable tags.
        monetization_potential : bool
            Whether this pattern has revenue potential.
        """
        if not self.enabled:
            raise ContinuousStudyError("Continuous Study Engine is disabled.")
        self._pattern_counter += 1
        pattern_id = f"ptn_{self._pattern_counter:06d}"
        pattern = KnowledgePattern(
            pattern_id=pattern_id,
            domain=domain,
            title=title,
            summary=summary,
            source=source,
            confidence=confidence,
            tags=tags or [],
            monetization_potential=monetization_potential,
        )
        self._patterns[pattern_id] = pattern
        # Increment scan count for any active module in same domain
        for module in self._modules.values():
            if module.domain == domain and module.active:
                module.scan_count += 1
        return pattern

    def search_patterns(
        self,
        domain: Optional[KnowledgeDomain] = None,
        tag: Optional[str] = None,
        monetizable_only: bool = False,
    ) -> list[KnowledgePattern]:
        """
        Search ingested patterns by domain, tag, or monetization flag.
        """
        results = list(self._patterns.values())
        if domain is not None:
            results = [p for p in results if p.domain == domain]
        if tag is not None:
            results = [p for p in results if tag in p.tags]
        if monetizable_only:
            results = [p for p in results if p.monetization_potential]
        return sorted(results, key=lambda p: p.discovered_at, reverse=True)

    def pattern_count(self) -> int:
        """Return total ingested patterns."""
        return len(self._patterns)

    # ------------------------------------------------------------------
    # Study report
    # ------------------------------------------------------------------

    def study_report(self) -> dict:
        """Return a summary of the study engine's current state."""
        active_modules = [m for m in self._modules.values() if m.active]
        monetizable = [p for p in self._patterns.values() if p.monetization_potential]
        by_domain: dict[str, int] = {}
        for p in self._patterns.values():
            by_domain[p.domain.value] = by_domain.get(p.domain.value, 0) + 1
        return {
            "enabled": self.enabled,
            "total_modules": len(self._modules),
            "active_modules": len(active_modules),
            "total_patterns": len(self._patterns),
            "monetizable_patterns": len(monetizable),
            "patterns_by_domain": by_domain,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _toggle_module(self, module_id: str, active: bool) -> StudyModule:
        module = self._modules.get(module_id)
        if module is None:
            raise ContinuousStudyError(f"No module found with id '{module_id}'.")
        module.active = active
        return module
