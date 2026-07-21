"""
SAM.gov API Integration — Government Contract Search

Searches the SAM.gov opportunities API for federal contracts matching a
given keyword.  Falls back to a mock response when no API key is present.

Usage
-----
    api = SAMGovAPI()
    contracts = api.search_contracts(keyword="IT services")
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401

SAM_GOV_BASE_URL = "https://api.sam.gov/opportunities/v2/search"


class SAMGovAPI:
    """
    Client for the SAM.gov Opportunities API.

    Parameters
    ----------
    api_key : SAM.gov API key (default: env SAM_GOV_API_KEY).
    mock    : Force mock mode (no HTTP calls).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        mock: bool = False,
    ) -> None:
        self._api_key = api_key or os.environ.get("SAM_GOV_API_KEY", "")
        self._mock = mock or not self._api_key

    @property
    def is_mock(self) -> bool:
        return self._mock

    def search_contracts(
        self,
        keyword: str = "IT",
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for contract opportunities matching *keyword*.

        Returns a dict with keys: ``opportunities`` (list), ``total`` (int),
        ``keyword`` (str), ``timestamp`` (str).
        """
        if self._mock:
            return self._mock_response(keyword, limit)
        return self._live_search(keyword, limit)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _live_search(self, keyword: str, limit: int) -> Dict[str, Any]:
        """Hit the real SAM.gov API."""
        import requests  # type: ignore[import]

        params: Dict[str, Any] = {
            "api_key": self._api_key,
            "q": keyword,
            "limit": limit,
        }
        response = requests.get(SAM_GOV_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        opportunities = data.get("opportunitiesData", [])
        return {
            "opportunities": opportunities,
            "total": len(opportunities),
            "keyword": keyword,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _mock_response(self, keyword: str, limit: int) -> Dict[str, Any]:
        """Return sample contract data for testing."""
        mock_opportunities = [
            {
                "noticeId": f"MOCK-{i:04d}",
                "title": f"Sample {keyword} Contract #{i}",
                "agency": "Dept. of Example",
                "type": "Solicitation",
                "postedDate": "2026-01-01",
                "responseDeadLine": "2026-03-01",
                "naicsCode": "541519",
                "baseType": "SOLICITATION",
                "archiveType": "auto30",
                "estimatedValue": 5_000 * (i + 1),
            }
            for i in range(min(limit, 3))
        ]
        return {
            "opportunities": mock_opportunities,
            "total": len(mock_opportunities),
            "keyword": keyword,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
