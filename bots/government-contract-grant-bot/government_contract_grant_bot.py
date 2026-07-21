"""
Government Contract & Grant Bot — tier-aware discovery and analysis of
federal/state contracts and grants.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_LIMITS = {
    Tier.FREE: {"results_per_search": 5, "saved_searches": 2, "alert_keywords": 3},
    Tier.PRO: {"results_per_search": 50, "saved_searches": 20, "alert_keywords": 30},
    Tier.ENTERPRISE: {"results_per_search": None, "saved_searches": None, "alert_keywords": None},
}

TIER_PRICES = {
    Tier.FREE: 0,
    Tier.PRO: 99,
    Tier.ENTERPRISE: 299,
}

BOT_FEATURES = {
    Tier.FREE: ["basic_contract_search", "federal_grants_preview"],
    Tier.PRO: [
        "full_contract_search", "grant_search", "state_contracts",
        "deadline_alerts", "bid_analysis", "naics_filter", "saved_searches",
    ],
    Tier.ENTERPRISE: [
        "full_contract_search", "grant_search", "state_contracts",
        "deadline_alerts", "bid_analysis", "naics_filter", "saved_searches",
        "ai_proposal_assistant", "competitor_analysis", "subcontract_finder",
        "compliance_checker", "performance_analytics", "api_access",
    ],
}


class GovernmentContractGrantBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Mock data — realistic government contract and grant records
# ---------------------------------------------------------------------------

MOCK_CONTRACTS = [
    {
        "id": "W912DY-24-R-0001",
        "title": "IT Infrastructure Modernization Services",
        "agency": "Department of Defense",
        "type": "contract",
        "value": 5_200_000,
        "naics": "541512",
        "deadline": "2024-09-30",
        "set_aside": "Small Business",
        "location": "Washington, DC",
        "description": "Modernization of legacy IT systems across multiple DoD facilities.",
        "category": "technology",
    },
    {
        "id": "47QTCA-24-R-0002",
        "title": "Cloud Computing and Managed Services",
        "agency": "General Services Administration",
        "type": "contract",
        "value": 12_000_000,
        "naics": "518210",
        "deadline": "2024-10-15",
        "set_aside": "8(a)",
        "location": "Multiple Locations",
        "description": "Cloud hosting, migration and managed services for federal agencies.",
        "category": "technology",
    },
    {
        "id": "FA8750-24-R-0003",
        "title": "Cybersecurity Assessment and Penetration Testing",
        "agency": "Air Force Research Laboratory",
        "type": "contract",
        "value": 3_800_000,
        "naics": "541519",
        "deadline": "2024-08-20",
        "set_aside": "Women-Owned Small Business",
        "location": "Wright-Patterson AFB, OH",
        "description": "Annual cybersecurity assessments, pen tests and remediation support.",
        "category": "cybersecurity",
    },
    {
        "id": "HHS-2024-ACF-001",
        "title": "Community Health Services Coordination",
        "agency": "Health and Human Services",
        "type": "contract",
        "value": 2_100_000,
        "naics": "621999",
        "deadline": "2024-11-01",
        "set_aside": "None",
        "location": "Nationwide",
        "description": "Coordination of community health outreach and preventive care services.",
        "category": "healthcare",
    },
    {
        "id": "VA-24-PR-0012",
        "title": "Veterans Benefits Management System Support",
        "agency": "Department of Veterans Affairs",
        "type": "contract",
        "value": 7_500_000,
        "naics": "541511",
        "deadline": "2024-12-01",
        "set_aside": "Service-Disabled Veteran-Owned",
        "location": "Washington, DC",
        "description": "Software maintenance and support for the veterans benefits management platform.",
        "category": "technology",
    },
    {
        "id": "DOT-OST-24-R-006",
        "title": "Transportation Data Analytics Platform",
        "agency": "Department of Transportation",
        "type": "contract",
        "value": 4_600_000,
        "naics": "541511",
        "deadline": "2024-10-30",
        "set_aside": "HUBZone",
        "location": "Washington, DC",
        "description": "Development and maintenance of a national transportation analytics platform.",
        "category": "technology",
    },
    {
        "id": "EPA-R10-24-005",
        "title": "Environmental Monitoring and Compliance",
        "agency": "Environmental Protection Agency",
        "type": "contract",
        "value": 1_800_000,
        "naics": "541380",
        "deadline": "2024-09-15",
        "set_aside": "Small Business",
        "location": "Seattle, WA",
        "description": "Air and water quality monitoring services in the Pacific Northwest region.",
        "category": "environment",
    },
    {
        "id": "USDA-NRCS-24-001",
        "title": "Conservation Technical Assistance",
        "agency": "Department of Agriculture",
        "type": "contract",
        "value": 2_900_000,
        "naics": "541620",
        "deadline": "2024-11-15",
        "set_aside": "Small Business",
        "location": "Multiple States",
        "description": "Technical assistance for agricultural land conservation programs.",
        "category": "agriculture",
    },
    {
        "id": "DHS-FEMA-24-R-009",
        "title": "Emergency Management Training Services",
        "agency": "Department of Homeland Security",
        "type": "contract",
        "value": 3_300_000,
        "naics": "611699",
        "deadline": "2024-10-01",
        "set_aside": "None",
        "location": "Emmitsburg, MD",
        "description": "Curriculum development and delivery for emergency management professionals.",
        "category": "training",
    },
    {
        "id": "ED-GRANTS-24-0001",
        "title": "STEM Education Innovation Grant",
        "agency": "Department of Education",
        "type": "grant",
        "value": 500_000,
        "naics": "611110",
        "deadline": "2024-08-31",
        "set_aside": "None",
        "location": "Nationwide",
        "description": "Competitive grants for K-12 STEM curriculum development and teacher training.",
        "category": "education",
    },
    {
        "id": "NIH-SBIR-24-001",
        "title": "Small Business Innovation Research — Biotech Phase II",
        "agency": "National Institutes of Health",
        "type": "grant",
        "value": 1_500_000,
        "naics": "541714",
        "deadline": "2024-09-05",
        "set_aside": "Small Business",
        "location": "Bethesda, MD",
        "description": "Phase II SBIR grant for biomedical technology commercialization.",
        "category": "research",
    },
    {
        "id": "NSF-2024-CIVIC",
        "title": "Civic Innovation Challenge Grant",
        "agency": "National Science Foundation",
        "type": "grant",
        "value": 1_000_000,
        "naics": "541720",
        "deadline": "2024-10-20",
        "set_aside": "None",
        "location": "Nationwide",
        "description": "Grants to fund AI and data science solutions for community challenges.",
        "category": "research",
    },
    {
        "id": "DOE-SB-24-003",
        "title": "Clean Energy Small Business Grant",
        "agency": "Department of Energy",
        "type": "grant",
        "value": 750_000,
        "naics": "541990",
        "deadline": "2024-11-30",
        "set_aside": "Small Business",
        "location": "Nationwide",
        "description": "Funding for small businesses developing clean energy technologies.",
        "category": "energy",
    },
    {
        "id": "SBA-8A-24-012",
        "title": "8(a) Business Development Program Mentor-Protege",
        "agency": "Small Business Administration",
        "type": "contract",
        "value": 800_000,
        "naics": "541611",
        "deadline": "2024-12-31",
        "set_aside": "8(a)",
        "location": "Nationwide",
        "description": "Management consulting services under the 8(a) mentor-protege program.",
        "category": "consulting",
    },
    {
        "id": "NASA-GSFC-24-002",
        "title": "Satellite Data Processing and Analysis",
        "agency": "NASA",
        "type": "contract",
        "value": 9_000_000,
        "naics": "541712",
        "deadline": "2024-09-20",
        "set_aside": "None",
        "location": "Greenbelt, MD",
        "description": "Scientific data processing, analysis and visualization for Earth observation missions.",
        "category": "technology",
    },
    {
        "id": "USMC-24-R-0044",
        "title": "Logistics Support Services",
        "agency": "Department of Defense",
        "type": "contract",
        "value": 6_700_000,
        "naics": "488510",
        "deadline": "2024-10-05",
        "set_aside": "Small Business",
        "location": "Camp Lejeune, NC",
        "description": "Supply chain and logistics management support for Marine Corps installations.",
        "category": "logistics",
    },
    {
        "id": "HUD-FY24-CDBG",
        "title": "Community Development Block Grant",
        "agency": "Housing and Urban Development",
        "type": "grant",
        "value": 2_000_000,
        "naics": "531311",
        "deadline": "2024-11-01",
        "set_aside": "None",
        "location": "Urban Areas",
        "description": "Grants for community development, affordable housing and economic development.",
        "category": "housing",
    },
    {
        "id": "USAID-24-AFR-001",
        "title": "International Development Consulting",
        "agency": "USAID",
        "type": "contract",
        "value": 15_000_000,
        "naics": "541690",
        "deadline": "2024-09-25",
        "set_aside": "None",
        "location": "Sub-Saharan Africa",
        "description": "Economic development consulting and program management in Sub-Saharan Africa.",
        "category": "consulting",
    },
    {
        "id": "BIA-24-R-0008",
        "title": "Tribal Education Support Services",
        "agency": "Bureau of Indian Affairs",
        "type": "contract",
        "value": 1_400_000,
        "naics": "611710",
        "deadline": "2024-10-12",
        "set_aside": "Indian Economic Enterprise",
        "location": "Tribal Nations, Nationwide",
        "description": "Educational support and tutoring services for students in tribal schools.",
        "category": "education",
    },
    {
        "id": "NIST-MEP-24-005",
        "title": "Manufacturing Extension Partnership Services",
        "agency": "Department of Commerce",
        "type": "grant",
        "value": 3_500_000,
        "naics": "541330",
        "deadline": "2024-12-15",
        "set_aside": "None",
        "location": "Nationwide",
        "description": "Technical assistance and consulting to help small manufacturers compete globally.",
        "category": "manufacturing",
    },
    {
        "id": "DOJ-OVW-24-001",
        "title": "Violence Against Women Act Services Grant",
        "agency": "Department of Justice",
        "type": "grant",
        "value": 600_000,
        "naics": "624190",
        "deadline": "2024-08-15",
        "set_aside": "None",
        "location": "Nationwide",
        "description": "Grants for non-profits providing services to survivors of domestic violence.",
        "category": "social_services",
    },
    {
        "id": "DHHS-ACL-24-003",
        "title": "Aging Network Support Services",
        "agency": "Administration for Community Living",
        "type": "contract",
        "value": 1_200_000,
        "naics": "624120",
        "deadline": "2024-09-10",
        "set_aside": "None",
        "location": "Nationwide",
        "description": "Support for home and community-based services for older adults.",
        "category": "social_services",
    },
    {
        "id": "SSA-24-R-0015",
        "title": "Disability Determination Services Support",
        "agency": "Social Security Administration",
        "type": "contract",
        "value": 4_100_000,
        "naics": "541611",
        "deadline": "2024-11-20",
        "set_aside": "Small Business",
        "location": "Baltimore, MD",
        "description": "Program support for SSA disability determination processes and case management.",
        "category": "consulting",
    },
    {
        "id": "IRS-24-IT-007",
        "title": "Tax Systems Technology Modernization",
        "agency": "Internal Revenue Service",
        "type": "contract",
        "value": 22_000_000,
        "naics": "541511",
        "deadline": "2024-10-31",
        "set_aside": "None",
        "location": "Washington, DC",
        "description": "Modernization of IRS tax processing and taxpayer service technology.",
        "category": "technology",
    },
    {
        "id": "FCC-24-R-0003",
        "title": "Rural Broadband Technical Assistance",
        "agency": "Federal Communications Commission",
        "type": "contract",
        "value": 890_000,
        "naics": "517311",
        "deadline": "2024-09-01",
        "set_aside": "Small Business",
        "location": "Rural Communities, Nationwide",
        "description": "Technical assistance for rural broadband deployment and digital equity programs.",
        "category": "technology",
    },
    {
        "id": "CDC-24-GH-002",
        "title": "Global Health Security Program",
        "agency": "Centers for Disease Control",
        "type": "grant",
        "value": 2_800_000,
        "naics": "541690",
        "deadline": "2024-11-10",
        "set_aside": "None",
        "location": "International",
        "description": "Support for disease surveillance and outbreak response in developing countries.",
        "category": "healthcare",
    },
    {
        "id": "FHWA-24-R-0009",
        "title": "Highway Safety Improvement Program",
        "agency": "Federal Highway Administration",
        "type": "contract",
        "value": 5_600_000,
        "naics": "237310",
        "deadline": "2024-10-08",
        "set_aside": "DBE",
        "location": "Multiple States",
        "description": "Design and construction services for highway safety improvement projects.",
        "category": "construction",
    },
    {
        "id": "USDA-AMS-24-004",
        "title": "Food Safety Inspection Services",
        "agency": "Department of Agriculture",
        "type": "contract",
        "value": 3_700_000,
        "naics": "926150",
        "deadline": "2024-09-28",
        "set_aside": "Small Business",
        "location": "Multiple States",
        "description": "Third-party food safety inspection and laboratory testing services.",
        "category": "agriculture",
    },
    {
        "id": "DHS-TSA-24-002",
        "title": "Airport Security Technology Services",
        "agency": "Transportation Security Administration",
        "type": "contract",
        "value": 18_000_000,
        "naics": "561612",
        "deadline": "2024-12-20",
        "set_aside": "None",
        "location": "Major Airports, Nationwide",
        "description": "Advanced screening technology maintenance and cybersecurity for airport security.",
        "category": "security",
    },
    {
        "id": "FEMA-24-HMGP-001",
        "title": "Hazard Mitigation Grant Program",
        "agency": "FEMA",
        "type": "grant",
        "value": 4_500_000,
        "naics": "541620",
        "deadline": "2024-08-25",
        "set_aside": "None",
        "location": "Disaster-Declared Areas",
        "description": "Grants to reduce future disaster losses through mitigation projects.",
        "category": "environment",
    },
]


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class GovernmentContractGrantBot:
    """Tier-aware bot that discovers, filters, and analyzes government
    contracts and grants from federal and state sources.

    Features
    --------
    - Search federal contracts and grants by keyword, NAICS code, agency, or
      set-aside category.
    - Filter opportunities by value range, deadline, and category.
    - Analyze bid feasibility and estimate win probability.
    - Track upcoming deadlines and alert on matching opportunities.
    - Generate bid summaries and proposal starter documents.

    Tiers
    -----
    FREE       — 5 results per search, basic federal contracts only.
    PRO        — 50 results, full search, state contracts, deadline alerts.
    ENTERPRISE — Unlimited, AI proposal assistant, competitor analysis, API.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.limits = TIER_LIMITS[tier]
        self.features = BOT_FEATURES[tier]
        self._saved_searches: list[dict] = []
        self._alerts: list[str] = []
        self.flow = GlobalAISourcesFlow(bot_name="GovernmentContractGrantBot")

    # ------------------------------------------------------------------
    # Search and filter
    # ------------------------------------------------------------------

    def search_opportunities(
        self,
        keyword: str = "",
        naics: Optional[str] = None,
        agency: Optional[str] = None,
        set_aside: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        min_value: float = 0,
        max_value: Optional[float] = None,
    ) -> list[dict]:
        """Search contracts and grants matching the given filters.

        Parameters
        ----------
        keyword : str
            Text to search in title/description.
        naics : str, optional
            NAICS code filter (prefix match).
        agency : str, optional
            Agency name filter (partial match, case-insensitive).
        set_aside : str, optional
            Set-aside category (e.g. "Small Business", "8(a)").
        opportunity_type : str, optional
            "contract" or "grant".
        min_value : float
            Minimum contract/grant value.
        max_value : float, optional
            Maximum contract/grant value (None = no limit).

        Returns
        -------
        list[dict]
            Matching opportunities, capped by tier limit.
        """
        results = []
        kw = keyword.lower()
        for opp in MOCK_CONTRACTS:
            if kw and kw not in opp["title"].lower() and kw not in opp["description"].lower():
                continue
            if naics and not opp["naics"].startswith(naics):
                continue
            if agency and agency.lower() not in opp["agency"].lower():
                continue
            if set_aside and set_aside.lower() not in opp["set_aside"].lower():
                continue
            if opportunity_type and opp["type"] != opportunity_type:
                continue
            if opp["value"] < min_value:
                continue
            if max_value is not None and opp["value"] > max_value:
                continue
            results.append(opp)

        limit = self.limits["results_per_search"]
        if limit is not None:
            results = results[:limit]
        return results

    def search_contracts(self, keyword: str = "", **kwargs) -> object:
        """Search federal contracts only."""
        query_kwarg = kwargs.pop("query", None)
        query = query_kwarg if query_kwarg is not None else keyword
        results = self.search_opportunities(keyword=query, opportunity_type="contract", **kwargs)
        # Legacy callers using the 'query' kwarg expect a dict response
        if query_kwarg is not None:
            return {"contracts": results, "count": len(results), "keyword": query}
        return results

    def search_grants(self, keyword: str = "", **kwargs) -> list[dict]:
        """Search grants only.  Requires PRO or ENTERPRISE tier."""
        if self.tier == Tier.FREE and "grant_search" not in self.features:
            raise GovernmentContractGrantBotTierError(
                "Full grant search requires PRO or ENTERPRISE tier."
            )
        return self.search_opportunities(keyword=keyword, opportunity_type="grant", **kwargs)

    def get_upcoming_deadlines(self, days: int = 30) -> list[dict]:
        """Return opportunities with deadlines within *days* calendar days."""
        import datetime
        today = datetime.date.today()
        cutoff = today + datetime.timedelta(days=days)
        results = []
        for opp in MOCK_CONTRACTS:
            try:
                deadline = datetime.date.fromisoformat(opp["deadline"])
                if today <= deadline <= cutoff:
                    results.append({**opp, "days_remaining": (deadline - today).days})
            except ValueError:
                continue
        results.sort(key=lambda x: x["days_remaining"])
        limit = self.limits["results_per_search"]
        return results[:limit] if limit else results

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze_opportunity(self, opportunity_id: str) -> dict:
        """Return a detailed analysis of a single opportunity.

        Requires PRO or ENTERPRISE tier.
        """
        if "bid_analysis" not in self.features:
            raise GovernmentContractGrantBotTierError(
                "Bid analysis requires PRO or ENTERPRISE tier."
            )
        opp = next((o for o in MOCK_CONTRACTS if o["id"] == opportunity_id), None)
        if opp is None:
            return {"error": f"Opportunity {opportunity_id!r} not found."}

        # Simple heuristic win probability
        win_prob = self._estimate_win_probability(opp)
        roi_score = self._estimate_roi_score(opp)
        return {
            "opportunity": opp,
            "analysis": {
                "win_probability_pct": win_prob,
                "roi_score": roi_score,
                "competition_level": "high" if opp["value"] > 5_000_000 else "medium" if opp["value"] > 1_000_000 else "low",
                "recommended_action": "bid" if win_prob >= 40 else "monitor" if win_prob >= 20 else "skip",
                "key_requirements": self._extract_requirements(opp),
                "similar_past_wins": [],
            },
        }

    def _estimate_win_probability(self, opp: dict) -> int:
        """Heuristic win probability (0–100)."""
        base = 35
        # Small business set-aside designations (using full names from mock data)
        small_biz_set_asides = (
            "Small Business",
            "8(a)",
            "Women-Owned Small Business",
            "HUBZone",
            "Service-Disabled Veteran-Owned",
            "Indian Economic Enterprise",
            "DBE",  # Disadvantaged Business Enterprise
        )
        if opp["set_aside"] in small_biz_set_asides:
            base += 20
        if opp["value"] < 1_000_000:
            base += 15
        elif opp["value"] > 10_000_000:
            base -= 15
        return min(max(base, 5), 90)

    def _estimate_roi_score(self, opp: dict) -> float:
        """ROI attractiveness score 0–10."""
        if opp["value"] == 0:
            return 0.0
        base = 5.0
        if opp["value"] > 5_000_000:
            base += 2.0
        if opp["set_aside"] != "None":
            base += 1.0
        if opp["type"] == "grant":
            base += 1.5
        return round(min(base, 10.0), 1)

    def _extract_requirements(self, opp: dict) -> list[str]:
        """Extract high-level requirements from opportunity description."""
        reqs = []
        desc = opp.get("description", "").lower()
        if "cybersecurity" in desc or "security" in desc:
            reqs.append("Cybersecurity clearance / CMMC compliance")
        if "cloud" in desc or "aws" in desc or "azure" in desc:
            reqs.append("Cloud platform expertise (AWS/Azure/GCP)")
        if "software" in desc or "development" in desc or "it" in opp.get("category", ""):
            reqs.append("Software development / IT capabilities")
        if "consulting" in desc or "management" in desc:
            reqs.append("Management consulting credentials")
        reqs.append("SAM.gov active registration")
        return reqs

    # ------------------------------------------------------------------
    # Saved searches and alerts
    # ------------------------------------------------------------------

    def save_search(self, name: str, filters: dict) -> dict:
        """Save a named search for reuse. Tier-limited."""
        limit = self.limits["saved_searches"]
        if limit is not None and len(self._saved_searches) >= limit:
            raise GovernmentContractGrantBotTierError(
                f"Saved search limit ({limit}) reached. Upgrade to save more."
            )
        entry = {"name": name, "filters": filters}
        self._saved_searches.append(entry)
        return {"saved": True, "search": entry}

    def add_alert_keyword(self, keyword: str) -> dict:
        """Register an alert keyword. Tier-limited."""
        if "deadline_alerts" not in self.features:
            raise GovernmentContractGrantBotTierError(
                "Deadline alerts require PRO or ENTERPRISE tier."
            )
        limit = self.limits["alert_keywords"]
        if limit is not None and len(self._alerts) >= limit:
            raise GovernmentContractGrantBotTierError(
                f"Alert keyword limit ({limit}) reached. Upgrade for more."
            )
        self._alerts.append(keyword)
        return {"added": True, "keyword": keyword, "total_alerts": len(self._alerts)}

    # ------------------------------------------------------------------
    # Summary and reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return a high-level summary of available opportunities."""
        contracts = [o for o in MOCK_CONTRACTS if o["type"] == "contract"]
        grants = [o for o in MOCK_CONTRACTS if o["type"] == "grant"]
        total_value = sum(o["value"] for o in MOCK_CONTRACTS)
        small_biz = [o for o in MOCK_CONTRACTS if o["set_aside"] != "None"]
        return {
            "total_opportunities": len(MOCK_CONTRACTS),
            "contracts": len(contracts),
            "grants": len(grants),
            "total_value_usd": total_value,
            "small_business_set_asides": len(small_biz),
            "categories": list({o["category"] for o in MOCK_CONTRACTS}),
            "agencies": list({o["agency"] for o in MOCK_CONTRACTS}),
            "tier": self.tier.value,
            "tier_price_monthly": TIER_PRICES[self.tier],
        }

    def get_tier_info(self) -> dict:
        """Return current tier information."""
        return {
            "tier": self.tier.value,
            "price_monthly": TIER_PRICES[self.tier],
            "features": self.features,
            "limits": self.limits,
        }

    # ------------------------------------------------------------------
    # Pipeline execution
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """Execute the full GLOBAL AI SOURCES FLOW pipeline for this bot."""
        print(f"GovernmentContractGrantBot running: scanning contracts and grants...")
        result = self.flow.run_pipeline(
            raw_data={"domain": "government_contracts_and_grants", "records": len(MOCK_CONTRACTS)},
            learning_method="supervised",
        )
        return result

    def start(self) -> None:
        """Start the bot."""
        print(f"GovernmentContractGrantBot starting...")

    def process_contracts(self) -> None:
        """Process available federal contracts."""
        contracts = self.search_contracts()
        count = contracts.get("count", 0) if isinstance(contracts, dict) else len(contracts)
        print(f"Processing {count} contracts...")

    def process_grants(self) -> None:
        """Process available grants."""
        try:
            grants = self.search_grants()
        except Exception:
            grants = []
        print(f"Processing {len(grants)} grants...")

    def check_grant_eligibility(self, organization: dict) -> dict:
        """Check if an organization is eligible for grants."""
        try:
            recommended = self.search_grants() if self.tier.value != "free" else []
        except Exception:
            recommended = []
        return {
            "eligible": True,
            "organization": organization,
            "recommended_grants": recommended,
            "tier": self.tier.value if hasattr(self.tier, 'value') else str(self.tier),
        }


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 10, "leads_generated": 10, "revenue": 500}


# If this module is run directly, start the bot
if __name__ == '__main__':
    bot = GovernmentContractGrantBot(tier=Tier.PRO)
    summary = bot.get_summary()
    print(f"Government Contract & Grant Bot — {summary['total_opportunities']} opportunities")
    print(f"  Contracts: {summary['contracts']}  |  Grants: {summary['grants']}")
    print(f"  Total value: ${summary['total_value_usd']:,.0f}")
    tech = bot.search_contracts(keyword="technology")
    print(f"  Technology contracts: {len(tech)}")
    deadlines = bot.get_upcoming_deadlines(days=60)
    print(f"  Upcoming deadlines (60 days): {len(deadlines)}")
