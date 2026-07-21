"""
DreamCo Training Data Store

Manages datasets for training bots to recognize faces, objects, and items
(antiques, coins, currency, etc.) and to learn job-specific tasks.

Usage
-----
    from data.training_data import TrainingDataStore

    store = TrainingDataStore()
    store.add_sample("coin", {"description": "1955 penny", "value_usd": 50.0})
    samples = store.get_samples("coin")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DataSample:
    """A single training data sample."""
    sample_id: str
    category: str          # e.g. 'coin', 'antique', 'face', 'job_task'
    data: dict[str, Any]
    label: str = ""
    split: str = "train"   # 'train' | 'val' | 'test'
    source: str = "manual"


class TrainingDataStore:
    """
    In-memory store for training datasets used by DreamCo bots.

    Supports face recognition, object recognition, item valuation, and
    job-specific task datasets.
    """

    def __init__(self) -> None:
        self._samples: list[DataSample] = []
        self._id_counter: int = 0

    def _next_id(self) -> str:
        self._id_counter += 1
        return f"sample_{self._id_counter:06d}"

    def add_sample(
        self,
        category: str,
        data: dict[str, Any],
        label: str = "",
        split: str = "train",
        source: str = "manual",
    ) -> DataSample:
        """Add a training sample and return it."""
        sample = DataSample(
            sample_id=self._next_id(),
            category=category,
            data=data,
            label=label,
            split=split,
            source=source,
        )
        self._samples.append(sample)
        return sample

    def get_samples(self, category: str, split: Optional[str] = None) -> list[DataSample]:
        """Return samples for *category*, optionally filtered by *split*."""
        results = [s for s in self._samples if s.category == category]
        if split:
            results = [s for s in results if s.split == split]
        return results

    def all_categories(self) -> list[str]:
        """Sorted list of unique categories in the store."""
        return sorted({s.category for s in self._samples})

    def count(self, category: Optional[str] = None) -> int:
        """Total number of samples, optionally filtered by category."""
        if category:
            return sum(1 for s in self._samples if s.category == category)
        return len(self._samples)

    def stats(self) -> dict:
        """Return a summary of the dataset store."""
        return {
            "total_samples": self.count(),
            "categories": self.all_categories(),
            "by_category": {cat: self.count(cat) for cat in self.all_categories()},
        }


__all__ = ["TrainingDataStore", "DataSample"]
