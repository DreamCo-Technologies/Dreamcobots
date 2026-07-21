# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Quantum Hedge Fund Manager — Fund Allocator

Manages dynamic capital allocation across High Yield Premium Structures.
Supports rule-based and AI-assisted rebalancing strategies.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from bots.quantum_hedge_fund_manager.high_yield_structures import (
    HighYieldStructure,
    HighYieldStructureDatabase,
)


class AllocationStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REBALANCING = "rebalancing"
    CLOSED = "closed"


class ReallocationStrategy(Enum):
    EQUAL_WEIGHT = "equal_weight"
    YIELD_WEIGHTED = "yield_weighted"
    RISK_PARITY = "risk_parity"
    MOMENTUM = "momentum"
    MIN_VARIANCE = "min_variance"
    QUANTUM_OPTIMISED = "quantum_optimised"


@dataclass
class AllocationSlice:
    """A single fund allocation slice within a portfolio."""

    structure_id: str
    structure_name: str
    weight_pct: float           # Target portfolio weight (0–100)
    allocated_amount_usd: float
    expected_yield_pct: float

    def to_dict(self) -> dict:
        return {
            "structure_id": self.structure_id,
            "structure_name": self.structure_name,
            "weight_pct": round(self.weight_pct, 4),
            "allocated_amount_usd": round(self.allocated_amount_usd, 2),
            "expected_yield_pct": round(self.expected_yield_pct, 2),
        }


@dataclass
class FundAllocation:
    """A complete fund allocation across multiple High Yield Structures."""

    allocation_id: str
    name: str
    total_aum_usd: float         # Assets under management
    strategy: ReallocationStrategy
    slices: list[AllocationSlice] = field(default_factory=list)
    status: AllocationStatus = AllocationStatus.DRAFT
    notes: str = ""
    reallocation_count: int = 0

    @property
    def total_weight_pct(self) -> float:
        return sum(s.weight_pct for s in self.slices)

    @property
    def blended_yield_pct(self) -> float:
        if not self.slices:
            return 0.0
        return sum(
            s.weight_pct / 100.0 * s.expected_yield_pct for s in self.slices
        )

    @property
    def annual_income_usd(self) -> float:
        return self.total_aum_usd * self.blended_yield_pct / 100.0

    def to_dict(self) -> dict:
        return {
            "allocation_id": self.allocation_id,
            "name": self.name,
            "total_aum_usd": self.total_aum_usd,
            "strategy": self.strategy.value,
            "status": self.status.value,
            "total_weight_pct": round(self.total_weight_pct, 4),
            "blended_yield_pct": round(self.blended_yield_pct, 4),
            "annual_income_usd": round(self.annual_income_usd, 2),
            "reallocation_count": self.reallocation_count,
            "slices": [s.to_dict() for s in self.slices],
            "notes": self.notes,
        }


class FundAllocatorError(Exception):
    """Raised when a fund allocation operation fails."""


class FundAllocator:
    """
    Dynamically allocates and reallocates capital across High Yield
    Premium Structures.

    Parameters
    ----------
    structure_db : HighYieldStructureDatabase
        The structure catalogue to allocate against.
    max_portfolios : int | None
        Maximum number of concurrent allocations (None = unlimited).
    """

    def __init__(
        self,
        structure_db: HighYieldStructureDatabase,
        max_portfolios: Optional[int] = None,
    ) -> None:
        self._db = structure_db
        self._max = max_portfolios
        self._allocations: dict[str, FundAllocation] = {}

    # ------------------------------------------------------------------
    # Allocation lifecycle
    # ------------------------------------------------------------------

    def create_allocation(
        self,
        name: str,
        total_aum_usd: float,
        strategy: ReallocationStrategy = ReallocationStrategy.YIELD_WEIGHTED,
        structure_ids: Optional[list[str]] = None,
        custom_weights: Optional[dict[str, float]] = None,
        notes: str = "",
    ) -> FundAllocation:
        """
        Create a new fund allocation.

        Parameters
        ----------
        name : str
            Human-readable allocation name.
        total_aum_usd : float
            Total capital to allocate in USD.
        strategy : ReallocationStrategy
            Strategy used to derive initial weights.
        structure_ids : list[str] | None
            Explicit list of structure IDs to include.  When *None* the
            top-10 structures by risk-adjusted yield are used.
        custom_weights : dict[str, float] | None
            Override weights per structure ID (must sum to ≤ 100).
        notes : str
            Free-text notes for the allocation.
        """
        if self._max is not None and len(self._allocations) >= self._max:
            raise FundAllocatorError(
                f"Maximum portfolio limit ({self._max}) reached. "
                "Upgrade your tier to create more allocations."
            )

        if total_aum_usd <= 0:
            raise FundAllocatorError("total_aum_usd must be positive.")

        # Resolve structure list
        if structure_ids:
            structures = [self._db.get_structure(sid) for sid in structure_ids]
        else:
            structures = self._db.top_by_risk_adjusted_yield(n=10)

        if not structures:
            raise FundAllocatorError("No structures available for allocation.")

        # Compute weights
        weights = self._compute_weights(
            structures, strategy, custom_weights or {}
        )

        slices = [
            AllocationSlice(
                structure_id=s.structure_id,
                structure_name=s.name,
                weight_pct=weights[s.structure_id],
                allocated_amount_usd=total_aum_usd * weights[s.structure_id] / 100.0,
                expected_yield_pct=s.mid_yield_pct,
            )
            for s in structures
        ]

        alloc = FundAllocation(
            allocation_id=str(uuid.uuid4())[:8],
            name=name,
            total_aum_usd=total_aum_usd,
            strategy=strategy,
            slices=slices,
            status=AllocationStatus.ACTIVE,
            notes=notes,
        )
        self._allocations[alloc.allocation_id] = alloc
        return alloc

    def reallocate(
        self,
        allocation_id: str,
        new_strategy: Optional[ReallocationStrategy] = None,
        new_structure_ids: Optional[list[str]] = None,
        custom_weights: Optional[dict[str, float]] = None,
        new_aum_usd: Optional[float] = None,
    ) -> FundAllocation:
        """
        Dynamically reallocate an existing fund allocation.

        Updates weights, structures, and/or AUM and increments the
        reallocation counter.
        """
        alloc = self.get_allocation(allocation_id)
        alloc.status = AllocationStatus.REBALANCING

        if new_aum_usd is not None:
            if new_aum_usd <= 0:
                raise FundAllocatorError("new_aum_usd must be positive.")
            alloc.total_aum_usd = new_aum_usd

        strategy = new_strategy or alloc.strategy
        alloc.strategy = strategy

        if new_structure_ids:
            structures = [self._db.get_structure(sid) for sid in new_structure_ids]
        else:
            structures = [
                self._db.get_structure(sl.structure_id) for sl in alloc.slices
            ]

        weights = self._compute_weights(
            structures, strategy, custom_weights or {}
        )

        alloc.slices = [
            AllocationSlice(
                structure_id=s.structure_id,
                structure_name=s.name,
                weight_pct=weights[s.structure_id],
                allocated_amount_usd=alloc.total_aum_usd * weights[s.structure_id] / 100.0,
                expected_yield_pct=s.mid_yield_pct,
            )
            for s in structures
        ]
        alloc.status = AllocationStatus.ACTIVE
        alloc.reallocation_count += 1
        return alloc

    def close_allocation(self, allocation_id: str) -> FundAllocation:
        alloc = self.get_allocation(allocation_id)
        alloc.status = AllocationStatus.CLOSED
        return alloc

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_allocation(self, allocation_id: str) -> FundAllocation:
        if allocation_id not in self._allocations:
            raise FundAllocatorError(f"Allocation '{allocation_id}' not found.")
        return self._allocations[allocation_id]

    def list_allocations(
        self, status: Optional[AllocationStatus] = None
    ) -> list[FundAllocation]:
        allocs = list(self._allocations.values())
        if status is not None:
            allocs = [a for a in allocs if a.status == status]
        return sorted(allocs, key=lambda a: a.blended_yield_pct, reverse=True)

    def total_aum(self) -> float:
        return sum(
            a.total_aum_usd
            for a in self._allocations.values()
            if a.status == AllocationStatus.ACTIVE
        )

    def portfolio_summary(self) -> dict:
        active = [a for a in self._allocations.values() if a.status == AllocationStatus.ACTIVE]
        if not active:
            return {"total_aum_usd": 0.0, "blended_yield_pct": 0.0, "annual_income_usd": 0.0}
        total = sum(a.total_aum_usd for a in active)
        blended = sum(a.total_aum_usd * a.blended_yield_pct for a in active) / total if total else 0.0
        income = sum(a.annual_income_usd for a in active)
        return {
            "total_aum_usd": round(total, 2),
            "blended_yield_pct": round(blended, 4),
            "annual_income_usd": round(income, 2),
            "active_allocations": len(active),
        }

    # ------------------------------------------------------------------
    # Internal weight computation
    # ------------------------------------------------------------------

    def _compute_weights(
        self,
        structures: list[HighYieldStructure],
        strategy: ReallocationStrategy,
        overrides: dict[str, float],
    ) -> dict[str, float]:
        weights: dict[str, float] = {}

        if overrides:
            # Use caller-supplied weights (normalise to sum to 100)
            total = sum(overrides.values())
            for s in structures:
                w = overrides.get(s.structure_id, 0.0)
                weights[s.structure_id] = (w / total * 100.0) if total > 0 else 100.0 / len(structures)
        elif strategy == ReallocationStrategy.EQUAL_WEIGHT:
            w = 100.0 / len(structures)
            for s in structures:
                weights[s.structure_id] = min(w, s.max_allocation_pct)
            # Renormalise
            total = sum(weights.values())
            weights = {k: v / total * 100.0 for k, v in weights.items()}

        elif strategy == ReallocationStrategy.YIELD_WEIGHTED:
            total_yield = sum(s.mid_yield_pct for s in structures) or 1.0
            for s in structures:
                raw = s.mid_yield_pct / total_yield * 100.0
                weights[s.structure_id] = min(raw, s.max_allocation_pct)
            total = sum(weights.values())
            weights = {k: v / total * 100.0 for k, v in weights.items()}

        elif strategy == ReallocationStrategy.RISK_PARITY:
            # Weight inversely proportional to risk score
            inv_risks = {s.structure_id: 1.0 / s.risk_score if s.risk_score > 0 else 1.0 for s in structures}
            total_inv = sum(inv_risks.values()) or 1.0
            for s in structures:
                raw = inv_risks[s.structure_id] / total_inv * 100.0
                weights[s.structure_id] = min(raw, s.max_allocation_pct)
            total = sum(weights.values())
            weights = {k: v / total * 100.0 for k, v in weights.items()}

        elif strategy in (ReallocationStrategy.MOMENTUM, ReallocationStrategy.MIN_VARIANCE,
                          ReallocationStrategy.QUANTUM_OPTIMISED):
            # Placeholder for advanced strategies — use risk-adjusted yield weighting
            rar = {s.structure_id: s.mid_yield_pct / s.risk_score if s.risk_score > 0 else s.mid_yield_pct for s in structures}
            total_rar = sum(rar.values()) or 1.0
            for s in structures:
                raw = rar[s.structure_id] / total_rar * 100.0
                weights[s.structure_id] = min(raw, s.max_allocation_pct)
            total = sum(weights.values())
            weights = {k: v / total * 100.0 for k, v in weights.items()}

        else:
            w = 100.0 / len(structures)
            for s in structures:
                weights[s.structure_id] = w

        # Enforce minimum allocation
        for s in structures:
            if weights[s.structure_id] < s.min_allocation_pct:
                weights[s.structure_id] = s.min_allocation_pct
        # Renormalise once more
        total = sum(weights.values()) or 1.0
        return {k: v / total * 100.0 for k, v in weights.items()}
