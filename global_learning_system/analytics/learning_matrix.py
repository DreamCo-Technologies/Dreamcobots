"""
learning_matrix.py — Creates and updates the Global Learning Matrix.

The Global Learning Matrix is a ranked knowledge store that maps AI methods
to their performance metrics, enabling the system to select, combine, and
evolve the best-performing strategies over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class MatrixEntry:
    """A single entry in the Global Learning Matrix."""

    method_id: str
    method_name: str
    category: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class LearningMatrix:
    """
    Maintains and updates the Global Learning Matrix.

    The matrix maps method identifiers to their aggregate performance
    scores. Entries can be added, updated, queried, and ranked.

    Parameters
    ----------
    decay_factor : float
        Multiplicative factor (0–1) applied to existing scores on each
        update to model temporal decay.
    """

    def __init__(self, decay_factor: float = 1.0):
        if not 0.0 <= decay_factor <= 1.0:
            raise ValueError("decay_factor must be between 0 and 1.")
        self.decay_factor = decay_factor
        self._entries: Dict[str, MatrixEntry] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def upsert(self, entry: MatrixEntry) -> None:
        """
        Insert a new entry or update an existing one.

        If the method already exists, its score is blended:
        ``new_score = existing_score * decay_factor + entry.score * (1 - decay_factor)``
        (or simply replaced when ``decay_factor == 1``).

        Parameters
        ----------
        entry : MatrixEntry
        """
        existing = self._entries.get(entry.method_id)
        if existing is not None and self.decay_factor < 1.0:
            blended = existing.score * self.decay_factor + entry.score * (1.0 - self.decay_factor)
            entry = MatrixEntry(
                method_id=entry.method_id,
                method_name=entry.method_name,
                category=entry.category,
                score=round(blended, 6),
                metadata={**existing.metadata, **entry.metadata},
                last_updated=datetime.now(timezone.utc).isoformat(),
            )
        self._entries[entry.method_id] = entry

    def get(self, method_id: str) -> Optional[MatrixEntry]:
        """Retrieve an entry by method identifier."""
        return self._entries.get(method_id)

    def rank(self, top_n: Optional[int] = None, category: Optional[str] = None) -> List[MatrixEntry]:
        """
        Return entries sorted by score (highest first).

        Parameters
        ----------
        top_n : int | None
            Limit the result to the top *n* entries.
        category : str | None
            Filter entries by category before ranking.
        """
        entries = list(self._entries.values())
        if category is not None:
            entries = [e for e in entries if e.category == category]
        entries.sort(key=lambda e: e.score, reverse=True)
        if top_n is not None:
            entries = entries[:top_n]
        return entries

    def remove(self, method_id: str) -> bool:
        """
        Remove an entry from the matrix.

        Returns
        -------
        bool
            ``True`` if the entry existed and was removed, ``False`` otherwise.
        """
        if method_id in self._entries:
            del self._entries[method_id]
            return True
        return False

    def summary(self) -> Dict[str, Any]:
        """Return aggregate statistics about the current matrix."""
        entries = list(self._entries.values())
        if not entries:
            return {"count": 0}
        scores = [e.score for e in entries]
        categories = list({e.category for e in entries})
        return {
            "count": len(entries),
            "categories": sorted(categories),
            "min_score": min(scores),
            "max_score": max(scores),
            "mean_score": round(sum(scores) / len(scores), 6),
        }

    def count(self) -> int:
        """Return the number of entries in the matrix."""
        return len(self._entries)
