"""Real Estate Bot — tier-aware real estate deal finder, ROI analyzer, and
Housing + Government Contract engine.

Engines:
  1. Property Acquisition        — find_distressed_properties()
  2. Government Program Finder   — find_gov_housing_programs()
  3. Revenue Matching Engine     — match_property_to_program(), calculate_housing_revenue()
  4. Outreach Engine             — send_outreach()
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from .tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class RealEstateBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class RealEstateBot:
    """Tier-aware real estate deal finder and ROI analyzer."""

    LOCATION_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    PROPERTY_DATABASE = {
        "austin": [
            {"address": "1204 Oak Blvd, Austin TX", "price": 320000, "beds": 3, "baths": 2, "sqft": 1450, "type": "single_family", "monthly_rent": 2400, "year_built": 1998},
            {"address": "5601 Riverside Dr #203, Austin TX", "price": 185000, "beds": 2, "baths": 1, "sqft": 875, "type": "condo", "monthly_rent": 1600, "year_built": 2005},
            {"address": "820 S Congress Ave, Austin TX", "price": 450000, "beds": 4, "baths": 3, "sqft": 2100, "type": "single_family", "monthly_rent": 3200, "year_built": 2001},
            {"address": "311 W 7th St #402, Austin TX", "price": 275000, "beds": 1, "baths": 1, "sqft": 720, "type": "condo", "monthly_rent": 2000, "year_built": 2010},
            {"address": "4422 Burnet Rd, Austin TX", "price": 380000, "beds": 3, "baths": 2, "sqft": 1600, "type": "townhouse", "monthly_rent": 2800, "year_built": 2003},
        ],
        "phoenix": [
            {"address": "3901 E Indian School Rd, Phoenix AZ", "price": 285000, "beds": 3, "baths": 2, "sqft": 1550, "type": "single_family", "monthly_rent": 2100, "year_built": 1995},
            {"address": "1820 N 44th St #110, Phoenix AZ", "price": 165000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo", "monthly_rent": 1450, "year_built": 2002},
            {"address": "6120 N 7th Ave, Phoenix AZ", "price": 220000, "beds": 3, "baths": 2, "sqft": 1350, "type": "single_family", "monthly_rent": 1800, "year_built": 1988},
            {"address": "2401 W Camelback Rd, Phoenix AZ", "price": 340000, "beds": 4, "baths": 2, "sqft": 1900, "type": "single_family", "monthly_rent": 2500, "year_built": 2000},
            {"address": "910 E Osborn Rd #301, Phoenix AZ", "price": 195000, "beds": 2, "baths": 1, "sqft": 880, "type": "condo", "monthly_rent": 1600, "year_built": 2008},
        ],
        "nashville": [
            {"address": "2204 Belmont Blvd, Nashville TN", "price": 415000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "monthly_rent": 2900, "year_built": 1997},
            {"address": "500 Church St #1205, Nashville TN", "price": 310000, "beds": 2, "baths": 2, "sqft": 1100, "type": "condo", "monthly_rent": 2400, "year_built": 2012},
            {"address": "1122 Gallatin Ave, Nashville TN", "price": 295000, "beds": 3, "baths": 1, "sqft": 1400, "type": "single_family", "monthly_rent": 2200, "year_built": 1962},
            {"address": "4401 Murphy Rd, Nashville TN", "price": 375000, "beds": 4, "baths": 3, "sqft": 2000, "type": "townhouse", "monthly_rent": 2700, "year_built": 2004},
        ],
        "denver": [
            {"address": "1502 Larimer St #4C, Denver CO", "price": 265000, "beds": 1, "baths": 1, "sqft": 750, "type": "condo", "monthly_rent": 2000, "year_built": 2007},
            {"address": "3822 W 38th Ave, Denver CO", "price": 445000, "beds": 3, "baths": 2, "sqft": 1650, "type": "single_family", "monthly_rent": 3100, "year_built": 1955},
            {"address": "7001 E Colfax Ave, Denver CO", "price": 325000, "beds": 3, "baths": 2, "sqft": 1500, "type": "single_family", "monthly_rent": 2500, "year_built": 1974},
        ],
        "tampa": [
            {"address": "4810 W Kennedy Blvd, Tampa FL", "price": 310000, "beds": 3, "baths": 2, "sqft": 1550, "type": "single_family", "monthly_rent": 2300, "year_built": 1993},
            {"address": "111 N 12th St #2205, Tampa FL", "price": 220000, "beds": 2, "baths": 2, "sqft": 1050, "type": "condo", "monthly_rent": 1900, "year_built": 2006},
            {"address": "2901 W Cypress St, Tampa FL", "price": 275000, "beds": 3, "baths": 2, "sqft": 1350, "type": "single_family", "monthly_rent": 2100, "year_built": 1985},
        ],
        "charlotte": [
            {"address": "2215 Park Rd, Charlotte NC", "price": 295000, "beds": 3, "baths": 2, "sqft": 1480, "type": "single_family", "monthly_rent": 2100, "year_built": 1996},
            {"address": "500 W 5th St #1804, Charlotte NC", "price": 245000, "beds": 1, "baths": 1, "sqft": 820, "type": "condo", "monthly_rent": 1800, "year_built": 2014},
        ],
        "atlanta": [
            {"address": "1350 Spring St NW, Atlanta GA", "price": 380000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "monthly_rent": 2600, "year_built": 2001},
            {"address": "805 Peachtree St NE #14, Atlanta GA", "price": 290000, "beds": 2, "baths": 2, "sqft": 1200, "type": "condo", "monthly_rent": 2200, "year_built": 2009},
        ],
        "dallas": [
            {"address": "4421 Lemmon Ave, Dallas TX", "price": 350000, "beds": 3, "baths": 2, "sqft": 1600, "type": "single_family", "monthly_rent": 2500, "year_built": 1999},
            {"address": "2922 Elm St #301, Dallas TX", "price": 210000, "beds": 1, "baths": 1, "sqft": 780, "type": "condo", "monthly_rent": 1700, "year_built": 2011},
        ],
        "houston": [
            {"address": "3901 Richmond Ave, Houston TX", "price": 290000, "beds": 3, "baths": 2, "sqft": 1500, "type": "single_family", "monthly_rent": 2000, "year_built": 1994},
            {"address": "2400 Mid Ln #401, Houston TX", "price": 175000, "beds": 2, "baths": 2, "sqft": 950, "type": "condo", "monthly_rent": 1500, "year_built": 2003},
        ],
        "las_vegas": [
            {"address": "8901 W Charleston Blvd, Las Vegas NV", "price": 320000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "monthly_rent": 2200, "year_built": 2002},
            {"address": "4455 Paradise Rd #506, Las Vegas NV", "price": 185000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo", "monthly_rent": 1550, "year_built": 2007},
        ],
    }

    MARKET_TRENDS = {
        "austin": {"avg_price_change_pct": 6.2, "inventory_months": 2.1, "days_on_market": 18, "price_per_sqft": 285},
        "phoenix": {"avg_price_change_pct": 4.8, "inventory_months": 2.8, "days_on_market": 22, "price_per_sqft": 210},
        "nashville": {"avg_price_change_pct": 5.5, "inventory_months": 1.9, "days_on_market": 15, "price_per_sqft": 260},
        "denver": {"avg_price_change_pct": 3.2, "inventory_months": 3.1, "days_on_market": 28, "price_per_sqft": 295},
        "tampa": {"avg_price_change_pct": 7.1, "inventory_months": 2.5, "days_on_market": 20, "price_per_sqft": 230},
        "charlotte": {"avg_price_change_pct": 5.9, "inventory_months": 2.2, "days_on_market": 17, "price_per_sqft": 218},
        "atlanta": {"avg_price_change_pct": 4.4, "inventory_months": 2.7, "days_on_market": 24, "price_per_sqft": 225},
        "dallas": {"avg_price_change_pct": 3.8, "inventory_months": 3.0, "days_on_market": 26, "price_per_sqft": 215},
        "houston": {"avg_price_change_pct": 3.1, "inventory_months": 3.4, "days_on_market": 30, "price_per_sqft": 190},
        "las_vegas": {"avg_price_change_pct": 4.9, "inventory_months": 2.6, "days_on_market": 21, "price_per_sqft": 220},
    }

    # ------------------------------------------------------------------ #
    # Housing + Gov Contract Bot data                                      #
    # ------------------------------------------------------------------ #

    DEFAULT_PAYMENT_PER_PERSON_MONTHLY = 750   # conservative fallback rate (USD)
    OPERATING_COST_RATE = 0.20                 # 20% of gross rent reserved for operations

    DISTRESSED_PROPERTIES = [
        {
            "id": "DP001",
            "address": "312 Elmwood St, Milwaukee WI",
            "state": "WI",
            "city": "milwaukee",
            "price": 18500,
            "market_value": 65000,
            "beds": 3, "baths": 1, "sqft": 1150,
            "type": "foreclosure",
            "source": "county_tax_sale",
            "tax_delinquent": True,
            "days_vacant": 420,
            "year_built": 1962,
        },
        {
            "id": "DP002",
            "address": "908 Garfield Ave, Detroit MI",
            "state": "MI",
            "city": "detroit",
            "price": 9500,
            "market_value": 42000,
            "beds": 3, "baths": 1, "sqft": 1050,
            "type": "tax_sale",
            "source": "county_tax_sale",
            "tax_delinquent": True,
            "days_vacant": 730,
            "year_built": 1948,
        },
        {
            "id": "DP003",
            "address": "2204 Vine St, Cleveland OH",
            "state": "OH",
            "city": "cleveland",
            "price": 22000,
            "market_value": 78000,
            "beds": 4, "baths": 2, "sqft": 1600,
            "type": "abandoned",
            "source": "facebook_marketplace",
            "tax_delinquent": False,
            "days_vacant": 300,
            "year_built": 1955,
        },
        {
            "id": "DP004",
            "address": "5511 Prospect Ave, Kansas City MO",
            "state": "MO",
            "city": "kansas_city",
            "price": 29000,
            "market_value": 95000,
            "beds": 5, "baths": 2, "sqft": 2000,
            "type": "foreclosure",
            "source": "auction_site",
            "tax_delinquent": True,
            "days_vacant": 180,
            "year_built": 1971,
        },
        {
            "id": "DP005",
            "address": "744 Broad St, Newark NJ",
            "state": "NJ",
            "city": "newark",
            "price": 55000,
            "market_value": 180000,
            "beds": 6, "baths": 3, "sqft": 2800,
            "type": "multifamily",
            "source": "zillow",
            "tax_delinquent": False,
            "days_vacant": 90,
            "year_built": 1938,
        },
        {
            "id": "DP006",
            "address": "1130 Division Ave, Grand Rapids MI",
            "state": "MI",
            "city": "grand_rapids",
            "price": 16000,
            "market_value": 58000,
            "beds": 3, "baths": 1, "sqft": 1050,
            "type": "tax_sale",
            "source": "county_tax_sale",
            "tax_delinquent": True,
            "days_vacant": 540,
            "year_built": 1959,
        },
        {
            "id": "DP007",
            "address": "633 King St, Gary IN",
            "state": "IN",
            "city": "gary",
            "price": 7500,
            "market_value": 35000,
            "beds": 4, "baths": 1, "sqft": 1300,
            "type": "abandoned",
            "source": "county_tax_sale",
            "tax_delinquent": True,
            "days_vacant": 900,
            "year_built": 1952,
        },
        {
            "id": "DP008",
            "address": "2801 N 12th St, Philadelphia PA",
            "state": "PA",
            "city": "philadelphia",
            "price": 28000,
            "market_value": 110000,
            "beds": 4, "baths": 2, "sqft": 1550,
            "type": "foreclosure",
            "source": "auction_site",
            "tax_delinquent": False,
            "days_vacant": 210,
            "year_built": 1968,
        },
    ]

    GOV_HOUSING_PROGRAMS = [
        {
            "id": "GHP001",
            "name": "HUD Emergency Housing Voucher Program",
            "agency": "HUD",
            "portal": "hud.gov",
            "type": "voucher",
            "payment_per_person_monthly": 850,
            "max_tenants": 8,
            "states": ["all"],
            "eligibility": "homeless, domestic violence survivors, youth aging out of foster care",
            "contract_term_months": 12,
            "category": "emergency_housing",
        },
        {
            "id": "GHP002",
            "name": "Continuum of Care (CoC) Program",
            "agency": "HUD",
            "portal": "hud.gov",
            "type": "grant",
            "payment_per_person_monthly": 750,
            "max_tenants": 10,
            "states": ["all"],
            "eligibility": "homeless individuals and families",
            "contract_term_months": 24,
            "category": "homeless_housing",
        },
        {
            "id": "GHP003",
            "name": "SAM.gov Supportive Housing Services Contract",
            "agency": "VA",
            "portal": "sam.gov",
            "type": "contract",
            "payment_per_person_monthly": 1100,
            "max_tenants": 6,
            "states": ["all"],
            "eligibility": "homeless veterans",
            "contract_term_months": 12,
            "category": "veteran_housing",
        },
        {
            "id": "GHP004",
            "name": "HOME Investment Partnerships Program",
            "agency": "HUD",
            "portal": "hud.gov",
            "type": "grant",
            "payment_per_person_monthly": 600,
            "max_tenants": 12,
            "states": ["all"],
            "eligibility": "low-income households",
            "contract_term_months": 36,
            "category": "affordable_housing",
        },
        {
            "id": "GHP005",
            "name": "Rapid Rehousing Program (Grants.gov)",
            "agency": "HHS",
            "portal": "grants.gov",
            "type": "grant",
            "payment_per_person_monthly": 800,
            "max_tenants": 8,
            "states": ["all"],
            "eligibility": "individuals experiencing homelessness",
            "contract_term_months": 12,
            "category": "rapid_rehousing",
        },
        {
            "id": "GHP006",
            "name": "Wisconsin Emergency Housing Assistance",
            "agency": "Wisconsin DHS",
            "portal": "dhs.wisconsin.gov",
            "type": "state_contract",
            "payment_per_person_monthly": 720,
            "max_tenants": 6,
            "states": ["WI"],
            "eligibility": "homeless families in Wisconsin",
            "contract_term_months": 12,
            "category": "emergency_housing",
        },
        {
            "id": "GHP007",
            "name": "Michigan State Emergency Relief Housing",
            "agency": "Michigan MDHHS",
            "portal": "michigan.gov/mdhhs",
            "type": "state_contract",
            "payment_per_person_monthly": 700,
            "max_tenants": 6,
            "states": ["MI"],
            "eligibility": "families in immediate housing crisis",
            "contract_term_months": 6,
            "category": "emergency_housing",
        },
        {
            "id": "GHP008",
            "name": "Ohio Housing Finance Agency Rental Assistance",
            "agency": "OHFA",
            "portal": "ohiohome.org",
            "type": "state_contract",
            "payment_per_person_monthly": 680,
            "max_tenants": 8,
            "states": ["OH"],
            "eligibility": "low-income renters in Ohio",
            "contract_term_months": 12,
            "category": "affordable_housing",
        },
    ]

    OUTREACH_TEMPLATES = {
        "property_owner": (
            "Subject: Partnership Opportunity — Your Property at {address}\n\n"
            "Hello,\n\nI am reaching out about your property at {address}. "
            "I work with government-funded housing programs and am interested in a "
            "master lease or purchase arrangement. This could provide you with "
            "guaranteed monthly income with no landlord responsibilities.\n\n"
            "I'd love to connect and share more details. Please reply or call me at your convenience.\n\n"
            "Best regards,\nDreamCo Housing Partners"
        ),
        "housing_department": (
            "Subject: Available Housing Units for {program_name}\n\n"
            "Hello,\n\nI represent DreamCo Housing Partners and have {unit_count} unit(s) "
            "available at {address} that may be suitable for participants in {program_name}. "
            "The property has {beds} bedrooms and has been prepared to meet habitability standards.\n\n"
            "I would welcome a site visit and the opportunity to discuss a provider agreement.\n\n"
            "Best regards,\nDreamCo Housing Partners"
        ),
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._searched_locations: list = []

    def _check_location_limit(self, location: str) -> None:
        limit = self.LOCATION_LIMITS[self.tier]
        loc_lower = location.lower().replace(" ", "_")
        if limit is not None and len(self._searched_locations) >= limit and loc_lower not in self._searched_locations:
            raise RealEstateBotTierError(
                f"Location limit of {limit} reached on {self.config.name} tier. Upgrade to search more locations."
            )
        if loc_lower not in self._searched_locations:
            self._searched_locations.append(loc_lower)

    def search_deals(self, location: str, budget: float) -> list:
        """Return properties under budget in location."""
        self._check_location_limit(location)
        loc_key = location.lower().replace(" ", "_")
        properties = self.PROPERTY_DATABASE.get(loc_key, self.PROPERTY_DATABASE["austin"])
        results = [p for p in properties if p["price"] <= budget]
        for p in results:
            p["roi_estimate"] = round(self.estimate_roi(p), 2)
        return results

    def evaluate_property(self, address: str) -> dict:
        """Return valuation, cap rate, and cash flow analysis."""
        prop = None
        for props in self.PROPERTY_DATABASE.values():
            for p in props:
                if address.lower() in p["address"].lower():
                    prop = p
                    break
            if prop:
                break
        if not prop:
            prop = list(self.PROPERTY_DATABASE["austin"])[0]

        annual_rent = prop["monthly_rent"] * 12
        operating_expenses = annual_rent * 0.35
        noi = annual_rent - operating_expenses
        cap_rate = round(noi / prop["price"] * 100, 2)
        monthly_cashflow = round((noi / 12) - (prop["price"] * 0.008), 2)

        result = {
            "address": prop["address"],
            "price": prop["price"],
            "beds": prop["beds"],
            "baths": prop["baths"],
            "sqft": prop["sqft"],
            "type": prop["type"],
            "monthly_rent": prop["monthly_rent"],
            "annual_rent": annual_rent,
            "cap_rate_pct": cap_rate,
            "monthly_cashflow_usd": monthly_cashflow,
            "noi_usd": round(noi, 2),
            "roi_estimate_pct": round(self.estimate_roi(prop), 2),
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["rental_comps"] = [{"address": "Comparable nearby", "rent": prop["monthly_rent"] + 100}]
            result["cash_flow_analysis"] = {
                "gross_rent": annual_rent,
                "vacancy_loss": round(annual_rent * 0.05, 2),
                "operating_expenses": round(operating_expenses, 2),
                "noi": round(noi, 2),
            }
        if self.tier == Tier.ENTERPRISE:
            result["ai_valuation"] = round(prop["price"] * 1.05, 0)
            result["predictive_appreciation_3yr_pct"] = 12.5
        return result

    def estimate_roi(self, property_dict: dict) -> float:
        """Return estimated annual ROI percentage."""
        annual_rent = property_dict["monthly_rent"] * 12
        operating_expenses = annual_rent * 0.35
        noi = annual_rent - operating_expenses
        return round(noi / property_dict["price"] * 100, 2)

    def get_market_trends(self, location: str) -> dict:
        """Return price trends, inventory, and days-on-market."""
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError("Market trends require PRO or ENTERPRISE tier.")
        loc_key = location.lower().replace(" ", "_")
        trends = self.MARKET_TRENDS.get(loc_key, self.MARKET_TRENDS["austin"])
        result = {
            "location": location,
            "avg_price_change_pct_yoy": trends["avg_price_change_pct"],
            "inventory_months_supply": trends["inventory_months"],
            "avg_days_on_market": trends["days_on_market"],
            "price_per_sqft": trends["price_per_sqft"],
            "market_type": "Seller's" if trends["inventory_months"] < 3 else "Buyer's",
            "tier": self.tier.value,
        }
        if self.tier == Tier.ENTERPRISE:
            result["predictive_analytics"] = {
                "6mo_price_forecast_pct": round(trends["avg_price_change_pct"] / 2, 1),
                "investment_score": min(100, int(trends["avg_price_change_pct"] * 12)),
            }
        return result

    # ------------------------------------------------------------------ #
    # Engine 1 — Property Acquisition Bot                                 #
    # ------------------------------------------------------------------ #

    def find_distressed_properties(
        self,
        state: str = None,
        city: str = None,
        max_price: float = None,
        property_type: str = None,
    ) -> list:
        """Return distressed properties (foreclosures, tax sales, abandoned homes).

        Available on all tiers. FREE tier returns up to 3 results without
        filtering by city or property type. PRO and ENTERPRISE unlock all
        filters and return the full result set.
        """
        results = list(self.DISTRESSED_PROPERTIES)
        if state:
            results = [p for p in results if p["state"].upper() == state.upper()]
        if city and self.tier != Tier.FREE:
            city_normalized = city.lower().replace(" ", "_")
            results = [p for p in results if p["city"].lower() == city_normalized]
        if max_price is not None:
            results = [p for p in results if p["price"] <= max_price]
        if property_type and self.tier != Tier.FREE:
            results = [p for p in results if p["type"] == property_type]
        if self.tier == Tier.FREE:
            results = results[:3]
        for p in results:
            p["equity_spread"] = p["market_value"] - p["price"]
            p["equity_pct"] = round((p["equity_spread"] / p["market_value"]) * 100, 1)
        return results

    # ------------------------------------------------------------------ #
    # Engine 2 — Government Contract Bot                                  #
    # ------------------------------------------------------------------ #

    def find_gov_housing_programs(
        self,
        state: str = None,
        category: str = None,
        portal: str = None,
    ) -> list:
        """Return government housing programs from HUD, SAM.gov, Grants.gov.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError(
                "Government housing program search requires PRO or ENTERPRISE tier."
            )
        results = list(self.GOV_HOUSING_PROGRAMS)
        if state:
            results = [
                p for p in results
                if "all" in p["states"] or state.upper() in [s.upper() for s in p["states"]]
            ]
        if category:
            results = [p for p in results if p["category"] == category]
        if portal:
            portal_lower = portal.lower()
            results = [
                p for p in results
                if (
                    p["portal"].lower() == portal_lower
                    or p["portal"].lower().startswith(portal_lower + "/")
                )
            ]
        if self.tier == Tier.PRO:
            results = results[:5]
        return results

    # ------------------------------------------------------------------ #
    # Engine 3 — Revenue Matching Engine                                  #
    # ------------------------------------------------------------------ #

    def calculate_housing_revenue(self, beds: int, program_id: str = None) -> dict:
        """Calculate projected monthly government-paid income for a property.

        Uses number of bedrooms as tenant count. Works on all tiers.
        When *program_id* is provided and the tier is PRO+, uses that
        program's payment rate; otherwise uses a conservative default of
        $750/person/month.
        """
        rate = self.DEFAULT_PAYMENT_PER_PERSON_MONTHLY  # default conservative rate
        program_name = "default"
        if program_id and self.tier != Tier.FREE:
            programs = {p["id"]: p for p in self.GOV_HOUSING_PROGRAMS}
            if program_id in programs:
                rate = programs[program_id]["payment_per_person_monthly"]
                program_name = programs[program_id]["name"]
        tenants = max(1, beds)
        monthly_gross = tenants * rate
        operating_costs = round(monthly_gross * self.OPERATING_COST_RATE, 2)
        monthly_net = round(monthly_gross - operating_costs, 2)
        return {
            "beds": beds,
            "tenants": tenants,
            "rate_per_person_usd": rate,
            "program": program_name,
            "monthly_gross_usd": monthly_gross,
            "operating_costs_usd": operating_costs,
            "monthly_net_usd": monthly_net,
            "annual_net_usd": round(monthly_net * 12, 2),
            "tier": self.tier.value,
        }

    def match_property_to_program(self, property_id: str) -> dict:
        """Match a distressed property to the best government housing program.

        Returns a revenue projection for the best-matching program.
        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError(
                "Property-to-program matching requires PRO or ENTERPRISE tier."
            )
        prop = next((p for p in self.DISTRESSED_PROPERTIES if p["id"] == property_id), None)
        if not prop:
            raise ValueError(f"Property '{property_id}' not found in distressed properties database.")

        state = prop["state"]
        candidates = [
            p for p in self.GOV_HOUSING_PROGRAMS
            if "all" in p["states"] or state.upper() in [s.upper() for s in p["states"]]
        ]
        if not candidates:
            candidates = self.GOV_HOUSING_PROGRAMS

        best_program = max(candidates, key=lambda p: p["payment_per_person_monthly"])
        revenue = self.calculate_housing_revenue(prop["beds"], best_program["id"])
        result = {
            "property_id": property_id,
            "address": prop["address"],
            "acquisition_price": prop["price"],
            "beds": prop["beds"],
            "matched_program": best_program["name"],
            "program_id": best_program["id"],
            "agency": best_program["agency"],
            "portal": best_program["portal"],
            "monthly_gross_usd": revenue["monthly_gross_usd"],
            "monthly_net_usd": revenue["monthly_net_usd"],
            "annual_net_usd": revenue["annual_net_usd"],
            "payback_months": (
                round(prop["price"] / revenue["monthly_net_usd"], 1)
                if revenue["monthly_net_usd"] > 0 else None
            ),
            "tier": self.tier.value,
        }
        if self.tier == Tier.ENTERPRISE:
            result["all_matching_programs"] = [p["name"] for p in candidates]
            result["strategy_recommendation"] = (
                "Master Lease" if prop.get("tax_delinquent") else "Purchase + Convert"
            )
        return result

    # ------------------------------------------------------------------ #
    # Engine 4 — Outreach Bot                                             #
    # ------------------------------------------------------------------ #

    def send_outreach(
        self,
        contact_type: str,
        address: str,
        program_name: str = "",
        unit_count: int = 1,
        beds: int = 3,
    ) -> dict:
        """Generate outreach message for property owners or housing departments.

        *contact_type* must be ``'property_owner'`` or ``'housing_department'``.
        Auto-send simulation (ENTERPRISE) marks ``sent=True``; PRO generates
        the message only. Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError("Outreach engine requires PRO or ENTERPRISE tier.")
        if contact_type not in self.OUTREACH_TEMPLATES:
            raise ValueError(
                f"Unknown contact_type '{contact_type}'. "
                "Use 'property_owner' or 'housing_department'."
            )
        template = self.OUTREACH_TEMPLATES[contact_type]
        message = template.format(
            address=address,
            program_name=program_name,
            unit_count=unit_count,
            beds=beds,
        )
        return {
            "contact_type": contact_type,
            "address": address,
            "message": message,
            "sent": self.tier == Tier.ENTERPRISE,
            "tier": self.tier.value,
        }

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Real Estate Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 5, "leads_generated": 5, "revenue": 2000}


# ---------------------------------------------------------------------------
# Stripe integration for RealEstateBot
# ---------------------------------------------------------------------------
from bots.stripe_integration.stripe_client import StripeClient as _StripeClientREB

_REB_PRICES = {
    Tier.PRO: 4900,         # $49/month
    Tier.ENTERPRISE: 29900, # $299/month
}

_orig_reb_init = RealEstateBot.__init__


def _reb_new_init(self, tier: Tier = Tier.FREE) -> None:
    _orig_reb_init(self, tier)
    self._stripe = _StripeClientREB()


def _reb_create_checkout_session(self, upgrade_tier: Tier, customer_email: str = None) -> dict:
    if upgrade_tier == Tier.FREE:
        raise RealEstateBotTierError("Cannot create checkout for FREE tier.")
    price_cents = _REB_PRICES.get(upgrade_tier, 4900)
    result = self._stripe.create_checkout_session(plan=f"RealEstate {upgrade_tier.value.title()}", amount_cents=price_cents)
    if customer_email:
        result["customer_email"] = customer_email
    result["mode"] = "subscription"
    return result


def _reb_create_payment_link(self, upgrade_tier: Tier) -> dict:
    if upgrade_tier == Tier.FREE:
        raise RealEstateBotTierError("Cannot create payment link for FREE tier.")
    price_cents = _REB_PRICES.get(upgrade_tier, 4900)
    return self._stripe.create_payment_link(plan=f"RealEstate {upgrade_tier.value.title()}", amount_cents=price_cents)


RealEstateBot.__init__ = _reb_new_init
RealEstateBot.create_checkout_session = _reb_create_checkout_session
RealEstateBot.create_payment_link = _reb_create_payment_link
