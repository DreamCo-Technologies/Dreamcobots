"""Foreclosure Finder Bot — tier-aware foreclosure search, risk assessment, and auction tracking."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.foreclosure_finder_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class ForeclosureFinderBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class ForeclosureFinderBot:
    """Tier-aware foreclosure finder: search, risk assessment, and auction calendar."""

    COUNTY_LIMITS = {Tier.FREE: 1, Tier.PRO: 5, Tier.ENTERPRISE: None}
    RESULTS_LIMITS = {Tier.FREE: 5, Tier.PRO: 25, Tier.ENTERPRISE: None}

    # ~20 foreclosure listings across various counties
    FORECLOSURE_DATABASE = [
        {
            "id": "FC001",
            "address": "1812 Westfield Ave, Cook County IL",
            "county": "cook",
            "state": "IL",
            "status": "pre_foreclosure",
            "listing_price": 98000,
            "market_value": 148000,
            "beds": 3, "baths": 1, "sqft": 1200,
            "year_built": 1955,
            "days_delinquent": 180,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 2,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC002",
            "address": "4420 Broad St, Maricopa County AZ",
            "county": "maricopa",
            "state": "AZ",
            "status": "auction",
            "listing_price": 165000,
            "market_value": 225000,
            "beds": 3, "baths": 2, "sqft": 1450,
            "year_built": 1992,
            "days_delinquent": 365,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": "2025-09-15",
            "bank": None,
        },
        {
            "id": "FC003",
            "address": "803 Pinecrest Rd, Harris County TX",
            "county": "harris",
            "state": "TX",
            "status": "reo",
            "listing_price": 87000,
            "market_value": 142000,
            "beds": 3, "baths": 2, "sqft": 1350,
            "year_built": 1978,
            "days_delinquent": 540,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 3,
            "auction_date": None,
            "bank": "Wells Fargo",
        },
        {
            "id": "FC004",
            "address": "217 Lakeview Dr, Wayne County MI",
            "county": "wayne",
            "state": "MI",
            "status": "pre_foreclosure",
            "listing_price": 42000,
            "market_value": 78000,
            "beds": 3, "baths": 1, "sqft": 1100,
            "year_built": 1948,
            "days_delinquent": 120,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 4,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC005",
            "address": "5501 Orange Blossom Ln, Hillsborough County FL",
            "county": "hillsborough",
            "state": "FL",
            "status": "auction",
            "listing_price": 192000,
            "market_value": 275000,
            "beds": 4, "baths": 2, "sqft": 1850,
            "year_built": 1995,
            "days_delinquent": 420,
            "tax_delinquent": False,
            "hoa_delinquent": True,
            "liens_count": 2,
            "auction_date": "2025-09-22",
            "bank": None,
        },
        {
            "id": "FC006",
            "address": "6640 Rosewood Blvd, Mecklenburg County NC",
            "county": "mecklenburg",
            "state": "NC",
            "status": "reo",
            "listing_price": 128000,
            "market_value": 195000,
            "beds": 3, "baths": 2, "sqft": 1500,
            "year_built": 1982,
            "days_delinquent": 600,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": None,
            "bank": "Chase",
        },
        {
            "id": "FC007",
            "address": "388 Hickory Hollow Rd, Cuyahoga County OH",
            "county": "cuyahoga",
            "state": "OH",
            "status": "pre_foreclosure",
            "listing_price": 51000,
            "market_value": 92000,
            "beds": 3, "baths": 1, "sqft": 1150,
            "year_built": 1960,
            "days_delinquent": 90,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 2,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC008",
            "address": "1901 Sundown Dr, Clark County NV",
            "county": "clark",
            "state": "NV",
            "status": "auction",
            "listing_price": 148000,
            "market_value": 215000,
            "beds": 3, "baths": 2, "sqft": 1600,
            "year_built": 2001,
            "days_delinquent": 330,
            "tax_delinquent": False,
            "hoa_delinquent": True,
            "liens_count": 2,
            "auction_date": "2025-10-05",
            "bank": None,
        },
        {
            "id": "FC009",
            "address": "742 Maple Grove Ln, Fulton County GA",
            "county": "fulton",
            "state": "GA",
            "status": "reo",
            "listing_price": 112000,
            "market_value": 178000,
            "beds": 3, "baths": 2, "sqft": 1400,
            "year_built": 1975,
            "days_delinquent": 480,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 3,
            "auction_date": None,
            "bank": "Bank of America",
        },
        {
            "id": "FC010",
            "address": "2214 Creek Side Ct, Davidson County TN",
            "county": "davidson",
            "state": "TN",
            "status": "pre_foreclosure",
            "listing_price": 185000,
            "market_value": 265000,
            "beds": 3, "baths": 2, "sqft": 1700,
            "year_built": 1988,
            "days_delinquent": 150,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC011",
            "address": "9012 Prairie Wind Dr, Dallas County TX",
            "county": "dallas",
            "state": "TX",
            "status": "auction",
            "listing_price": 118000,
            "market_value": 182000,
            "beds": 3, "baths": 2, "sqft": 1450,
            "year_built": 1980,
            "days_delinquent": 390,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 2,
            "auction_date": "2025-09-30",
            "bank": None,
        },
        {
            "id": "FC012",
            "address": "3318 Bridgewater Ct, Marion County IN",
            "county": "marion",
            "state": "IN",
            "status": "reo",
            "listing_price": 58000,
            "market_value": 105000,
            "beds": 3, "baths": 1, "sqft": 1100,
            "year_built": 1962,
            "days_delinquent": 720,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 5,
            "auction_date": None,
            "bank": "Citibank",
        },
        {
            "id": "FC013",
            "address": "4500 Harvest Moon Blvd, Bexar County TX",
            "county": "bexar",
            "state": "TX",
            "status": "pre_foreclosure",
            "listing_price": 78000,
            "market_value": 135000,
            "beds": 3, "baths": 1, "sqft": 1250,
            "year_built": 1968,
            "days_delinquent": 200,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 2,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC014",
            "address": "7720 Fern Valley Rd, Jefferson County KY",
            "county": "jefferson",
            "state": "KY",
            "status": "auction",
            "listing_price": 72000,
            "market_value": 118000,
            "beds": 3, "baths": 1, "sqft": 1200,
            "year_built": 1957,
            "days_delinquent": 300,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": "2025-10-12",
            "bank": None,
        },
        {
            "id": "FC015",
            "address": "1140 Valley Brook Dr, Sacramento County CA",
            "county": "sacramento",
            "state": "CA",
            "status": "reo",
            "listing_price": 215000,
            "market_value": 345000,
            "beds": 3, "baths": 2, "sqft": 1500,
            "year_built": 1978,
            "days_delinquent": 540,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": None,
            "bank": "US Bank",
        },
        {
            "id": "FC016",
            "address": "2880 Cottonwood Ave, Denver County CO",
            "county": "denver",
            "state": "CO",
            "status": "pre_foreclosure",
            "listing_price": 245000,
            "market_value": 375000,
            "beds": 3, "baths": 2, "sqft": 1650,
            "year_built": 1975,
            "days_delinquent": 95,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC017",
            "address": "508 Dogwood Circle, Wake County NC",
            "county": "wake",
            "state": "NC",
            "status": "auction",
            "listing_price": 155000,
            "market_value": 238000,
            "beds": 3, "baths": 2, "sqft": 1600,
            "year_built": 1990,
            "days_delinquent": 450,
            "tax_delinquent": True,
            "hoa_delinquent": True,
            "liens_count": 3,
            "auction_date": "2025-10-20",
            "bank": None,
        },
        {
            "id": "FC018",
            "address": "3201 Magnolia St, East Baton Rouge Parish LA",
            "county": "east_baton_rouge",
            "state": "LA",
            "status": "reo",
            "listing_price": 62000,
            "market_value": 108000,
            "beds": 3, "baths": 1, "sqft": 1150,
            "year_built": 1958,
            "days_delinquent": 680,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 4,
            "auction_date": None,
            "bank": "PNC Bank",
        },
        {
            "id": "FC019",
            "address": "6601 Elmwood Ave, King County WA",
            "county": "king",
            "state": "WA",
            "status": "pre_foreclosure",
            "listing_price": 385000,
            "market_value": 525000,
            "beds": 3, "baths": 2, "sqft": 1800,
            "year_built": 1985,
            "days_delinquent": 130,
            "tax_delinquent": False,
            "hoa_delinquent": False,
            "liens_count": 1,
            "auction_date": None,
            "bank": None,
        },
        {
            "id": "FC020",
            "address": "4415 Birch Run Rd, Hamilton County OH",
            "county": "hamilton",
            "state": "OH",
            "status": "auction",
            "listing_price": 68000,
            "market_value": 115000,
            "beds": 3, "baths": 1, "sqft": 1250,
            "year_built": 1953,
            "days_delinquent": 360,
            "tax_delinquent": True,
            "hoa_delinquent": False,
            "liens_count": 2,
            "auction_date": "2025-11-03",
            "bank": None,
        },
    ]

    # Cost constants for lien payoff estimation
    _COST_PER_LIEN_USD = 8500
    _TAX_DELINQUENCY_COST_USD = 12000
    # Cost constants for title clearance estimation
    _TITLE_CLEARANCE_COST_PER_LIEN_USD = 1200
    _TITLE_TAX_DELINQUENCY_COST_USD = 8000
    _TITLE_HOA_DELINQUENCY_COST_USD = 3500

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._searched_counties: list = []
        self.flow = GlobalAISourcesFlow(bot_name="ForeclosureFinderBot")

    def _check_county_limit(self, county: str) -> None:
        limit = self.COUNTY_LIMITS[self.tier]
        county_lower = county.lower().replace(" ", "_")
        if (
            limit is not None
            and len(self._searched_counties) >= limit
            and county_lower not in self._searched_counties
        ):
            raise ForeclosureFinderBotTierError(
                f"County search limit of {limit} reached on {self.config.name} tier. "
                "Upgrade to search more counties."
            )
        if county_lower not in self._searched_counties:
            self._searched_counties.append(county_lower)

    def _get_property_by_id(self, property_id: str) -> dict:
        for prop in self.FORECLOSURE_DATABASE:
            if prop["id"] == property_id:
                return dict(prop)
        return dict(self.FORECLOSURE_DATABASE[0])

    def _compute_discount_pct(self, listing_price: float, market_value: float) -> float:
        if market_value <= 0:
            return 0.0
        return round((1 - listing_price / market_value) * 100, 1)

    def _assess_risk_level(self, prop: dict) -> str:
        """Return LOW / MEDIUM / HIGH / VERY HIGH based on property risk factors."""
        risk_score = 0
        risk_score += min(5, prop.get("liens_count", 0))
        if prop.get("tax_delinquent"):
            risk_score += 2
        if prop.get("hoa_delinquent"):
            risk_score += 1
        if prop.get("days_delinquent", 0) > 365:
            risk_score += 2
        if prop.get("year_built", 2000) < 1960:
            risk_score += 1

        if risk_score <= 2:
            return "LOW"
        if risk_score <= 4:
            return "MEDIUM"
        if risk_score <= 6:
            return "HIGH"
        return "VERY HIGH"

    def search_foreclosures(self, county: str, max_price: float = None) -> list:
        """Return foreclosure properties in the specified county."""
        self._check_county_limit(county)
        county_lower = county.lower().replace(" ", "_")

        results = [
            prop for prop in self.FORECLOSURE_DATABASE
            if prop["county"].lower().replace(" ", "_") == county_lower
        ]

        if not results:
            # Return first few as fallback for unknown counties
            results = list(self.FORECLOSURE_DATABASE[:3])

        if max_price is not None:
            results = [p for p in results if p["listing_price"] <= max_price]

        results_limit = self.RESULTS_LIMITS[self.tier]
        if results_limit is not None:
            results = results[:results_limit]

        output = []
        for prop in results:
            entry = {
                "id": prop["id"],
                "address": prop["address"],
                "county": prop["county"],
                "status": prop["status"],
                "listing_price_usd": prop["listing_price"],
                "market_value_usd": prop["market_value"],
                "discount_pct": self._compute_discount_pct(prop["listing_price"], prop["market_value"]),
                "beds": prop["beds"],
                "baths": prop["baths"],
                "sqft": prop["sqft"],
                "tier": self.tier.value,
            }

            if self.tier in (Tier.PRO, Tier.ENTERPRISE):
                entry["tax_delinquent"] = prop["tax_delinquent"]
                entry["hoa_delinquent"] = prop["hoa_delinquent"]
                entry["liens_count"] = prop["liens_count"]
                entry["days_delinquent"] = prop["days_delinquent"]
                entry["risk_level"] = self._assess_risk_level(prop)
                if prop["auction_date"]:
                    entry["auction_date"] = prop["auction_date"]

            output.append(entry)

        return output

    def evaluate_foreclosure(self, property_id: str) -> dict:
        """Return risk assessment and discount analysis for a foreclosure property."""
        prop = self._get_property_by_id(property_id)
        discount = self._compute_discount_pct(prop["listing_price"], prop["market_value"])
        risk_level = self._assess_risk_level(prop)
        potential_profit = prop["market_value"] - prop["listing_price"]

        result = {
            "property_id": property_id,
            "address": prop["address"],
            "status": prop["status"],
            "listing_price_usd": prop["listing_price"],
            "market_value_usd": prop["market_value"],
            "discount_from_market_pct": discount,
            "potential_gross_profit_usd": potential_profit,
            "risk_level": risk_level,
            "year_built": prop["year_built"],
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["lien_summary"] = {
                "liens_count": prop["liens_count"],
                "tax_delinquent": prop["tax_delinquent"],
                "hoa_delinquent": prop["hoa_delinquent"],
                "days_delinquent": prop["days_delinquent"],
                "estimated_lien_payoff_usd": (prop["liens_count"] * self._COST_PER_LIEN_USD
                                               + (self._TAX_DELINQUENCY_COST_USD if prop["tax_delinquent"] else 0)),
            }
            result["net_profit_after_liens_usd"] = round(
                potential_profit - result["lien_summary"]["estimated_lien_payoff_usd"], 0
            )
            if prop["auction_date"]:
                result["auction_date"] = prop["auction_date"]
            if prop["bank"]:
                result["bank_reo_contact"] = prop["bank"]

        if self.tier == Tier.ENTERPRISE:
            result["title_risks"] = self.check_title_risks(property_id)
            result["predictive_alert"] = {
                "foreclosure_likelihood_next_90days": "HIGH" if prop["days_delinquent"] > 270 else "MEDIUM",
                "recommended_action": "Submit offer immediately" if discount > 30 else "Monitor and wait",
            }

        return result

    def get_auction_calendar(self, county: str = None) -> list:
        """Return upcoming auction listings, optionally filtered by county."""
        if self.tier == Tier.FREE:
            raise ForeclosureFinderBotTierError(
                "Auction calendar requires PRO or ENTERPRISE tier."
            )

        auctions = [p for p in self.FORECLOSURE_DATABASE if p["auction_date"] is not None]

        if county:
            county_lower = county.lower().replace(" ", "_")
            auctions = [p for p in auctions if p["county"].lower().replace(" ", "_") == county_lower]

        result = []
        for prop in sorted(auctions, key=lambda x: x["auction_date"]):
            entry = {
                "id": prop["id"],
                "address": prop["address"],
                "county": prop["county"],
                "state": prop["state"],
                "auction_date": prop["auction_date"],
                "opening_bid_usd": prop["listing_price"],
                "estimated_market_value_usd": prop["market_value"],
                "discount_pct": self._compute_discount_pct(prop["listing_price"], prop["market_value"]),
                "beds": prop["beds"],
                "baths": prop["baths"],
                "sqft": prop["sqft"],
            }
            if self.tier == Tier.ENTERPRISE:
                entry["risk_level"] = self._assess_risk_level(prop)
                entry["liens_count"] = prop["liens_count"]
            result.append(entry)

        return result

    def check_title_risks(self, property_id: str) -> dict:
        """Return lien and title risk assessment (PRO/ENTERPRISE only)."""
        if self.tier == Tier.FREE:
            raise ForeclosureFinderBotTierError(
                "Title risk assessment requires PRO or ENTERPRISE tier."
            )

        prop = self._get_property_by_id(property_id)
        liens_count = prop.get("liens_count", 0)
        tax_del = prop.get("tax_delinquent", False)
        hoa_del = prop.get("hoa_delinquent", False)
        year_built = prop.get("year_built", 2000)

        risks = []
        if liens_count > 0:
            risks.append(f"{liens_count} lien(s) recorded — title search required before purchase")
        if tax_del:
            risks.append("Tax delinquency flag — county may hold senior lien")
        if hoa_del:
            risks.append("HOA delinquency — potential super-lien in some states")
        if year_built < 1978:
            risks.append("Pre-1978 construction — lead paint disclosure required")
        if year_built < 1960:
            risks.append("Pre-1960 construction — potential asbestos, outdated wiring")

        overall_risk = self._assess_risk_level(prop)
        estimated_title_clearance_cost = (
            liens_count * self._TITLE_CLEARANCE_COST_PER_LIEN_USD
            + (self._TITLE_TAX_DELINQUENCY_COST_USD if tax_del else 0)
            + (self._TITLE_HOA_DELINQUENCY_COST_USD if hoa_del else 0)
        )

        return {
            "property_id": property_id,
            "overall_title_risk": overall_risk,
            "liens_count": liens_count,
            "risk_factors": risks,
            "estimated_title_clearance_cost_usd": estimated_title_clearance_cost,
            "recommendation": "Proceed with caution — hire title attorney" if overall_risk in ("HIGH", "VERY HIGH") else "Standard title search recommended",
        }

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Foreclosure Finder Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output

    def run(self) -> dict:
        """Run the GlobalAISourcesFlow pipeline with sample foreclosure data."""
        sample_data = [
            {k: v for k, v in prop.items()}
            for prop in self.FORECLOSURE_DATABASE[:5]
        ]
        return self.flow.run_pipeline(
            raw_data={"foreclosure_listings": sample_data, "tier": self.tier.value},
            learning_method="supervised",
        )
