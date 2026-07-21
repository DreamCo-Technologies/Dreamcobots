"""
github_scraper.py — GitHub scraper module.

Ingests repositories, READMEs, and code artefacts from GitHub to feed
the DreamCo global learning pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _REQUESTS_AVAILABLE = False

_LOG = logging.getLogger(__name__)


@dataclass
class GitHubRepo:
    """Represents a scraped GitHub repository."""

    full_name: str
    description: Optional[str]
    url: str
    stars: int
    language: Optional[str]
    topics: List[str] = field(default_factory=list)
    readme_excerpt: Optional[str] = None


class GitHubScraper:
    """
    Scrapes GitHub repositories relevant to AI/ML topics.

    Parameters
    ----------
    token : str | None
        Optional GitHub personal-access token for authenticated requests.
    max_results : int
        Maximum number of repositories to return per search.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, max_results: int = 50):
        self.token = token
        self.max_results = max_results
        self._ingested: List[GitHubRepo] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search_repositories(self, query: str, language: Optional[str] = None) -> List[GitHubRepo]:
        """
        Search GitHub for repositories matching *query*.

        Parameters
        ----------
        query : str
            Topic or keyword string.
        language : str | None
            Optional programming language filter.

        Returns
        -------
        list[GitHubRepo]
        """
        repos = self._fetch_repos(query, language)
        self._ingested.extend(repos)
        return repos

    def get_ingested(self) -> List[GitHubRepo]:
        """Return all repositories collected during this session."""
        return list(self._ingested)

    def clear(self) -> None:
        """Clear the in-memory ingestion cache."""
        self._ingested = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_repos(self, query: str, language: Optional[str]) -> List[GitHubRepo]:
        """Fetch repositories from the GitHub Search API for *query*.

        Falls back to synthetic placeholder records if the API is unreachable
        or returns an error (e.g. rate-limited with no token).
        """
        if _REQUESTS_AVAILABLE:
            try:
                search_q = query
                if language:
                    search_q += f" language:{language}"

                headers: dict = {"Accept": "application/vnd.github+json"}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"

                params = {
                    "q": search_q,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": min(self.max_results, 30),
                }

                resp = _requests.get(
                    f"{self.BASE_URL}/search/repositories",
                    headers=headers,
                    params=params,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                results: List[GitHubRepo] = []
                for item in data.get("items", [])[: self.max_results]:
                    results.append(
                        GitHubRepo(
                            full_name=item["full_name"],
                            description=item.get("description"),
                            url=item["html_url"],
                            stars=item.get("stargazers_count", 0),
                            language=item.get("language"),
                            topics=item.get("topics", []),
                            readme_excerpt=None,
                        )
                    )
                if results:
                    return results
            except Exception as exc:  # requests errors, JSON errors, HTTP errors
                _LOG.debug("GitHub API request failed (%s); using fallback data.", exc)

        # Fallback: return synthetic records when the API is unavailable.
        fallback: List[GitHubRepo] = []
        for i in range(min(3, self.max_results)):
            lang = language or "Python"
            fallback.append(
                GitHubRepo(
                    full_name=f"dreamco-org/{query.replace(' ', '-')}-{i + 1}",
                    description=f"Sample repo #{i + 1} for query '{query}'",
                    url=f"https://github.com/dreamco-org/{query.replace(' ', '-')}-{i + 1}",
                    stars=(i + 1) * 100,
                    language=lang,
                    topics=[query.lower(), "ai", "machine-learning"],
                    readme_excerpt=f"README excerpt for {query} repo #{i + 1}.",
                )
            )
        return fallback
