# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Country-level lab tracking and monitoring for the Global AI Learning Matrix."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Country:
    code: str
    name: str
    region: str
    lab_count: int
    active_models: int
    health_score: float  # 0-100


# Seed data: 50+ countries across regions
_SEED_COUNTRIES = [
    # Americas
    Country("US", "United States", "Americas", 450, 1200, 94.5),
    Country("CA", "Canada", "Americas", 120, 310, 91.2),
    Country("BR", "Brazil", "Americas", 85, 220, 78.4),
    Country("MX", "Mexico", "Americas", 45, 130, 72.1),
    Country("AR", "Argentina", "Americas", 38, 95, 70.8),
    Country("CL", "Chile", "Americas", 30, 80, 73.5),
    Country("CO", "Colombia", "Americas", 25, 65, 68.9),
    Country("PE", "Peru", "Americas", 18, 45, 65.3),
    # Europe
    Country("GB", "United Kingdom", "Europe", 310, 820, 93.1),
    Country("DE", "Germany", "Europe", 295, 780, 92.7),
    Country("FR", "France", "Europe", 260, 690, 91.4),
    Country("NL", "Netherlands", "Europe", 140, 370, 90.8),
    Country("SE", "Sweden", "Europe", 115, 300, 89.6),
    Country("CH", "Switzerland", "Europe", 110, 290, 92.3),
    Country("ES", "Spain", "Europe", 105, 275, 85.2),
    Country("IT", "Italy", "Europe", 98, 255, 83.7),
    Country("PL", "Poland", "Europe", 72, 185, 80.1),
    Country("NO", "Norway", "Europe", 65, 170, 88.4),
    Country("DK", "Denmark", "Europe", 62, 160, 87.9),
    Country("FI", "Finland", "Europe", 58, 150, 88.1),
    Country("BE", "Belgium", "Europe", 55, 142, 86.5),
    Country("AT", "Austria", "Europe", 50, 130, 85.3),
    # Asia-Pacific
    Country("CN", "China", "Asia-Pacific", 620, 1650, 88.3),
    Country("JP", "Japan", "Asia-Pacific", 380, 1010, 91.8),
    Country("KR", "South Korea", "Asia-Pacific", 220, 580, 90.4),
    Country("IN", "India", "Asia-Pacific", 310, 820, 83.6),
    Country("AU", "Australia", "Asia-Pacific", 145, 385, 89.7),
    Country("SG", "Singapore", "Asia-Pacific", 130, 345, 93.4),
    Country("TW", "Taiwan", "Asia-Pacific", 115, 305, 90.1),
    Country("NZ", "New Zealand", "Asia-Pacific", 42, 110, 87.2),
    Country("MY", "Malaysia", "Asia-Pacific", 55, 145, 78.9),
    Country("TH", "Thailand", "Asia-Pacific", 48, 125, 74.3),
    Country("ID", "Indonesia", "Asia-Pacific", 62, 160, 72.8),
    Country("VN", "Vietnam", "Asia-Pacific", 40, 105, 70.5),
    Country("PH", "Philippines", "Asia-Pacific", 35, 90, 69.1),
    Country("PK", "Pakistan", "Asia-Pacific", 28, 72, 64.2),
    Country("BD", "Bangladesh", "Asia-Pacific", 20, 52, 62.4),
    # Middle East
    Country("IL", "Israel", "Middle East", 185, 490, 94.2),
    Country("AE", "UAE", "Middle East", 120, 320, 88.6),
    Country("SA", "Saudi Arabia", "Middle East", 95, 250, 82.4),
    Country("TR", "Turkey", "Middle East", 78, 205, 79.1),
    Country("IR", "Iran", "Middle East", 45, 118, 65.7),
    Country("QA", "Qatar", "Middle East", 38, 100, 80.3),
    Country("JO", "Jordan", "Middle East", 22, 58, 71.5),
    # Africa
    Country("ZA", "South Africa", "Africa", 68, 178, 77.3),
    Country("EG", "Egypt", "Africa", 52, 137, 72.6),
    Country("NG", "Nigeria", "Africa", 45, 118, 68.4),
    Country("KE", "Kenya", "Africa", 35, 92, 70.1),
    Country("ET", "Ethiopia", "Africa", 18, 47, 59.8),
    Country("GH", "Ghana", "Africa", 22, 58, 65.2),
    Country("TN", "Tunisia", "Africa", 28, 73, 69.7),
    Country("MA", "Morocco", "Africa", 32, 84, 71.8),
]


class CountryMonitor:
    """Tracks country-level AI lab data and health metrics."""

    def __init__(self):
        self._countries: dict[str, Country] = {}
        for c in _SEED_COUNTRIES:
            self._countries[c.code.upper()] = c

    def add_country(self, country: Country) -> None:
        self._countries[country.code.upper()] = country

    def get_country(self, code: str) -> Country:
        key = code.upper()
        if key not in self._countries:
            raise KeyError(f"Country code '{code}' not found.")
        return self._countries[key]

    def list_countries(self, region: Optional[str] = None) -> list[Country]:
        countries = list(self._countries.values())
        if region:
            countries = [c for c in countries if c.region.lower() == region.lower()]
        return countries

    def update_lab_count(self, code: str, count: int) -> None:
        country = self.get_country(code)
        country.lab_count = count

    def get_top_countries(self, n: int = 10) -> list[Country]:
        return sorted(self._countries.values(), key=lambda c: c.lab_count, reverse=True)[:n]

    def get_global_stats(self) -> dict:
        countries = list(self._countries.values())
        total_labs = sum(c.lab_count for c in countries)
        avg_health = sum(c.health_score for c in countries) / len(countries) if countries else 0.0

        region_labs: dict[str, int] = {}
        for c in countries:
            region_labs[c.region] = region_labs.get(c.region, 0) + c.lab_count
        top_region = max(region_labs, key=region_labs.get) if region_labs else "N/A"

        return {
            "total_countries": len(countries),
            "total_labs": total_labs,
            "avg_health_score": round(avg_health, 2),
            "top_region": top_region,
        }
