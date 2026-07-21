"""
DreamCo Family Resource & Survival GPS — 211 Bot.

A comprehensive, GPS-based resource tool that aggregates data from 211,
Feeding America, HUD, American Job Centers, and more to help families find
food pantries, shelters, job centers, legal aid, and other critical services.

Usage
-----
    from bot import ResourceBot, Tier, ResourceFilter, UserProfile

    bot = ResourceBot(tier=Tier.PRO)

    # Search for resources near a location
    results = bot.search_resources(lat=40.7128, lon=-74.0060, category="food")

    # Get a Building Intelligence Panel for a specific resource
    panel = bot.get_building_intel_panel(resource_id="r001")

    # AI-powered personalised plan
    profile = UserProfile(income_level="very_low", housing_status="homeless")
    plan = bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
"""

from __future__ import annotations

import math
import sys
import os

# ---------------------------------------------------------------------------
# Path setup — allow direct execution from the bot directory
# ---------------------------------------------------------------------------
_BOT_DIR = os.path.dirname(__file__)
sys.path.insert(0, _BOT_DIR)

from tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    RESOURCE_CATEGORIES,
    FEATURE_BUILDING_INTEL_PANELS,
    FEATURE_ADVANCED_FILTERING,
    FEATURE_ROUTE_PLANNING,
    FEATURE_RIDESHARE_COST_ESTIMATE,
    FEATURE_CROWD_REPORTING,
    FEATURE_SUPPLY_ALERTS,
    FEATURE_SAFETY_SCORE,
    FEATURE_AI_RESOURCE_MATCHING,
    FEATURE_REAL_TIME_DATA,
    FEATURE_FAMILY_GPS,
    FEATURE_PANIC_BUTTON,
    FEATURE_ARRIVAL_ALERTS,
    FEATURE_SPONSORED_LISTINGS,
    FEATURE_AFFILIATE_PROGRAMS,
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_INTEGRATIONS,
    FEATURE_ANALYTICS_DASHBOARD,
    DATA_SOURCE_211,
    DATA_SOURCE_FEEDING_AMERICA,
    DATA_SOURCE_HUD,
    DATA_SOURCE_AMERICAN_JOB_CENTERS,
    DATA_SOURCE_GOOGLE_MAPS,
)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ResourceBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class ResourceNotFoundError(Exception):
    """Raised when a requested resource cannot be found."""


class InvalidLocationError(Exception):
    """Raised when an invalid GPS coordinate is supplied."""


# ---------------------------------------------------------------------------
# Data classes (pure Python — no external dependencies required)
# ---------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class ResourceFilter:
    """Filters to apply when searching for resources.

    Attributes
    ----------
    open_now : bool
        Only return resources that are currently open.
    kid_friendly : bool
        Only return resources that are child-friendly.
    handicap_accessible : bool
        Only return ADA/wheelchair-accessible resources.
    spanish_speaking : bool
        Only return resources that offer Spanish-language services.
    max_distance_km : float | None
        Maximum distance in kilometres from the search origin.
    category : str | None
        Limit results to a specific resource category (see RESOURCE_CATEGORIES).
    """

    open_now: bool = False
    kid_friendly: bool = False
    handicap_accessible: bool = False
    spanish_speaking: bool = False
    max_distance_km: Optional[float] = None
    category: Optional[str] = None


@dataclass
class UserProfile:
    """User profile used for AI-powered resource matching.

    Attributes
    ----------
    income_level : str
        One of ``"very_low"``, ``"low"``, ``"moderate"``, ``"above_moderate"``.
    housing_status : str
        One of ``"housed"``, ``"at_risk"``, ``"homeless"``.
    household_size : int
        Number of people in the household.
    has_children : bool
        Whether the household includes children.
    has_disability : bool
        Whether any member has a disability.
    spanish_preferred : bool
        Whether the household prefers Spanish-language services.
    employed : bool
        Whether any adult in the household is employed.
    """

    income_level: str = "low"
    housing_status: str = "housed"
    household_size: int = 1
    has_children: bool = False
    has_disability: bool = False
    spanish_preferred: bool = False
    employed: bool = False


@dataclass
class Resource:
    """Represents a single community resource location.

    Attributes
    ----------
    resource_id : str
        Unique identifier for this resource.
    name : str
        Display name of the resource / organisation.
    category : str
        Resource category (e.g. ``"food"``, ``"shelter"``).
    address : str
        Street address.
    lat : float
        Latitude.
    lon : float
        Longitude.
    phone : str
        Contact phone number.
    website : str
        URL of the resource's website.
    hours : dict[str, str]
        Opening hours keyed by day abbreviation (``"Mon"``, ``"Tue"``, …).
    eligibility : list[str]
        Human-readable eligibility requirements.
    required_documents : list[str]
        Documents needed to access this resource.
    optimal_visit_times : list[str]
        Recommended times to visit (e.g. ``"Tuesday 9 AM – 11 AM"``).
    average_wait_minutes : int
        Typical wait time in minutes.
    instructions : str
        Step-by-step instructions for a first visit.
    video_walkthrough_url : str
        URL to an embedded video walkthrough.
    kid_friendly : bool
        Whether the resource is child-friendly.
    handicap_accessible : bool
        Whether the resource is ADA/wheelchair-accessible.
    spanish_speaking : bool
        Whether Spanish-language services are available.
    data_source : str
        Which data source this record originated from.
    sponsored : bool
        Whether this is a sponsored listing.
    supply_available : bool
        Whether supplies / capacity are currently available.
    current_crowd_level : str
        One of ``"low"``, ``"medium"``, ``"high"``.
    """

    resource_id: str
    name: str
    category: str
    address: str
    lat: float
    lon: float
    phone: str = ""
    website: str = ""
    hours: Dict[str, str] = field(default_factory=dict)
    eligibility: List[str] = field(default_factory=list)
    required_documents: List[str] = field(default_factory=list)
    optimal_visit_times: List[str] = field(default_factory=list)
    average_wait_minutes: int = 0
    instructions: str = ""
    video_walkthrough_url: str = ""
    kid_friendly: bool = False
    handicap_accessible: bool = False
    spanish_speaking: bool = False
    data_source: str = DATA_SOURCE_211
    sponsored: bool = False
    supply_available: bool = True
    current_crowd_level: str = "low"


@dataclass
class BuildingIntelPanel:
    """Rich information panel displayed alongside a resource on the GPS map.

    Attributes
    ----------
    resource : Resource
        The underlying resource record.
    type_label : str
        Human-friendly category label (e.g. ``"Food Pantry"``).
    eligibility_summary : str
        One-line eligibility summary.
    documents_needed : list[str]
        List of required documents.
    optimal_visit_times : list[str]
        Best times to visit.
    wait_time_label : str
        Human-readable wait time (e.g. ``"~15 minutes"``).
    success_instructions : str
        Tips for a successful visit.
    video_walkthrough_url : str
        Embedded video walkthrough URL.
    crowd_level : str
        Current crowd level (``"low"`` / ``"medium"`` / ``"high"``).
    supply_status : str
        ``"available"`` or ``"unavailable"``.
    safety_score : float | None
        Neighbourhood safety score 0–10 (None if unavailable on this tier).
    """

    resource: Resource
    type_label: str
    eligibility_summary: str
    documents_needed: List[str]
    optimal_visit_times: List[str]
    wait_time_label: str
    success_instructions: str
    video_walkthrough_url: str
    crowd_level: str
    supply_status: str
    safety_score: Optional[float]


@dataclass
class RouteInfo:
    """Driving / walking route information for a resource.

    Attributes
    ----------
    resource_id : str
        Target resource.
    distance_km : float
        Great-circle distance in kilometres.
    estimated_drive_minutes : int
        Estimated driving time.
    estimated_walk_minutes : int
        Estimated walking time.
    uber_estimate_usd : float | None
        Estimated Uber fare in USD (None if unavailable on this tier).
    lyft_estimate_usd : float | None
        Estimated Lyft fare in USD (None if unavailable on this tier).
    maps_url : str
        Deep-link to Google Maps directions.
    safe_route : bool
        Whether the route avoids low-safety areas (PRO/ENTERPRISE only).
    """

    resource_id: str
    distance_km: float
    estimated_drive_minutes: int
    estimated_walk_minutes: int
    uber_estimate_usd: Optional[float]
    lyft_estimate_usd: Optional[float]
    maps_url: str
    safe_route: bool


@dataclass
class ResourcePlan:
    """AI-generated personalised resource plan.

    Attributes
    ----------
    profile : UserProfile
        The user profile used to generate this plan.
    recommended_resources : list[Resource]
        Ordered list of recommended resources.
    priority_categories : list[str]
        Resource categories listed in priority order for this profile.
    summary : str
        Plain-English summary of the plan.
    financial_literacy_tips : list[str]
        Basic financial literacy suggestions (ETFs, Roth IRA, budgeting).
    """

    profile: UserProfile
    recommended_resources: List[Resource]
    priority_categories: List[str]
    summary: str
    financial_literacy_tips: List[str]


@dataclass
class FamilyAlert:
    """Safety alert dispatched by the family GPS module.

    Attributes
    ----------
    alert_type : str
        One of ``"arrival"``, ``"panic"``, ``"route_deviation"``.
    member_name : str
        Name of the family member.
    lat : float
        Current latitude.
    lon : float
        Current longitude.
    message : str
        Human-readable alert message.
    """

    alert_type: str
    member_name: str
    lat: float
    lon: float
    message: str


# ---------------------------------------------------------------------------
# Sample / stub resource database (simulates API / scraper results)
# ---------------------------------------------------------------------------

_SAMPLE_RESOURCES: List[Resource] = [
    Resource(
        resource_id="r001",
        name="City Food Pantry",
        category="food",
        address="123 Main St, Anytown, USA",
        lat=40.7128,
        lon=-74.0060,
        phone="(555) 000-0001",
        website="https://cityfoodpantry.example.org",
        hours={"Mon": "9am-5pm", "Wed": "9am-5pm", "Fri": "9am-3pm"},
        eligibility=["Residents of Anytown", "Income below 200% federal poverty line"],
        required_documents=["Photo ID", "Proof of address"],
        optimal_visit_times=["Tuesday 9 AM – 11 AM", "Thursday 2 PM – 4 PM"],
        average_wait_minutes=15,
        instructions=(
            "1. Arrive during open hours.\n"
            "2. Sign in at the front desk.\n"
            "3. Present your photo ID and proof of address.\n"
            "4. Wait to be called.\n"
            "5. Collect your food box."
        ),
        video_walkthrough_url="https://www.youtube.com/watch?v=example_food",
        kid_friendly=True,
        handicap_accessible=True,
        spanish_speaking=True,
        data_source=DATA_SOURCE_FEEDING_AMERICA,
        supply_available=True,
        current_crowd_level="low",
    ),
    Resource(
        resource_id="r002",
        name="Downtown Emergency Shelter",
        category="shelter",
        address="456 Oak Ave, Anytown, USA",
        lat=40.7200,
        lon=-74.0100,
        phone="(555) 000-0002",
        website="https://downtownshelter.example.org",
        hours={"Mon": "Open 24/7", "Tue": "Open 24/7", "Wed": "Open 24/7",
               "Thu": "Open 24/7", "Fri": "Open 24/7", "Sat": "Open 24/7",
               "Sun": "Open 24/7"},
        eligibility=["Individuals experiencing homelessness"],
        required_documents=["No documents required for emergency intake"],
        optimal_visit_times=["Arrive before 6 PM for best bed availability"],
        average_wait_minutes=30,
        instructions=(
            "1. Arrive at the front entrance.\n"
            "2. Speak with the intake coordinator.\n"
            "3. Complete a brief assessment form.\n"
            "4. You will be assigned a bed and shown the facilities."
        ),
        video_walkthrough_url="https://www.youtube.com/watch?v=example_shelter",
        kid_friendly=True,
        handicap_accessible=True,
        spanish_speaking=False,
        data_source=DATA_SOURCE_HUD,
        supply_available=True,
        current_crowd_level="medium",
    ),
    Resource(
        resource_id="r003",
        name="Workforce Development Center",
        category="job_assistance",
        address="789 Elm Blvd, Anytown, USA",
        lat=40.7050,
        lon=-74.0150,
        phone="(555) 000-0003",
        website="https://workforcedev.example.org",
        hours={"Mon": "8am-6pm", "Tue": "8am-6pm", "Wed": "8am-6pm",
               "Thu": "8am-6pm", "Fri": "8am-4pm"},
        eligibility=["Adults 18+", "Currently unemployed or underemployed"],
        required_documents=["Government-issued ID", "Social Security card",
                            "Proof of income (or unemployment confirmation)"],
        optimal_visit_times=["Monday morning for intake appointments",
                             "Walk-ins accepted Tue–Thu 10 AM – 2 PM"],
        average_wait_minutes=20,
        instructions=(
            "1. Visit the front desk for an initial skills assessment.\n"
            "2. Meet with a career counsellor.\n"
            "3. Enroll in training programs relevant to your goals.\n"
            "4. Utilise the job placement board and attend resume workshops."
        ),
        video_walkthrough_url="https://www.youtube.com/watch?v=example_jobs",
        kid_friendly=False,
        handicap_accessible=True,
        spanish_speaking=True,
        data_source=DATA_SOURCE_AMERICAN_JOB_CENTERS,
        supply_available=True,
        current_crowd_level="low",
    ),
    Resource(
        resource_id="r004",
        name="Community Legal Aid Society",
        category="legal_aid",
        address="321 Pine Rd, Anytown, USA",
        lat=40.7300,
        lon=-73.9900,
        phone="(555) 000-0004",
        website="https://legalaid.example.org",
        hours={"Mon": "9am-5pm", "Tue": "9am-5pm", "Wed": "9am-5pm",
               "Thu": "9am-5pm", "Fri": "9am-3pm"},
        eligibility=["Income below 125% federal poverty line",
                     "Residents of the county"],
        required_documents=["Photo ID", "Proof of income", "Case-related documents"],
        optimal_visit_times=["Call ahead for an appointment",
                             "Walk-in hours: Mon & Wed 9 AM – 11 AM"],
        average_wait_minutes=45,
        instructions=(
            "1. Call to schedule an appointment or arrive during walk-in hours.\n"
            "2. Bring all relevant case documents.\n"
            "3. Complete the intake form at the reception.\n"
            "4. Meet with a staff attorney for a free consultation."
        ),
        video_walkthrough_url="https://www.youtube.com/watch?v=example_legal",
        kid_friendly=False,
        handicap_accessible=True,
        spanish_speaking=False,
        data_source=DATA_SOURCE_211,
        supply_available=True,
        current_crowd_level="low",
    ),
    Resource(
        resource_id="r005",
        name="Warming Center at St. Mark's",
        category="shelter",
        address="555 Cedar Ln, Anytown, USA",
        lat=40.7180,
        lon=-74.0200,
        phone="(555) 000-0005",
        website="",
        hours={"Mon": "7pm-7am", "Tue": "7pm-7am", "Wed": "7pm-7am",
               "Thu": "7pm-7am", "Fri": "7pm-7am", "Sat": "7pm-7am",
               "Sun": "7pm-7am"},
        eligibility=["Anyone needing warmth – no requirements"],
        required_documents=[],
        optimal_visit_times=["Arrive by 8 PM for guaranteed access"],
        average_wait_minutes=10,
        instructions=(
            "1. Arrive after 7 PM at the side entrance.\n"
            "2. Sign in with a first name only.\n"
            "3. A cot and blanket will be provided."
        ),
        video_walkthrough_url="",
        kid_friendly=True,
        handicap_accessible=False,
        spanish_speaking=True,
        data_source=DATA_SOURCE_211,
        supply_available=True,
        current_crowd_level="high",
    ),
    Resource(
        resource_id="r006",
        name="Financial Literacy Hub",
        category="financial_literacy",
        address="100 Market St, Anytown, USA",
        lat=40.7090,
        lon=-74.0080,
        phone="(555) 000-0006",
        website="https://finlit.example.org",
        hours={"Mon": "10am-4pm", "Wed": "10am-4pm", "Sat": "9am-1pm"},
        eligibility=["Open to all community members"],
        required_documents=[],
        optimal_visit_times=["Saturday morning workshops – arrive 9 AM"],
        average_wait_minutes=5,
        instructions=(
            "1. Attend a free budgeting workshop.\n"
            "2. Learn about Roth IRAs, ETFs, and emergency funds.\n"
            "3. Sign up for one-on-one financial coaching."
        ),
        video_walkthrough_url="https://www.youtube.com/watch?v=example_finlit",
        kid_friendly=True,
        handicap_accessible=True,
        spanish_speaking=True,
        data_source=DATA_SOURCE_211,
        supply_available=True,
        current_crowd_level="low",
    ),
]

# ---------------------------------------------------------------------------
# Category label mapping
# ---------------------------------------------------------------------------

_CATEGORY_LABELS: Dict[str, str] = {
    "food": "Food Pantry / Food Bank",
    "shelter": "Shelter / Housing",
    "job_assistance": "Job Assistance / Workforce Development",
    "legal_aid": "Legal Aid",
    "financial_literacy": "Financial Literacy",
    "healthcare": "Healthcare / Medical",
    "childcare": "Childcare",
    "transportation": "Transportation Assistance",
    "clothing": "Clothing Closet",
    "mental_health": "Mental Health Services",
}

# ---------------------------------------------------------------------------
# Neighbourhood safety score stubs (keyed by resource_id)
# ---------------------------------------------------------------------------

_SAFETY_SCORES: Dict[str, float] = {
    "r001": 8.2,
    "r002": 6.5,
    "r003": 9.0,
    "r004": 8.7,
    "r005": 5.8,
    "r006": 8.5,
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in kilometres between two points."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return r * 2 * math.asin(math.sqrt(a))


def _validate_coordinates(lat: float, lon: float) -> None:
    if not (-90 <= lat <= 90):
        raise InvalidLocationError(f"Latitude {lat} is out of range [-90, 90].")
    if not (-180 <= lon <= 180):
        raise InvalidLocationError(f"Longitude {lon} is out of range [-180, 180].")


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------


class ResourceBot:
    """
    DreamCo Family Resource & Survival GPS — 211 Bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        # Internal resource registry — populated from data sources
        self._resources: List[Resource] = list(_SAMPLE_RESOURCES)
        # Family GPS member tracking (member_name → (lat, lon))
        self._family_members: Dict[str, tuple] = {}
        # Monetisation: registered affiliate organisations
        self._affiliates: List[str] = []

    # ------------------------------------------------------------------
    # Resource search
    # ------------------------------------------------------------------

    def search_resources(
        self,
        lat: float,
        lon: float,
        category: Optional[str] = None,
        filters: Optional[ResourceFilter] = None,
    ) -> List[Resource]:
        """
        Search for community resources near a GPS coordinate.

        Parameters
        ----------
        lat : float
            Latitude of the search origin.
        lon : float
            Longitude of the search origin.
        category : str | None
            Limit results to this resource category.
        filters : ResourceFilter | None
            Additional filters (advanced filtering requires PRO/ENTERPRISE).

        Returns
        -------
        List[Resource]
            Resources sorted by distance, respecting tier result limits.
        """
        _validate_coordinates(lat, lon)

        if filters is None:
            filters = ResourceFilter()

        # Advanced filtering is a PRO+ feature
        advanced_filter_active = (
            filters.open_now
            or filters.kid_friendly
            or filters.handicap_accessible
            or filters.spanish_speaking
            or filters.max_distance_km is not None
        )
        if advanced_filter_active:
            self._require_feature(FEATURE_ADVANCED_FILTERING)

        results: List[Resource] = []
        for resource in self._resources:
            # Category filter
            effective_category = category or (filters.category if filters else None)
            if effective_category and resource.category != effective_category:
                continue
            # Attribute filters
            if filters.kid_friendly and not resource.kid_friendly:
                continue
            if filters.handicap_accessible and not resource.handicap_accessible:
                continue
            if filters.spanish_speaking and not resource.spanish_speaking:
                continue
            # Distance filter
            dist = _haversine_km(lat, lon, resource.lat, resource.lon)
            if filters.max_distance_km is not None and dist > filters.max_distance_km:
                continue
            results.append(resource)

        # Sort by distance
        results.sort(key=lambda r: _haversine_km(lat, lon, r.lat, r.lon))

        # Apply tier result limit
        max_r = self.config.max_results
        if max_r is not None:
            results = results[:max_r]

        return results

    # ------------------------------------------------------------------
    # Building Intelligence Panel
    # ------------------------------------------------------------------

    def get_building_intel_panel(self, resource_id: str) -> BuildingIntelPanel:
        """
        Return a Building Intelligence Panel for a specific resource.

        This feature requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        resource_id : str
            ID of the resource to retrieve panel data for.

        Returns
        -------
        BuildingIntelPanel
        """
        self._require_feature(FEATURE_BUILDING_INTEL_PANELS)
        resource = self._get_resource_by_id(resource_id)

        wait_label = (
            f"~{resource.average_wait_minutes} minutes"
            if resource.average_wait_minutes > 0
            else "Minimal / no wait"
        )
        eligibility_summary = (
            resource.eligibility[0] if resource.eligibility else "Open to all"
        )
        safety_score: Optional[float] = None
        if self.config.has_feature(FEATURE_SAFETY_SCORE):
            safety_score = _SAFETY_SCORES.get(resource_id)

        return BuildingIntelPanel(
            resource=resource,
            type_label=_CATEGORY_LABELS.get(resource.category, resource.category),
            eligibility_summary=eligibility_summary,
            documents_needed=list(resource.required_documents),
            optimal_visit_times=list(resource.optimal_visit_times),
            wait_time_label=wait_label,
            success_instructions=resource.instructions,
            video_walkthrough_url=resource.video_walkthrough_url,
            crowd_level=resource.current_crowd_level,
            supply_status="available" if resource.supply_available else "unavailable",
            safety_score=safety_score,
        )

    # ------------------------------------------------------------------
    # Route planning
    # ------------------------------------------------------------------

    def get_route_info(
        self,
        origin_lat: float,
        origin_lon: float,
        resource_id: str,
    ) -> RouteInfo:
        """
        Return route planning information from an origin to a resource.

        Requires PRO or ENTERPRISE tier.  Rideshare cost estimates are
        computed from a simplified distance-based model.

        Parameters
        ----------
        origin_lat : float
            Latitude of the starting point.
        origin_lon : float
            Longitude of the starting point.
        resource_id : str
            ID of the destination resource.

        Returns
        -------
        RouteInfo
        """
        self._require_feature(FEATURE_ROUTE_PLANNING)
        _validate_coordinates(origin_lat, origin_lon)
        resource = self._get_resource_by_id(resource_id)

        dist_km = _haversine_km(origin_lat, origin_lon, resource.lat, resource.lon)
        drive_min = max(1, int(dist_km / 0.5))   # rough ~30 km/h urban speed
        walk_min = max(1, int(dist_km / 0.08))   # rough ~5 km/h walking speed

        uber_usd: Optional[float] = None
        lyft_usd: Optional[float] = None
        if self.config.has_feature(FEATURE_RIDESHARE_COST_ESTIMATE):
            base_fare = 2.50
            per_km = 1.25
            uber_usd = round(base_fare + dist_km * per_km, 2)
            lyft_usd = round((base_fare + dist_km * per_km) * 0.95, 2)

        maps_url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={origin_lat},{origin_lon}"
            f"&destination={resource.lat},{resource.lon}"
        )

        safe_route = self.config.has_feature(FEATURE_SAFETY_SCORE)

        return RouteInfo(
            resource_id=resource_id,
            distance_km=round(dist_km, 3),
            estimated_drive_minutes=drive_min,
            estimated_walk_minutes=walk_min,
            uber_estimate_usd=uber_usd,
            lyft_estimate_usd=lyft_usd,
            maps_url=maps_url,
            safe_route=safe_route,
        )

    # ------------------------------------------------------------------
    # Crowd reporting & supply alerts
    # ------------------------------------------------------------------

    def report_crowd_level(self, resource_id: str, level: str) -> None:
        """
        Submit a real-time crowd report for a resource.

        Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        resource_id : str
            Target resource.
        level : str
            One of ``"low"``, ``"medium"``, ``"high"``.
        """
        self._require_feature(FEATURE_CROWD_REPORTING)
        if level not in ("low", "medium", "high"):
            raise ValueError("level must be one of 'low', 'medium', 'high'.")
        resource = self._get_resource_by_id(resource_id)
        resource.current_crowd_level = level

    def report_supply_status(self, resource_id: str, available: bool) -> None:
        """
        Update the supply availability flag for a resource.

        Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        resource_id : str
            Target resource.
        available : bool
            ``True`` if supplies are currently available.
        """
        self._require_feature(FEATURE_SUPPLY_ALERTS)
        resource = self._get_resource_by_id(resource_id)
        resource.supply_available = available

    # ------------------------------------------------------------------
    # Neighbourhood safety score
    # ------------------------------------------------------------------

    def get_safety_score(self, resource_id: str) -> float:
        """
        Return the neighbourhood safety score for a resource location.

        Requires PRO or ENTERPRISE tier.

        Returns
        -------
        float
            Score in the range 0–10 (higher = safer).
        """
        self._require_feature(FEATURE_SAFETY_SCORE)
        self._get_resource_by_id(resource_id)  # validates ID
        return _SAFETY_SCORES.get(resource_id, 5.0)

    # ------------------------------------------------------------------
    # AI resource matching
    # ------------------------------------------------------------------

    def generate_resource_plan(
        self,
        profile: UserProfile,
        lat: float,
        lon: float,
    ) -> ResourcePlan:
        """
        Generate an AI-powered personalised resource plan.

        Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        profile : UserProfile
            User's demographic and situational profile.
        lat : float
            User's current latitude.
        lon : float
            User's current longitude.

        Returns
        -------
        ResourcePlan
        """
        self._require_feature(FEATURE_AI_RESOURCE_MATCHING)
        _validate_coordinates(lat, lon)

        # Determine priority categories from profile
        priorities: List[str] = []
        if profile.housing_status in ("homeless", "at_risk"):
            priorities.append("shelter")
        if profile.income_level in ("very_low", "low"):
            priorities.append("food")
        if not profile.employed:
            priorities.append("job_assistance")
        if profile.income_level in ("very_low", "low", "moderate"):
            priorities.append("financial_literacy")
        priorities.append("legal_aid")  # always useful

        # Gather nearby resources matching priority categories
        recommended: List[Resource] = []
        seen_ids: set = set()
        for cat in priorities:
            nearby = self.search_resources(lat, lon, category=cat)
            for r in nearby:
                if r.resource_id not in seen_ids:
                    recommended.append(r)
                    seen_ids.add(r.resource_id)

        # Financial literacy tips based on profile
        fin_tips: List[str] = []
        if profile.income_level in ("very_low", "low"):
            fin_tips.append("Start with a zero-based monthly budget to track every dollar.")
            fin_tips.append("Build a $500 emergency fund before investing.")
        if profile.income_level in ("low", "moderate", "above_moderate"):
            fin_tips.append(
                "Open a Roth IRA — contributions grow tax-free and can be "
                "withdrawn penalty-free after age 59½."
            )
            fin_tips.append(
                "Consider low-cost index ETFs (e.g., S&P 500 ETF) for long-term growth."
            )
        fin_tips.append("Avoid payday loans — seek credit-union alternatives instead.")

        # Build plain-English summary
        housing_phrase = {
            "homeless": "currently experiencing homelessness",
            "at_risk": "at risk of homelessness",
            "housed": "housed",
        }.get(profile.housing_status, profile.housing_status)
        summary = (
            f"Based on your profile ({housing_phrase}, "
            f"household of {profile.household_size}, "
            f"income level '{profile.income_level}'), "
            f"we recommend focusing on: {', '.join(priorities)}. "
            f"We found {len(recommended)} resource(s) near you."
        )

        return ResourcePlan(
            profile=profile,
            recommended_resources=recommended,
            priority_categories=priorities,
            summary=summary,
            financial_literacy_tips=fin_tips,
        )

    # ------------------------------------------------------------------
    # Family GPS & safety alerts
    # ------------------------------------------------------------------

    def register_family_member(self, name: str, lat: float, lon: float) -> None:
        """
        Register or update a family member's GPS location.

        Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        name : str
            Family member's name (used as identifier).
        lat : float
            Current latitude.
        lon : float
            Current longitude.
        """
        self._require_feature(FEATURE_FAMILY_GPS)
        _validate_coordinates(lat, lon)
        self._family_members[name] = (lat, lon)

    def get_family_locations(self) -> Dict[str, tuple]:
        """
        Return all registered family member locations.

        Requires PRO or ENTERPRISE tier.

        Returns
        -------
        dict[str, tuple[float, float]]
            Mapping of member name to (lat, lon).
        """
        self._require_feature(FEATURE_FAMILY_GPS)
        return dict(self._family_members)

    def send_panic_alert(self, member_name: str) -> FamilyAlert:
        """
        Dispatch a panic alert for a family member.

        Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        member_name : str
            Name of the family member triggering the panic button.

        Returns
        -------
        FamilyAlert
        """
        self._require_feature(FEATURE_PANIC_BUTTON)
        location = self._family_members.get(member_name, (0.0, 0.0))
        alert = FamilyAlert(
            alert_type="panic",
            member_name=member_name,
            lat=location[0],
            lon=location[1],
            message=(
                f"⚠️ PANIC ALERT: {member_name} needs immediate assistance at "
                f"({location[0]:.4f}, {location[1]:.4f}). "
                "Contact emergency services if needed."
            ),
        )
        return alert

    def send_arrival_alert(self, member_name: str, destination: str) -> FamilyAlert:
        """
        Dispatch an arrival alert when a family member reaches a destination.

        Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        member_name : str
            Name of the family member.
        destination : str
            Name of the destination.

        Returns
        -------
        FamilyAlert
        """
        self._require_feature(FEATURE_ARRIVAL_ALERTS)
        location = self._family_members.get(member_name, (0.0, 0.0))
        alert = FamilyAlert(
            alert_type="arrival",
            member_name=member_name,
            lat=location[0],
            lon=location[1],
            message=f"✅ {member_name} has arrived safely at {destination}.",
        )
        return alert

    # ------------------------------------------------------------------
    # Monetisation — sponsored listings & affiliates
    # ------------------------------------------------------------------

    def add_sponsored_resource(self, resource: Resource) -> None:
        """
        Add a sponsored resource listing.

        Requires ENTERPRISE tier.

        Parameters
        ----------
        resource : Resource
            The resource to add as a sponsored listing.
        """
        self._require_feature(FEATURE_SPONSORED_LISTINGS)
        resource.sponsored = True
        self._resources.append(resource)

    def register_affiliate(self, organisation_name: str) -> None:
        """
        Register a nonprofit or local business as an affiliate.

        Requires ENTERPRISE tier.

        Parameters
        ----------
        organisation_name : str
            Name of the affiliate organisation.
        """
        self._require_feature(FEATURE_AFFILIATE_PROGRAMS)
        if organisation_name not in self._affiliates:
            self._affiliates.append(organisation_name)

    def get_affiliates(self) -> List[str]:
        """
        Return the list of registered affiliate organisations.

        Requires ENTERPRISE tier.

        Returns
        -------
        list[str]
        """
        self._require_feature(FEATURE_AFFILIATE_PROGRAMS)
        return list(self._affiliates)

    # ------------------------------------------------------------------
    # Resource layers (homeless, job, financial literacy, safety)
    # ------------------------------------------------------------------

    def get_homeless_resources(self, lat: float, lon: float) -> List[Resource]:
        """
        Return a curated layer of homeless resources (shelters, warming centers).

        Parameters
        ----------
        lat : float
            Search origin latitude.
        lon : float
            Search origin longitude.

        Returns
        -------
        List[Resource]
        """
        _validate_coordinates(lat, lon)
        results: List[Resource] = []
        for r in self._resources:
            if r.category == "shelter":
                results.append(r)
        results.sort(key=lambda r: _haversine_km(lat, lon, r.lat, r.lon))
        max_r = self.config.max_results
        if max_r is not None:
            results = results[:max_r]
        return results

    def get_job_resources(self, lat: float, lon: float) -> List[Resource]:
        """
        Return a curated layer of job and workforce development resources.

        Parameters
        ----------
        lat : float
            Search origin latitude.
        lon : float
            Search origin longitude.

        Returns
        -------
        List[Resource]
        """
        _validate_coordinates(lat, lon)
        results = [r for r in self._resources if r.category == "job_assistance"]
        results.sort(key=lambda r: _haversine_km(lat, lon, r.lat, r.lon))
        max_r = self.config.max_results
        if max_r is not None:
            results = results[:max_r]
        return results

    def get_financial_literacy_resources(self, lat: float, lon: float) -> List[Resource]:
        """
        Return a curated layer of financial literacy resources.

        Parameters
        ----------
        lat : float
            Search origin latitude.
        lon : float
            Search origin longitude.

        Returns
        -------
        List[Resource]
        """
        _validate_coordinates(lat, lon)
        results = [r for r in self._resources if r.category == "financial_literacy"]
        results.sort(key=lambda r: _haversine_km(lat, lon, r.lat, r.lon))
        max_r = self.config.max_results
        if max_r is not None:
            results = results[:max_r]
        return results

    # ------------------------------------------------------------------
    # Custom resource management (data ingestion)
    # ------------------------------------------------------------------

    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource to the local database.

        This method simulates the result of data scraping, API ingestion, or
        manual data entry.

        Parameters
        ----------
        resource : Resource
            The resource to add.
        """
        self._resources.append(resource)

    def get_resource_by_id(self, resource_id: str) -> Resource:
        """
        Look up a resource by its unique ID (public wrapper).

        Parameters
        ----------
        resource_id : str
            The resource ID.

        Returns
        -------
        Resource

        Raises
        ------
        ResourceNotFoundError
            If no resource with the given ID exists.
        """
        return self._get_resource_by_id(resource_id)

    # ------------------------------------------------------------------
    # Tier / upgrade information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return and print a description of the current bot tier."""
        cfg = self.config
        limit = "Unlimited" if cfg.is_unlimited() else str(cfg.max_results)
        lines = [
            f"=== DreamCo 211 Bot — {cfg.name} Tier ===",
            f"Price  : ${cfg.price_usd_monthly:.2f}/month",
            f"Max GPS results: {limit} per query",
            f"Support: {cfg.support_level}",
            "",
            "Enabled features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        lines.append("")
        lines.append("Integrated data sources:")
        for src in cfg.data_sources:
            lines.append(f"  • {src}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Return and print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg

        current_feats = set(self.config.features)
        new_feats = [f for f in next_cfg.features if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features unlocked:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat.replace('_', ' ').title()}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing ResourceBot."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise ResourceBotTierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier. Please upgrade to access it."
            )

    def _get_resource_by_id(self, resource_id: str) -> Resource:
        for r in self._resources:
            if r.resource_id == resource_id:
                return r
        raise ResourceNotFoundError(
            f"No resource found with ID '{resource_id}'."
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("DreamCo Family Resource & Survival GPS — 211 Bot\n")

    for tier in Tier:
        bot = ResourceBot(tier=tier)
        bot.describe_tier()
        bot.show_upgrade_path()
        print()

    # Demo search
    demo_bot = ResourceBot(tier=Tier.PRO)
    results = demo_bot.search_resources(lat=40.7128, lon=-74.0060)
    print(f"Found {len(results)} resource(s) near (40.7128, -74.0060):")
    for r in results:
        print(f"  [{r.category}] {r.name} — {r.address}")

    # Demo Building Intelligence Panel
    panel = demo_bot.get_building_intel_panel("r001")
    print(f"\nBuilding Intel Panel — {panel.resource.name}:")
    print(f"  Type      : {panel.type_label}")
    print(f"  Eligibility: {panel.eligibility_summary}")
    print(f"  Wait time : {panel.wait_time_label}")
    print(f"  Crowd     : {panel.crowd_level}")
    print(f"  Safety score: {panel.safety_score}")

    # Demo route info
    route = demo_bot.get_route_info(40.7000, -74.0000, "r001")
    print(f"\nRoute to r001: {route.distance_km} km, "
          f"~{route.estimated_drive_minutes} min drive, "
          f"Uber ~${route.uber_estimate_usd}")
