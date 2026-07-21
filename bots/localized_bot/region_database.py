"""
Region Database — 30+ global regions for the DreamCo Localized Bot.

Each region entry includes:
  - region_id, region_name, country_code, language_code, language_name
  - industries (3-5 dominant industries)
  - population_millions, timezone, currency_code

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

_REGIONS: list[dict] = [
    {
        "region_id": "US",
        "region_name": "United States",
        "country_code": "US",
        "language_code": "en",
        "language_name": "English",
        "industries": ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"],
        "population_millions": 331.0,
        "timezone": "America/New_York",
        "currency_code": "USD",
    },
    {
        "region_id": "UK",
        "region_name": "United Kingdom",
        "country_code": "GB",
        "language_code": "en",
        "language_name": "English",
        "industries": ["Finance", "Technology", "Healthcare", "Education"],
        "population_millions": 67.0,
        "timezone": "Europe/London",
        "currency_code": "GBP",
    },
    {
        "region_id": "Mexico",
        "region_name": "Mexico",
        "country_code": "MX",
        "language_code": "es",
        "language_name": "Spanish",
        "industries": ["Manufacturing", "Agriculture", "Tourism", "Energy"],
        "population_millions": 128.0,
        "timezone": "America/Mexico_City",
        "currency_code": "MXN",
    },
    {
        "region_id": "Brazil",
        "region_name": "Brazil",
        "country_code": "BR",
        "language_code": "pt",
        "language_name": "Portuguese",
        "industries": ["Agriculture", "Mining", "Technology", "Finance", "Tourism"],
        "population_millions": 213.0,
        "timezone": "America/Sao_Paulo",
        "currency_code": "BRL",
    },
    {
        "region_id": "France",
        "region_name": "France",
        "country_code": "FR",
        "language_code": "fr",
        "language_name": "French",
        "industries": ["Luxury Goods", "Tourism", "Aerospace", "Agriculture", "Finance"],
        "population_millions": 67.0,
        "timezone": "Europe/Paris",
        "currency_code": "EUR",
    },
    {
        "region_id": "Germany",
        "region_name": "Germany",
        "country_code": "DE",
        "language_code": "de",
        "language_name": "German",
        "industries": ["Automotive", "Manufacturing", "Technology", "Finance", "Healthcare"],
        "population_millions": 83.0,
        "timezone": "Europe/Berlin",
        "currency_code": "EUR",
    },
    {
        "region_id": "Japan",
        "region_name": "Japan",
        "country_code": "JP",
        "language_code": "ja",
        "language_name": "Japanese",
        "industries": ["Automotive", "Electronics", "Robotics", "Finance", "Tourism"],
        "population_millions": 125.0,
        "timezone": "Asia/Tokyo",
        "currency_code": "JPY",
    },
    {
        "region_id": "China",
        "region_name": "China",
        "country_code": "CN",
        "language_code": "zh",
        "language_name": "Chinese",
        "industries": ["Manufacturing", "Technology", "Finance", "Retail", "Energy"],
        "population_millions": 1412.0,
        "timezone": "Asia/Shanghai",
        "currency_code": "CNY",
    },
    {
        "region_id": "India",
        "region_name": "India",
        "country_code": "IN",
        "language_code": "hi",
        "language_name": "Hindi",
        "industries": ["IT Services", "Agriculture", "Manufacturing", "Finance", "Pharmaceuticals"],
        "population_millions": 1380.0,
        "timezone": "Asia/Kolkata",
        "currency_code": "INR",
    },
    {
        "region_id": "Nigeria",
        "region_name": "Nigeria",
        "country_code": "NG",
        "language_code": "en",
        "language_name": "English",
        "industries": ["Oil & Gas", "Agriculture", "Finance", "Telecommunications"],
        "population_millions": 211.0,
        "timezone": "Africa/Lagos",
        "currency_code": "NGN",
    },
    {
        "region_id": "South_Africa",
        "region_name": "South Africa",
        "country_code": "ZA",
        "language_code": "en",
        "language_name": "English",
        "industries": ["Mining", "Finance", "Tourism", "Manufacturing", "Agriculture"],
        "population_millions": 59.0,
        "timezone": "Africa/Johannesburg",
        "currency_code": "ZAR",
    },
    {
        "region_id": "Australia",
        "region_name": "Australia",
        "country_code": "AU",
        "language_code": "en",
        "language_name": "English",
        "industries": ["Mining", "Agriculture", "Finance", "Tourism", "Healthcare"],
        "population_millions": 25.0,
        "timezone": "Australia/Sydney",
        "currency_code": "AUD",
    },
    {
        "region_id": "Canada",
        "region_name": "Canada",
        "country_code": "CA",
        "language_code": "en",
        "language_name": "English",
        "industries": ["Energy", "Finance", "Technology", "Agriculture", "Healthcare"],
        "population_millions": 38.0,
        "timezone": "America/Toronto",
        "currency_code": "CAD",
    },
    {
        "region_id": "Saudi_Arabia",
        "region_name": "Saudi Arabia",
        "country_code": "SA",
        "language_code": "ar",
        "language_name": "Arabic",
        "industries": ["Oil & Gas", "Finance", "Construction", "Tourism"],
        "population_millions": 35.0,
        "timezone": "Asia/Riyadh",
        "currency_code": "SAR",
    },
    {
        "region_id": "South_Korea",
        "region_name": "South Korea",
        "country_code": "KR",
        "language_code": "ko",
        "language_name": "Korean",
        "industries": ["Electronics", "Automotive", "Finance", "Technology", "Entertainment"],
        "population_millions": 52.0,
        "timezone": "Asia/Seoul",
        "currency_code": "KRW",
    },
    {
        "region_id": "Russia",
        "region_name": "Russia",
        "country_code": "RU",
        "language_code": "ru",
        "language_name": "Russian",
        "industries": ["Energy", "Mining", "Manufacturing", "Agriculture", "Technology"],
        "population_millions": 144.0,
        "timezone": "Europe/Moscow",
        "currency_code": "RUB",
    },
    {
        "region_id": "Indonesia",
        "region_name": "Indonesia",
        "country_code": "ID",
        "language_code": "id",
        "language_name": "Indonesian",
        "industries": ["Agriculture", "Mining", "Manufacturing", "Tourism", "Finance"],
        "population_millions": 273.0,
        "timezone": "Asia/Jakarta",
        "currency_code": "IDR",
    },
    {
        "region_id": "Argentina",
        "region_name": "Argentina",
        "country_code": "AR",
        "language_code": "es",
        "language_name": "Spanish",
        "industries": ["Agriculture", "Finance", "Energy", "Manufacturing", "Tourism"],
        "population_millions": 45.0,
        "timezone": "America/Argentina/Buenos_Aires",
        "currency_code": "ARS",
    },
    {
        "region_id": "Spain",
        "region_name": "Spain",
        "country_code": "ES",
        "language_code": "es",
        "language_name": "Spanish",
        "industries": ["Tourism", "Automotive", "Finance", "Agriculture", "Energy"],
        "population_millions": 47.0,
        "timezone": "Europe/Madrid",
        "currency_code": "EUR",
    },
    {
        "region_id": "Italy",
        "region_name": "Italy",
        "country_code": "IT",
        "language_code": "it",
        "language_name": "Italian",
        "industries": ["Fashion", "Automotive", "Tourism", "Agriculture", "Finance"],
        "population_millions": 60.0,
        "timezone": "Europe/Rome",
        "currency_code": "EUR",
    },
    {
        "region_id": "Egypt",
        "region_name": "Egypt",
        "country_code": "EG",
        "language_code": "ar",
        "language_name": "Arabic",
        "industries": ["Tourism", "Oil & Gas", "Agriculture", "Manufacturing", "Finance"],
        "population_millions": 102.0,
        "timezone": "Africa/Cairo",
        "currency_code": "EGP",
    },
    {
        "region_id": "Turkey",
        "region_name": "Turkey",
        "country_code": "TR",
        "language_code": "tr",
        "language_name": "Turkish",
        "industries": ["Tourism", "Textile", "Automotive", "Agriculture", "Finance"],
        "population_millions": 84.0,
        "timezone": "Europe/Istanbul",
        "currency_code": "TRY",
    },
    {
        "region_id": "Thailand",
        "region_name": "Thailand",
        "country_code": "TH",
        "language_code": "th",
        "language_name": "Thai",
        "industries": ["Tourism", "Manufacturing", "Agriculture", "Electronics", "Finance"],
        "population_millions": 70.0,
        "timezone": "Asia/Bangkok",
        "currency_code": "THB",
    },
    {
        "region_id": "Vietnam",
        "region_name": "Vietnam",
        "country_code": "VN",
        "language_code": "vi",
        "language_name": "Vietnamese",
        "industries": ["Manufacturing", "Agriculture", "Tourism", "Technology", "Retail"],
        "population_millions": 97.0,
        "timezone": "Asia/Ho_Chi_Minh",
        "currency_code": "VND",
    },
    {
        "region_id": "Poland",
        "region_name": "Poland",
        "country_code": "PL",
        "language_code": "pl",
        "language_name": "Polish",
        "industries": ["Manufacturing", "IT Services", "Agriculture", "Finance", "Energy"],
        "population_millions": 38.0,
        "timezone": "Europe/Warsaw",
        "currency_code": "PLN",
    },
    {
        "region_id": "Netherlands",
        "region_name": "Netherlands",
        "country_code": "NL",
        "language_code": "nl",
        "language_name": "Dutch",
        "industries": ["Finance", "Agriculture", "Technology", "Logistics", "Energy"],
        "population_millions": 17.0,
        "timezone": "Europe/Amsterdam",
        "currency_code": "EUR",
    },
    {
        "region_id": "UAE",
        "region_name": "United Arab Emirates",
        "country_code": "AE",
        "language_code": "ar",
        "language_name": "Arabic",
        "industries": ["Oil & Gas", "Finance", "Tourism", "Construction", "Retail"],
        "population_millions": 10.0,
        "timezone": "Asia/Dubai",
        "currency_code": "AED",
    },
    {
        "region_id": "Colombia",
        "region_name": "Colombia",
        "country_code": "CO",
        "language_code": "es",
        "language_name": "Spanish",
        "industries": ["Energy", "Agriculture", "Mining", "Finance", "Tourism"],
        "population_millions": 51.0,
        "timezone": "America/Bogota",
        "currency_code": "COP",
    },
    {
        "region_id": "Pakistan",
        "region_name": "Pakistan",
        "country_code": "PK",
        "language_code": "ur",
        "language_name": "Urdu",
        "industries": ["Agriculture", "Textile", "Manufacturing", "Finance", "IT Services"],
        "population_millions": 220.0,
        "timezone": "Asia/Karachi",
        "currency_code": "PKR",
    },
    {
        "region_id": "Bangladesh",
        "region_name": "Bangladesh",
        "country_code": "BD",
        "language_code": "bn",
        "language_name": "Bengali",
        "industries": ["Textile", "Agriculture", "Manufacturing", "Finance", "IT Services"],
        "population_millions": 166.0,
        "timezone": "Asia/Dhaka",
        "currency_code": "BDT",
    },
]

_REGION_INDEX: dict[str, dict] = {r["region_id"]: r for r in _REGIONS}


class RegionDatabase:
    """In-memory database of global regions with lookup and search capabilities."""

    def get_region(self, region_id: str) -> dict:
        """Return the region dict for *region_id*, or raise KeyError if not found."""
        if region_id not in _REGION_INDEX:
            raise KeyError(f"Region '{region_id}' not found in database.")
        return _REGION_INDEX[region_id]

    def list_regions(self) -> list:
        """Return all region records as a list."""
        return list(_REGIONS)

    def get_regions_by_language(self, language_code: str) -> list:
        """Return all regions whose primary language matches *language_code*."""
        return [r for r in _REGIONS if r["language_code"] == language_code]

    def get_regions_by_industry(self, industry: str) -> list:
        """Return regions that list *industry* among their dominant industries (case-insensitive)."""
        industry_lower = industry.lower()
        return [
            r for r in _REGIONS
            if any(ind.lower() == industry_lower for ind in r["industries"])
        ]

    def search_regions(self, query: str) -> list:
        """Return regions whose name or language name contains *query* (case-insensitive)."""
        query_lower = query.lower()
        return [
            r for r in _REGIONS
            if query_lower in r["region_name"].lower()
            or query_lower in r["language_name"].lower()
        ]
