"""
API client for the 211 Resource and Eligibility Checker Bot.

Handles all outbound HTTP calls to:
  - The 211 open-API (resource search)
  - Future eligibility data APIs

The client degrades gracefully when no API key is configured: it returns
clearly marked mock data so the bot can still demonstrate its workflow
in development/demo environments.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from config import API_211_BASE_URL, API_211_KEY, RESOURCE_CATEGORIES

# Allowed URL schemes for the 211 API base URL (guards against SSRF)
_ALLOWED_SCHEMES = {"https", "http"}


# ---------------------------------------------------------------------------
# Mock data – returned when the 211 API key is absent or the network is
# unavailable.  Replace with real 211 API results in production.
# ---------------------------------------------------------------------------
_MOCK_RESOURCES: dict[str, list[dict]] = {
    "housing": [
        {
            "name": "City Housing Authority – Emergency Shelter",
            "address": "123 Main St, Anytown, USA",
            "phone": "1-800-555-0101",
            "description": "Emergency shelter for families and individuals in crisis.",
            "url": "https://example.org/housing",
        },
        {
            "name": "Habitat for Humanity – Home Repair",
            "address": "456 Oak Ave, Anytown, USA",
            "phone": "1-800-555-0102",
            "description": "Critical home repairs for low-income homeowners.",
            "url": "https://www.habitat.org",
        },
    ],
    "food": [
        {
            "name": "Community Food Bank",
            "address": "789 Elm St, Anytown, USA",
            "phone": "1-800-555-0201",
            "description": "Free groceries and meals for individuals and families in need.",
            "url": "https://example.org/foodbank",
        },
        {
            "name": "Meals on Wheels",
            "address": "321 Pine Rd, Anytown, USA",
            "phone": "1-800-555-0202",
            "description": "Home-delivered meals for seniors and disabled individuals.",
            "url": "https://www.mealsonwheelsamerica.org",
        },
    ],
    "mental_health": [
        {
            "name": "Crisis Hotline – 988 Suicide & Crisis Lifeline",
            "address": "Available 24/7",
            "phone": "988",
            "description": "Free and confidential emotional support for people in suicidal crisis.",
            "url": "https://988lifeline.org",
        },
        {
            "name": "Community Mental Health Center",
            "address": "654 Maple Blvd, Anytown, USA",
            "phone": "1-800-555-0301",
            "description": "Outpatient mental health counseling and psychiatric services.",
            "url": "https://example.org/mentalhealth",
        },
    ],
    "health": [
        {
            "name": "Local Community Health Clinic",
            "address": "987 Birch Dr, Anytown, USA",
            "phone": "1-800-555-0401",
            "description": "Low-cost primary care on a sliding-scale fee.",
            "url": "https://example.org/clinic",
        },
    ],
    "utilities": [
        {
            "name": "LIHEAP – Energy Assistance Program",
            "address": "Online / by phone",
            "phone": "1-866-674-6327",
            "description": "Federal program to help low-income households with energy bills.",
            "url": "https://www.acf.hhs.gov/ocs/low-income-home-energy-assistance-program-liheap",
        },
    ],
}


class APIClient211:
    """Client for the 211 resource search API."""

    def __init__(self, api_key: str = API_211_KEY, base_url: str = API_211_BASE_URL):
        parsed = urllib.parse.urlparse(base_url)
        if parsed.scheme not in _ALLOWED_SCHEMES or not parsed.netloc:
            raise ValueError(
                f"Invalid API_211_BASE_URL: '{base_url}'. "
                "Must be an absolute http:// or https:// URL."
            )
        self._api_key = api_key
        self._base_url = base_url

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search_resources(
        self,
        category: str,
        location: str,
        radius_miles: int = 25,
        limit: int = 5,
    ) -> list[dict]:
        """
        Search for resources matching *category* near *location*.

        Falls back to mock data when no API key is set or on network error.

        Parameters
        ----------
        category : str
            One of the categories defined in :data:`config.RESOURCE_CATEGORIES`.
        location : str
            City name or ZIP code.
        radius_miles : int
            Search radius in miles.
        limit : int
            Maximum number of results to return.

        Returns
        -------
        list[dict]
            Each dict contains at minimum: name, address, phone, description.
        """
        if not self._api_key:
            return self._mock_results(category, limit)

        try:
            return self._live_search(category, location, radius_miles, limit)
        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            return self._mock_results(category, limit)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _live_search(
        self,
        category: str,
        location: str,
        radius_miles: int,
        limit: int,
    ) -> list[dict]:
        """Make a live request to the 211 API."""
        params = urllib.parse.urlencode(
            {
                "keyword": category,
                "location": location,
                "radius": radius_miles,
                "limit": limit,
                "api_key": self._api_key,
            }
        )
        url = f"{self._base_url}?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return self._normalise(data)

    @staticmethod
    def _normalise(raw: Any) -> list[dict]:
        """Normalise a 211 API response to our internal schema."""
        resources = []
        # The 211 open API returns results under different keys depending on
        # the endpoint version; handle both list and dict payloads.
        items = raw if isinstance(raw, list) else raw.get("results", raw.get("data", []))
        for item in items:
            resources.append(
                {
                    "name": item.get("AgencyName") or item.get("name", "Unknown"),
                    "address": item.get("SiteAddress") or item.get("address", "N/A"),
                    "phone": item.get("Phone") or item.get("phone", "N/A"),
                    "description": item.get("ServiceDescription") or item.get("description", ""),
                    "url": item.get("URL") or item.get("url", ""),
                }
            )
        return resources

    @staticmethod
    def _mock_results(category: str, limit: int) -> list[dict]:
        """Return mock results for development / demo use."""
        # Normalise category key
        key = category.lower().replace(" ", "_").replace("-", "_")
        # Fall back to housing mock data if category not found
        mocks = _MOCK_RESOURCES.get(key, _MOCK_RESOURCES.get("housing", []))
        results = mocks[:limit]
        for r in results:
            r.setdefault("_mock", True)
        return results
