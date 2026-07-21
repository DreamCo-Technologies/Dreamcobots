"""
paper_scraper.py — Research paper scraper module.

Responsible for discovering and ingesting academic papers from sources such
as arXiv, Semantic Scholar, and PubMed into the DreamCo global learning
pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Paper:
    """Represents a single ingested research paper."""

    title: str
    authors: List[str]
    abstract: str
    source: str
    url: str
    published_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class PaperScraper:
    """
    Scrapes research papers from configurable academic sources.

    Parameters
    ----------
    sources : list[str]
        List of source names to scrape (e.g. ``["arxiv", "semantic_scholar"]``).
    max_results : int
        Maximum number of results to fetch per query.
    """

    SUPPORTED_SOURCES = ["arxiv", "semantic_scholar", "pubmed"]

    def __init__(self, sources: Optional[List[str]] = None, max_results: int = 50):
        self.sources = sources or self.SUPPORTED_SOURCES
        self.max_results = max_results
        self._ingested: List[Paper] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self, query: str) -> List[Paper]:
        """
        Fetch papers matching *query* from all configured sources.

        Parameters
        ----------
        query : str
            Search string (e.g. ``"reinforcement learning"``)

        Returns
        -------
        list[Paper]
            Deduplicated list of ingested papers.
        """
        results: List[Paper] = []
        for source in self.sources:
            results.extend(self._fetch_from_source(source, query))
        papers = self._deduplicate(results)
        self._ingested.extend(papers)
        return papers

    def get_ingested(self) -> List[Paper]:
        """Return all papers collected during this session."""
        return list(self._ingested)

    def clear(self) -> None:
        """Clear the in-memory ingestion cache."""
        self._ingested = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_from_source(self, source: str, query: str) -> List[Paper]:
        """Return mock paper records for *source* and *query*."""
        if source not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Unsupported source: {source!r}")
        return [
            Paper(
                title=f"[{source.upper()}] Sample paper on '{query}' #{i + 1}",
                authors=["DreamCo Research"],
                abstract=f"Abstract {i + 1} from {source} about {query}.",
                source=source,
                url=f"https://{source}.org/papers/{i + 1}",
                tags=[query.lower()],
            )
            for i in range(min(3, self.max_results))
        ]

    @staticmethod
    def _deduplicate(papers: List[Paper]) -> List[Paper]:
        """Remove duplicate papers by URL."""
        seen: set = set()
        unique: List[Paper] = []
        for paper in papers:
            if paper.url not in seen:
                seen.add(paper.url)
                unique.append(paper)
        return unique
