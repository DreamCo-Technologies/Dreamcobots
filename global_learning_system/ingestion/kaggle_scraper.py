"""
kaggle_scraper.py — Kaggle scraper module.

Discovers and ingests datasets and competition artefacts from Kaggle
to enrich the DreamCo global learning pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KaggleDataset:
    """Represents a single Kaggle dataset or competition entry."""

    title: str
    owner: str
    url: str
    size_mb: float
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    download_count: int = 0


class KaggleScraper:
    """
    Scrapes datasets and competitions from Kaggle.

    Parameters
    ----------
    api_key : str | None
        Optional Kaggle API key for authenticated requests.
    max_results : int
        Maximum number of results to return per search.
    """

    BASE_URL = "https://www.kaggle.com/api/v1"

    def __init__(self, api_key: Optional[str] = None, max_results: int = 50):
        self.api_key = api_key
        self.max_results = max_results
        self._ingested: List[KaggleDataset] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search_datasets(self, query: str) -> List[KaggleDataset]:
        """
        Search Kaggle for datasets matching *query*.

        Parameters
        ----------
        query : str
            Topic or keyword string.

        Returns
        -------
        list[KaggleDataset]
        """
        datasets = self._fetch_datasets(query)
        self._ingested.extend(datasets)
        return datasets

    def get_ingested(self) -> List[KaggleDataset]:
        """Return all datasets collected during this session."""
        return list(self._ingested)

    def clear(self) -> None:
        """Clear the in-memory ingestion cache."""
        self._ingested = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_datasets(self, query: str) -> List[KaggleDataset]:
        """Return mock dataset records for *query*."""
        results: List[KaggleDataset] = []
        for i in range(min(3, self.max_results)):
            results.append(
                KaggleDataset(
                    title=f"{query.title()} Dataset #{i + 1}",
                    owner=f"kaggle-user-{i + 1}",
                    url=f"https://www.kaggle.com/datasets/kaggle-user-{i + 1}/{query.replace(' ', '-')}-{i + 1}",
                    size_mb=round((i + 1) * 12.5, 2),
                    tags=[query.lower(), "csv", "tabular"],
                    description=f"Sample Kaggle dataset #{i + 1} related to {query}.",
                    download_count=(i + 1) * 500,
                )
            )
        return results
