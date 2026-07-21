"""
Big Bro AI — Route & GPS Intelligence

Integrates routing logic, resource eligibility navigation (like the
211 bot), city app catalogues, and geographic-aware guidance so Big
Bro can direct users to the right services, franchises, and opportunities
in their area.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Resource categories
# ---------------------------------------------------------------------------

class ResourceCategory(Enum):
    FINANCIAL = "financial"
    HOUSING = "housing"
    FOOD = "food"
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    TRANSPORTATION = "transportation"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    GOVERNMENT = "government"
    COMMUNITY = "community"


# ---------------------------------------------------------------------------
# Route types
# ---------------------------------------------------------------------------

class RouteType(Enum):
    SERVICE = "service"         # Path to a government / community service
    OPPORTUNITY = "opportunity" # Income or business opportunity
    FRANCHISE = "franchise"     # Franchise location
    CATALOG = "catalog"         # Catalog ordering point
    EDUCATION = "education"     # Learning resource
    TECH = "tech"               # Technology resource


# ---------------------------------------------------------------------------
# Resource record
# ---------------------------------------------------------------------------

@dataclass
class Resource:
    """
    A local or online resource that Big Bro can route users to.

    Attributes
    ----------
    resource_id : str
        Unique identifier.
    name : str
        Display name.
    category : ResourceCategory
        Service category.
    description : str
        What this resource provides.
    eligibility : list[str]
        Who qualifies (e.g., "low income", "veterans", "all").
    url : str
        Web address if available.
    phone : str
        Phone number if applicable.
    city : str
        City or region (empty = national / online).
    state : str
        State/province (empty = national).
    free : bool
        Whether the resource is free.
    tags : list[str]
        Searchable tags.
    """

    resource_id: str
    name: str
    category: ResourceCategory
    description: str
    eligibility: list[str] = field(default_factory=list)
    url: str = ""
    phone: str = ""
    city: str = ""
    state: str = ""
    free: bool = True
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "eligibility": self.eligibility,
            "url": self.url,
            "phone": self.phone,
            "city": self.city,
            "state": self.state,
            "free": self.free,
            "tags": self.tags,
        }


# ---------------------------------------------------------------------------
# Route (navigation path to a resource)
# ---------------------------------------------------------------------------

@dataclass
class Route:
    """
    A navigable path from a user need to a resource.

    Attributes
    ----------
    route_id : str
        Unique identifier.
    route_type : RouteType
        Type of route.
    resource : Resource
        Destination resource.
    steps : list[str]
        Turn-by-turn guidance steps.
    estimated_time : str
        Time estimate (e.g., "5 minutes online", "1-2 business days").
    big_bro_tip : str
        Big Bro's contextual coaching tip for this route.
    """

    route_id: str
    route_type: RouteType
    resource: Resource
    steps: list[str] = field(default_factory=list)
    estimated_time: str = ""
    big_bro_tip: str = ""

    def to_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "route_type": self.route_type.value,
            "resource": self.resource.to_dict(),
            "steps": self.steps,
            "estimated_time": self.estimated_time,
            "big_bro_tip": self.big_bro_tip,
        }


# ---------------------------------------------------------------------------
# Route & GPS Intelligence Engine
# ---------------------------------------------------------------------------

class RouteGPSError(Exception):
    """Raised when a routing operation fails."""


class RouteGPSIntelligence:
    """
    Routes users to services, opportunities, and franchises based on
    their needs, location, and eligibility.

    Parameters
    ----------
    default_city : str
        Default city context for routing.
    default_state : str
        Default state/province context.
    """

    def __init__(
        self,
        default_city: str = "",
        default_state: str = "",
    ) -> None:
        self.default_city = default_city
        self.default_state = default_state
        self._resources: dict[str, Resource] = {}
        self._routes: dict[str, Route] = {}
        self._resource_counter: int = 0
        self._route_counter: int = 0
        self._seed_resources()

    # ------------------------------------------------------------------
    # Seed national resources
    # ------------------------------------------------------------------

    def _seed_resources(self) -> None:
        """Pre-load a set of core national resources."""
        seeds = [
            {
                "name": "211 Helpline",
                "category": ResourceCategory.COMMUNITY,
                "description": (
                    "Free national helpline connecting people to local social services, "
                    "food, housing, healthcare, and employment resources."
                ),
                "eligibility": ["all"],
                "phone": "211",
                "url": "https://www.211.org",
                "free": True,
                "tags": ["social services", "emergency", "housing", "food"],
            },
            {
                "name": "SBA Small Business Resources",
                "category": ResourceCategory.BUSINESS,
                "description": "Free business planning tools, funding guidance, and mentorship.",
                "eligibility": ["entrepreneurs", "small business owners"],
                "url": "https://www.sba.gov",
                "free": True,
                "tags": ["business", "grants", "loans", "startup"],
            },
            {
                "name": "Coursera Free Courses",
                "category": ResourceCategory.EDUCATION,
                "description": "Free and paid online courses from top universities and companies.",
                "eligibility": ["all"],
                "url": "https://www.coursera.org",
                "free": False,
                "tags": ["education", "tech", "ai", "coding"],
            },
            {
                "name": "DreamCo Bot Marketplace",
                "category": ResourceCategory.TECHNOLOGY,
                "description": (
                    "Access DreamCo's full catalog of income-generating bots and "
                    "automation systems."
                ),
                "eligibility": ["all"],
                "url": "https://dreamco.ai",
                "free": False,
                "tags": ["bots", "automation", "income", "tech"],
            },
        ]
        for s in seeds:
            self._resource_counter += 1
            r_id = f"res_{self._resource_counter:04d}"
            resource = Resource(
                resource_id=r_id,
                name=s["name"],
                category=s["category"],
                description=s["description"],
                eligibility=s.get("eligibility", ["all"]),
                url=s.get("url", ""),
                phone=s.get("phone", ""),
                free=s.get("free", True),
                tags=s.get("tags", []),
            )
            self._resources[r_id] = resource

    # ------------------------------------------------------------------
    # Resource management
    # ------------------------------------------------------------------

    def add_resource(
        self,
        name: str,
        category: ResourceCategory,
        description: str,
        eligibility: Optional[list[str]] = None,
        url: str = "",
        phone: str = "",
        city: str = "",
        state: str = "",
        free: bool = True,
        tags: Optional[list[str]] = None,
    ) -> Resource:
        """Register a new resource."""
        self._resource_counter += 1
        r_id = f"res_{self._resource_counter:04d}"
        resource = Resource(
            resource_id=r_id,
            name=name,
            category=category,
            description=description,
            eligibility=eligibility or ["all"],
            url=url,
            phone=phone,
            city=city,
            state=state,
            free=free,
            tags=tags or [],
        )
        self._resources[r_id] = resource
        return resource

    def search_resources(
        self,
        category: Optional[ResourceCategory] = None,
        free_only: bool = False,
        tag: Optional[str] = None,
        city: Optional[str] = None,
    ) -> list[Resource]:
        """Find resources matching the given criteria."""
        results = list(self._resources.values())
        if category is not None:
            results = [r for r in results if r.category == category]
        if free_only:
            results = [r for r in results if r.free]
        if tag is not None:
            results = [r for r in results if tag in r.tags]
        if city is not None:
            results = [
                r for r in results if r.city.lower() == city.lower() or r.city == ""
            ]
        return results

    def resource_count(self) -> int:
        return len(self._resources)

    # ------------------------------------------------------------------
    # Route creation
    # ------------------------------------------------------------------

    def create_route(
        self,
        route_type: RouteType,
        resource_id: str,
        steps: Optional[list[str]] = None,
        estimated_time: str = "",
        big_bro_tip: str = "",
    ) -> Route:
        """Create a navigable route to a resource."""
        resource = self._resources.get(resource_id)
        if resource is None:
            raise RouteGPSError(f"No resource found with id '{resource_id}'.")
        self._route_counter += 1
        route_id = f"rte_{self._route_counter:04d}"
        route = Route(
            route_id=route_id,
            route_type=route_type,
            resource=resource,
            steps=steps or [],
            estimated_time=estimated_time,
            big_bro_tip=big_bro_tip,
        )
        self._routes[route_id] = route
        return route

    def navigate(self, need: str, city: Optional[str] = None) -> list[Route]:
        """
        Find relevant routes for a stated need.

        Performs keyword matching against resource names, descriptions,
        and tags to surface the most relevant guidance.
        """
        lower_need = need.lower()
        matching_resources = [
            r for r in self._resources.values()
            if (
                lower_need in r.name.lower()
                or lower_need in r.description.lower()
                or any(lower_need in t for t in r.tags)
            ) and (city is None or r.city == "" or r.city.lower() == city.lower())
        ]
        # Create on-the-fly routes for matching resources
        routes = []
        for resource in matching_resources:
            self._route_counter += 1
            route_id = f"rte_{self._route_counter:04d}"
            route = Route(
                route_id=route_id,
                route_type=RouteType.SERVICE,
                resource=resource,
                big_bro_tip=(
                    f"Big Bro tip: '{resource.name}' can help with '{need}'. "
                    "Start here and build from there."
                ),
            )
            routes.append(route)
        return routes

    # ------------------------------------------------------------------
    # GPS report
    # ------------------------------------------------------------------

    def gps_report(self) -> dict:
        """Return a summary of available resources and routes."""
        by_category: dict[str, int] = {}
        for r in self._resources.values():
            by_category[r.category.value] = by_category.get(r.category.value, 0) + 1
        return {
            "total_resources": len(self._resources),
            "total_routes": len(self._routes),
            "resources_by_category": by_category,
            "default_city": self.default_city,
            "default_state": self.default_state,
        }
