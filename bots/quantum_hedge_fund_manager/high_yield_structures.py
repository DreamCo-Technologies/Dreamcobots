# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Quantum Hedge Fund Manager — High Yield Structures

Defines the catalogue of High Yield Premium Structures that the fund
manager can allocate capital into.  Each structure encapsulates:
  - Asset class and risk profile
  - Expected annual yield range
  - Minimum / maximum allocation percentages
  - Liquidity rating
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AssetClass(Enum):
    BONDS = "bonds"
    EQUITIES = "equities"
    REITS = "reits"
    COMMODITIES = "commodities"
    DERIVATIVES = "derivatives"
    CRYPTO = "crypto"
    PRIVATE_EQUITY = "private_equity"
    PREFERRED_STOCKS = "preferred_stocks"
    STRUCTURED_NOTES = "structured_notes"
    INFRASTRUCTURE = "infrastructure"


class LiquidityRating(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ILLIQUID = "illiquid"


class StructureStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"


@dataclass
class HighYieldStructure:
    """Represents a single High Yield Premium Structure."""

    structure_id: str
    name: str
    asset_class: AssetClass
    min_yield_pct: float          # Expected annual yield lower bound
    max_yield_pct: float          # Expected annual yield upper bound
    min_allocation_pct: float     # Minimum portfolio weight
    max_allocation_pct: float     # Maximum portfolio weight
    liquidity: LiquidityRating
    risk_score: float             # 0–10 scale (10 = highest risk)
    description: str = ""
    status: StructureStatus = StructureStatus.ACTIVE
    tags: list = field(default_factory=list)

    @property
    def mid_yield_pct(self) -> float:
        return (self.min_yield_pct + self.max_yield_pct) / 2.0

    def to_dict(self) -> dict:
        return {
            "structure_id": self.structure_id,
            "name": self.name,
            "asset_class": self.asset_class.value,
            "min_yield_pct": self.min_yield_pct,
            "max_yield_pct": self.max_yield_pct,
            "mid_yield_pct": round(self.mid_yield_pct, 2),
            "min_allocation_pct": self.min_allocation_pct,
            "max_allocation_pct": self.max_allocation_pct,
            "liquidity": self.liquidity.value,
            "risk_score": self.risk_score,
            "description": self.description,
            "status": self.status.value,
            "tags": self.tags,
        }


def _make_id() -> str:
    return str(uuid.uuid4())[:8]


# ---------------------------------------------------------------------------
# Built-in High Yield Premium Structure catalogue
# ---------------------------------------------------------------------------

DEFAULT_STRUCTURES: list[HighYieldStructure] = [
    HighYieldStructure(
        structure_id=_make_id(),
        name="AI-Enhanced High Yield Bond Fund",
        asset_class=AssetClass.BONDS,
        min_yield_pct=6.5,
        max_yield_pct=10.0,
        min_allocation_pct=5.0,
        max_allocation_pct=30.0,
        liquidity=LiquidityRating.MEDIUM,
        risk_score=4.5,
        description="Corporate high-yield bonds selected via AI credit analysis.",
        tags=["fixed_income", "ai_selected"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Quantum REIT Income Portfolio",
        asset_class=AssetClass.REITS,
        min_yield_pct=5.0,
        max_yield_pct=9.0,
        min_allocation_pct=5.0,
        max_allocation_pct=25.0,
        liquidity=LiquidityRating.HIGH,
        risk_score=3.5,
        description="Diversified real estate investment trusts with premium dividend yields.",
        tags=["real_estate", "dividend"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Preferred Stock Premium Series",
        asset_class=AssetClass.PREFERRED_STOCKS,
        min_yield_pct=5.5,
        max_yield_pct=8.5,
        min_allocation_pct=2.0,
        max_allocation_pct=20.0,
        liquidity=LiquidityRating.HIGH,
        risk_score=3.0,
        description="Investment-grade preferred shares with fixed dividend payments.",
        tags=["preferred", "dividend", "fixed_income"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Emerging Market High Yield Debt",
        asset_class=AssetClass.BONDS,
        min_yield_pct=8.0,
        max_yield_pct=14.0,
        min_allocation_pct=2.0,
        max_allocation_pct=15.0,
        liquidity=LiquidityRating.MEDIUM,
        risk_score=6.5,
        description="Sovereign and corporate debt from high-growth emerging markets.",
        tags=["emerging_markets", "high_yield"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Infrastructure Revenue Bonds",
        asset_class=AssetClass.INFRASTRUCTURE,
        min_yield_pct=4.5,
        max_yield_pct=7.5,
        min_allocation_pct=5.0,
        max_allocation_pct=20.0,
        liquidity=LiquidityRating.LOW,
        risk_score=2.5,
        description="Long-duration bonds backed by toll roads, utilities, and airports.",
        tags=["infrastructure", "long_duration"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Structured Credit Note — AI Series",
        asset_class=AssetClass.STRUCTURED_NOTES,
        min_yield_pct=7.0,
        max_yield_pct=12.0,
        min_allocation_pct=2.0,
        max_allocation_pct=10.0,
        liquidity=LiquidityRating.LOW,
        risk_score=5.5,
        description="Custom structured notes with AI-optimised underlying basket.",
        tags=["structured", "ai_optimised"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Private Equity Growth Fund",
        asset_class=AssetClass.PRIVATE_EQUITY,
        min_yield_pct=12.0,
        max_yield_pct=25.0,
        min_allocation_pct=1.0,
        max_allocation_pct=10.0,
        liquidity=LiquidityRating.ILLIQUID,
        risk_score=7.5,
        description="Early-stage and growth-equity positions in AI and tech companies.",
        tags=["private_equity", "growth", "illiquid"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Commodity-Linked Premium Note",
        asset_class=AssetClass.COMMODITIES,
        min_yield_pct=6.0,
        max_yield_pct=11.0,
        min_allocation_pct=2.0,
        max_allocation_pct=15.0,
        liquidity=LiquidityRating.MEDIUM,
        risk_score=5.0,
        description="Capital-protected notes linked to a diversified commodity index.",
        tags=["commodities", "capital_protection"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Quantitative Derivatives Overlay",
        asset_class=AssetClass.DERIVATIVES,
        min_yield_pct=8.0,
        max_yield_pct=18.0,
        min_allocation_pct=1.0,
        max_allocation_pct=8.0,
        liquidity=LiquidityRating.HIGH,
        risk_score=8.0,
        description="Options and futures strategies managed by quantitative algorithms.",
        tags=["derivatives", "quant", "high_risk"],
    ),
    HighYieldStructure(
        structure_id=_make_id(),
        name="Digital Asset Yield Fund",
        asset_class=AssetClass.CRYPTO,
        min_yield_pct=5.0,
        max_yield_pct=20.0,
        min_allocation_pct=1.0,
        max_allocation_pct=10.0,
        liquidity=LiquidityRating.HIGH,
        risk_score=8.5,
        description="Staking, lending, and DeFi yield strategies on blue-chip digital assets.",
        tags=["crypto", "defi", "yield"],
    ),
]


class HighYieldStructureDatabase:
    """In-memory catalogue of High Yield Premium Structures."""

    def __init__(self, load_defaults: bool = True) -> None:
        self._structures: dict[str, HighYieldStructure] = {}
        if load_defaults:
            for s in DEFAULT_STRUCTURES:
                self._structures[s.structure_id] = s

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_structure(self, structure: HighYieldStructure) -> HighYieldStructure:
        if structure.structure_id in self._structures:
            raise ValueError(f"Structure '{structure.structure_id}' already exists.")
        self._structures[structure.structure_id] = structure
        return structure

    def get_structure(self, structure_id: str) -> HighYieldStructure:
        if structure_id not in self._structures:
            raise KeyError(f"Structure '{structure_id}' not found.")
        return self._structures[structure_id]

    def list_structures(
        self,
        asset_class: Optional[AssetClass] = None,
        min_yield: Optional[float] = None,
        max_risk: Optional[float] = None,
        status: Optional[StructureStatus] = None,
    ) -> list[HighYieldStructure]:
        results = list(self._structures.values())
        if asset_class is not None:
            results = [s for s in results if s.asset_class == asset_class]
        if min_yield is not None:
            results = [s for s in results if s.mid_yield_pct >= min_yield]
        if max_risk is not None:
            results = [s for s in results if s.risk_score <= max_risk]
        if status is not None:
            results = [s for s in results if s.status == status]
        return sorted(results, key=lambda s: s.mid_yield_pct, reverse=True)

    def count(self) -> int:
        return len(self._structures)

    def top_by_yield(self, n: int = 5) -> list[HighYieldStructure]:
        return self.list_structures()[:n]

    def top_by_risk_adjusted_yield(self, n: int = 5) -> list[HighYieldStructure]:
        """Rank by yield/risk ratio (higher is better)."""
        structures = [s for s in self._structures.values() if s.risk_score > 0]
        ranked = sorted(
            structures,
            key=lambda s: s.mid_yield_pct / s.risk_score,
            reverse=True,
        )
        return ranked[:n]
