"""
Real Estate AI module for Dreamcobots platform.

Provides AI-powered property listing aggregation, market trend analysis,
valuation estimation, lead management, and report generation for real estate.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Property:
    """Represents a real estate property listing."""
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    listing_type: str          # 'sale', 'rent'
    price: float
    bedrooms: int
    bathrooms: float
    sqft: float
    description: str = ""
    status: str = "active"     # 'active', 'pending', 'sold', 'rented'
    tags: List[str] = field(default_factory=list)


@dataclass
class Lead:
    """Represents a prospective buyer or renter lead."""
    lead_id: str
    name: str
    email: str
    phone: str
    interest: str              # 'buy', 'rent', 'invest'
    budget: float
    preferred_cities: List[str] = field(default_factory=list)
    status: str = "new"        # 'new', 'contacted', 'qualified', 'closed'


# ---------------------------------------------------------------------------
# RealEstateAI bot
# ---------------------------------------------------------------------------

class RealEstateAI(BotBase):
    """
    AI-powered real estate management bot.

    Aggregates listings, performs market analysis, estimates property values,
    manages leads, and generates analytical reports.

    Args:
        autonomy: Autonomy level.
        scaling: Scaling level.
    """

    def __init__(
        self,
        autonomy: AutonomyLevel = AutonomyLevel.SEMI_AUTONOMOUS,
        scaling: ScalingLevel = ScalingLevel.MODERATE,
    ) -> None:
        super().__init__("RealEstateAI", autonomy, scaling)
        self._properties: Dict[str, Property] = {}
        self._leads: Dict[str, Lead] = {}
        self._market_data: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Property management
    # ------------------------------------------------------------------

    def add_property(self, prop: Property) -> Property:
        """Register a property listing."""
        self._properties[prop.property_id] = prop
        return prop

    def get_property(self, property_id: str) -> Optional[Property]:
        """Return a property or None."""
        return self._properties.get(property_id)

    def search_properties(
        self,
        city: Optional[str] = None,
        listing_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_bedrooms: Optional[int] = None,
    ) -> List[Property]:
        """
        Search listings matching all provided criteria.

        Args:
            city: Filter by city (case-insensitive).
            listing_type: 'sale' or 'rent'.
            min_price: Minimum listing price.
            max_price: Maximum listing price.
            min_bedrooms: Minimum bedroom count.

        Returns:
            List of matching Property objects.
        """
        results = list(self._properties.values())
        if city:
            results = [p for p in results if p.city.lower() == city.lower()]
        if listing_type:
            results = [p for p in results if p.listing_type == listing_type]
        if min_price is not None:
            results = [p for p in results if p.price >= min_price]
        if max_price is not None:
            results = [p for p in results if p.price <= max_price]
        if min_bedrooms is not None:
            results = [p for p in results if p.bedrooms >= min_bedrooms]
        return results

    def update_property_status(self, property_id: str, status: str) -> bool:
        """Update the status of a property. Returns True if found."""
        prop = self._properties.get(property_id)
        if prop:
            prop.status = status
            return True
        return False

    # ------------------------------------------------------------------
    # Market analysis
    # ------------------------------------------------------------------

    def record_market_data(self, city: str, avg_price: float, volume: int, month: str) -> None:
        """Record a monthly market data point for trend analysis."""
        self._market_data.append({
            "city": city,
            "avg_price": avg_price,
            "volume": volume,
            "month": month,
        })

    def analyze_market_trends(self, city: str) -> Dict[str, Any]:
        """
        Compute market trend statistics for *city*.

        Returns:
            Dict with avg_price, min_price, max_price, total_volume, trend.
        """
        city_data = [d for d in self._market_data if d["city"].lower() == city.lower()]
        if not city_data:
            return {"city": city, "trend": "no data"}

        prices = [d["avg_price"] for d in city_data]
        volumes = [d["volume"] for d in city_data]
        trend = "rising" if len(prices) >= 2 and prices[-1] > prices[0] else "stable_or_declining"

        return {
            "city": city,
            "data_points": len(city_data),
            "avg_price": round(sum(prices) / len(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
            "total_volume": sum(volumes),
            "trend": trend,
        }

    def estimate_value(self, sqft: float, bedrooms: int, city: str) -> float:
        """
        Estimate a property's value using recent market data for *city*.

        Falls back to a conservative national average if no city data exists.

        Args:
            sqft: Property square footage.
            bedrooms: Number of bedrooms.
            city: City where the property is located.

        Returns:
            Estimated value in USD.
        """
        city_data = [d for d in self._market_data if d["city"].lower() == city.lower()]
        if city_data:
            avg_price_per_sqft = sum(d["avg_price"] for d in city_data) / len(city_data) / 1500
        else:
            avg_price_per_sqft = 200.0  # national fallback $/sqft

        base_value = sqft * avg_price_per_sqft
        bedroom_premium = bedrooms * 5000
        return round(base_value + bedroom_premium, 2)

    # ------------------------------------------------------------------
    # Lead management
    # ------------------------------------------------------------------

    def add_lead(self, lead: Lead) -> Lead:
        """Register a new lead."""
        self._leads[lead.lead_id] = lead
        return lead

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Return a lead or None."""
        return self._leads.get(lead_id)

    def qualify_lead(self, lead_id: str) -> bool:
        """Mark a lead as qualified. Returns True if found."""
        lead = self._leads.get(lead_id)
        if lead:
            lead.status = "qualified"
            return True
        return False

    def match_properties_to_lead(self, lead_id: str) -> List[Property]:
        """
        Return properties matching a lead's budget and preferred cities.
        """
        lead = self._leads.get(lead_id)
        if not lead:
            return []
        return self.search_properties(
            listing_type=("sale" if lead.interest in ("buy", "invest") else "rent"),
            max_price=lead.budget,
        )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> Dict[str, Any]:
        """Generate a real estate portfolio and market summary report."""
        active = [p for p in self._properties.values() if p.status == "active"]
        sold = [p for p in self._properties.values() if p.status in ("sold", "rented")]
        cities = list({p.city for p in self._properties.values()})
        return {
            "total_listings": len(self._properties),
            "active_listings": len(active),
            "sold_or_rented": len(sold),
            "total_leads": len(self._leads),
            "qualified_leads": sum(1 for l in self._leads.values() if l.status == "qualified"),
            "cities_covered": cities,
        }

    # ------------------------------------------------------------------
    # Task runner
    # ------------------------------------------------------------------

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "")
        if task_type == "search_properties":
            props = self.search_properties(
                city=task.get("city"),
                listing_type=task.get("listing_type"),
                max_price=task.get("max_price"),
            )
            return {"status": "ok", "count": len(props)}
        if task_type == "estimate_value":
            value = self.estimate_value(
                sqft=float(task.get("sqft", 0)),
                bedrooms=int(task.get("bedrooms", 0)),
                city=task.get("city", ""),
            )
            return {"status": "ok", "estimated_value": value}
        return super()._run_task(task)
