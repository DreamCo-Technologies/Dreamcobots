"""Home Flipping Analyzer Bot — tier-aware property flip analysis and ROI calculator."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.home_flipping_analyzer.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class HomeFlippingAnalyzerTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class HomeFlippingAnalyzerBot:
    """Tier-aware home flipping analyzer: ARV, renovation cost, ROI, and deal scoring."""

    PROPERTY_LIMITS = {Tier.FREE: 1, Tier.PRO: 5, Tier.ENTERPRISE: None}

    # Sample/mock flip property database for demonstration purposes
    FLIP_DATABASE = {
        "FLP001": {
            "address": "412 Maple St, Memphis TN",
            "purchase_price": 85000,
            "current_condition": "distressed",
            "sqft": 1200,
            "beds": 3, "baths": 1,
            "year_built": 1968,
            "market": "memphis",
            "arv_estimate": 145000,
            "days_on_market": 45,
            "neighborhood_grade": "C",
        },
        "FLP002": {
            "address": "7820 Oak Ave, Cleveland OH",
            "purchase_price": 62000,
            "current_condition": "distressed",
            "sqft": 1450,
            "beds": 3, "baths": 2,
            "year_built": 1955,
            "market": "cleveland",
            "arv_estimate": 128000,
            "days_on_market": 60,
            "neighborhood_grade": "C",
        },
        "FLP003": {
            "address": "1901 Peach Tree Ln, Atlanta GA",
            "purchase_price": 175000,
            "current_condition": "fair",
            "sqft": 1650,
            "beds": 3, "baths": 2,
            "year_built": 1978,
            "market": "atlanta",
            "arv_estimate": 265000,
            "days_on_market": 30,
            "neighborhood_grade": "B",
        },
        "FLP004": {
            "address": "304 Birch Rd, Indianapolis IN",
            "purchase_price": 72000,
            "current_condition": "distressed",
            "sqft": 1100,
            "beds": 2, "baths": 1,
            "year_built": 1962,
            "market": "indianapolis",
            "arv_estimate": 118000,
            "days_on_market": 55,
            "neighborhood_grade": "C+",
        },
        "FLP005": {
            "address": "5540 Cypress Dr, Tampa FL",
            "purchase_price": 210000,
            "current_condition": "fair",
            "sqft": 1800,
            "beds": 4, "baths": 2,
            "year_built": 1985,
            "market": "tampa",
            "arv_estimate": 340000,
            "days_on_market": 22,
            "neighborhood_grade": "B+",
        },
        "FLP006": {
            "address": "8802 Desert Rose Blvd, Phoenix AZ",
            "purchase_price": 195000,
            "current_condition": "fair",
            "sqft": 1550,
            "beds": 3, "baths": 2,
            "year_built": 1990,
            "market": "phoenix",
            "arv_estimate": 295000,
            "days_on_market": 28,
            "neighborhood_grade": "B",
        },
        "FLP007": {
            "address": "229 Elm St, Kansas City MO",
            "purchase_price": 55000,
            "current_condition": "distressed",
            "sqft": 1050,
            "beds": 2, "baths": 1,
            "year_built": 1950,
            "market": "kansas_city",
            "arv_estimate": 105000,
            "days_on_market": 70,
            "neighborhood_grade": "C",
        },
        "FLP008": {
            "address": "1620 Willow Way, Charlotte NC",
            "purchase_price": 165000,
            "current_condition": "fair",
            "sqft": 1700,
            "beds": 3, "baths": 2,
            "year_built": 1982,
            "market": "charlotte",
            "arv_estimate": 265000,
            "days_on_market": 18,
            "neighborhood_grade": "B+",
        },
        "FLP009": {
            "address": "3310 Sunflower Ct, Dallas TX",
            "purchase_price": 135000,
            "current_condition": "distressed",
            "sqft": 1350,
            "beds": 3, "baths": 1,
            "year_built": 1970,
            "market": "dallas",
            "arv_estimate": 230000,
            "days_on_market": 40,
            "neighborhood_grade": "B-",
        },
        "FLP010": {
            "address": "714 Magnolia Ave, Nashville TN",
            "purchase_price": 225000,
            "current_condition": "good",
            "sqft": 1900,
            "beds": 4, "baths": 2,
            "year_built": 1995,
            "market": "nashville",
            "arv_estimate": 355000,
            "days_on_market": 12,
            "neighborhood_grade": "A-",
        },
        "FLP011": {
            "address": "456 Riverfront Dr, Pittsburgh PA",
            "purchase_price": 68000,
            "current_condition": "distressed",
            "sqft": 1300,
            "beds": 3, "baths": 1,
            "year_built": 1948,
            "market": "pittsburgh",
            "arv_estimate": 122000,
            "days_on_market": 50,
            "neighborhood_grade": "C+",
        },
        "FLP012": {
            "address": "2201 Sunset Blvd, Las Vegas NV",
            "purchase_price": 185000,
            "current_condition": "fair",
            "sqft": 1600,
            "beds": 3, "baths": 2,
            "year_built": 1998,
            "market": "las_vegas",
            "arv_estimate": 290000,
            "days_on_market": 25,
            "neighborhood_grade": "B",
        },
        "FLP013": {
            "address": "903 Hickory Lane, Columbus OH",
            "purchase_price": 80000,
            "current_condition": "distressed",
            "sqft": 1250,
            "beds": 3, "baths": 1,
            "year_built": 1965,
            "market": "columbus",
            "arv_estimate": 148000,
            "days_on_market": 62,
            "neighborhood_grade": "C+",
        },
        "FLP014": {
            "address": "1750 Harbor View Rd, Tampa FL",
            "purchase_price": 245000,
            "current_condition": "good",
            "sqft": 2000,
            "beds": 4, "baths": 3,
            "year_built": 2000,
            "market": "tampa",
            "arv_estimate": 390000,
            "days_on_market": 15,
            "neighborhood_grade": "A-",
        },
        "FLP015": {
            "address": "607 Chestnut Blvd, Detroit MI",
            "purchase_price": 35000,
            "current_condition": "distressed",
            "sqft": 1100,
            "beds": 3, "baths": 1,
            "year_built": 1945,
            "market": "detroit",
            "arv_estimate": 82000,
            "days_on_market": 90,
            "neighborhood_grade": "D",
        },
        "FLP016": {
            "address": "2880 Lakewood Dr, Denver CO",
            "purchase_price": 285000,
            "current_condition": "fair",
            "sqft": 1750,
            "beds": 3, "baths": 2,
            "year_built": 1972,
            "market": "denver",
            "arv_estimate": 430000,
            "days_on_market": 20,
            "neighborhood_grade": "B+",
        },
        "FLP017": {
            "address": "5192 Palm Ave, Houston TX",
            "purchase_price": 110000,
            "current_condition": "distressed",
            "sqft": 1400,
            "beds": 3, "baths": 2,
            "year_built": 1975,
            "market": "houston",
            "arv_estimate": 195000,
            "days_on_market": 48,
            "neighborhood_grade": "C+",
        },
        "FLP018": {
            "address": "338 Vineyard St, Austin TX",
            "purchase_price": 320000,
            "current_condition": "good",
            "sqft": 1950,
            "beds": 3, "baths": 2,
            "year_built": 1988,
            "market": "austin",
            "arv_estimate": 495000,
            "days_on_market": 10,
            "neighborhood_grade": "A",
        },
        "FLP019": {
            "address": "4401 Redwood Ct, Sacramento CA",
            "purchase_price": 260000,
            "current_condition": "fair",
            "sqft": 1600,
            "beds": 3, "baths": 2,
            "year_built": 1980,
            "market": "sacramento",
            "arv_estimate": 395000,
            "days_on_market": 22,
            "neighborhood_grade": "B",
        },
        "FLP020": {
            "address": "1014 Ironwood Dr, San Antonio TX",
            "purchase_price": 98000,
            "current_condition": "distressed",
            "sqft": 1300,
            "beds": 3, "baths": 1,
            "year_built": 1960,
            "market": "san_antonio",
            "arv_estimate": 172000,
            "days_on_market": 55,
            "neighborhood_grade": "C+",
        },
    }

    # Renovation cost estimates per sqft by scope and condition
    RENOVATION_COST_PER_SQFT = {
        "cosmetic": {"distressed": 15, "fair": 8, "good": 4},
        "moderate": {"distressed": 35, "fair": 22, "good": 14},
        "full_gut": {"distressed": 65, "fair": 45, "good": 28},
    }

    # Per-unit costs for specific renovation items
    RENOVATION_ITEM_COSTS = {
        "kitchen_full_remodel": 18000,
        "kitchen_cosmetic": 6000,
        "bathroom_full_remodel": 10000,
        "bathroom_cosmetic": 3500,
        "roof_replacement": 12000,
        "hvac_full_replacement": 9000,
        "hvac_repair": 2500,
        "flooring_per_sqft": 6,
        "paint_interior_per_sqft": 2,
        "paint_exterior": 4500,
        "windows_per_unit": 450,
        "electrical_update": 8000,
        "plumbing_update": 7000,
        "foundation_repair": 15000,
        "landscaping": 3500,
    }

    MARKET_APPRECIATION = {
        "austin": 6.2, "atlanta": 4.4, "tampa": 7.1, "phoenix": 4.8,
        "nashville": 5.5, "charlotte": 5.9, "dallas": 3.8, "houston": 3.1,
        "denver": 3.2, "las_vegas": 4.9, "memphis": 2.8, "cleveland": 2.5,
        "indianapolis": 3.1, "kansas_city": 3.0, "pittsburgh": 2.7,
        "columbus": 3.3, "detroit": 2.1, "sacramento": 4.5, "san_antonio": 3.5,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._analyzed_properties: list = []
        self.flow = GlobalAISourcesFlow(bot_name="HomeFlippingAnalyzerBot")

    def _check_property_limit(self, property_id: str) -> None:
        limit = self.PROPERTY_LIMITS[self.tier]
        if (
            limit is not None
            and len(self._analyzed_properties) >= limit
            and property_id not in self._analyzed_properties
        ):
            raise HomeFlippingAnalyzerTierError(
                f"Property analysis limit of {limit} reached on {self.config.name} tier. "
                "Upgrade to analyze more properties."
            )
        if property_id not in self._analyzed_properties:
            self._analyzed_properties.append(property_id)

    def _get_property(self, address_or_id: str) -> dict:
        """Look up a property by ID or partial address match."""
        if address_or_id in self.FLIP_DATABASE:
            return dict(self.FLIP_DATABASE[address_or_id])
        for pid, prop in self.FLIP_DATABASE.items():
            if address_or_id.lower() in prop["address"].lower():
                return dict(prop)
        # Fall back to first property
        first_key = next(iter(self.FLIP_DATABASE))
        return dict(self.FLIP_DATABASE[first_key])

    def _get_property_id(self, address_or_id: str) -> str:
        """Return the database key for a property."""
        if address_or_id in self.FLIP_DATABASE:
            return address_or_id
        for pid, prop in self.FLIP_DATABASE.items():
            if address_or_id.lower() in prop["address"].lower():
                return pid
        return next(iter(self.FLIP_DATABASE))

    def calculate_arv(self, property_id: str, comparable_sales: list = None) -> float:
        """Return the estimated After Repair Value for a property.

        On PRO/ENTERPRISE tiers, comparable_sales (list of recent sold prices)
        can be supplied to refine the estimate.
        """
        prop = self._get_property(property_id)
        base_arv = prop["arv_estimate"]

        if comparable_sales and self.tier in (Tier.PRO, Tier.ENTERPRISE):
            avg_comp = sum(comparable_sales) / len(comparable_sales)
            # Blend database estimate 60% with comp average 40%
            base_arv = round(base_arv * 0.6 + avg_comp * 0.4, 0)

        if self.tier == Tier.ENTERPRISE:
            # Apply market appreciation factor (6-month forward estimate)
            market = prop.get("market", "austin")
            appreciation_rate = self.MARKET_APPRECIATION.get(market, 4.0) / 100
            base_arv = round(base_arv * (1 + appreciation_rate * 0.5), 0)

        return base_arv

    def estimate_renovation_cost(self, property_id: str, renovation_scope: str = "moderate") -> dict:
        """Return a detailed renovation cost breakdown.

        renovation_scope: 'cosmetic' | 'moderate' | 'full_gut'
        PRO/ENTERPRISE tiers get itemized breakdowns.
        """
        prop = self._get_property(property_id)
        condition = prop.get("current_condition", "fair")
        sqft = prop.get("sqft", 1200)
        scope = renovation_scope if renovation_scope in self.RENOVATION_COST_PER_SQFT else "moderate"

        base_cost_per_sqft = self.RENOVATION_COST_PER_SQFT[scope][condition]
        base_total = sqft * base_cost_per_sqft

        result = {
            "property_id": property_id,
            "renovation_scope": scope,
            "condition": condition,
            "sqft": sqft,
            "estimated_total_usd": round(base_total, 0),
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            items = self._build_itemized_costs(prop, scope)
            result["itemized_costs"] = items
            result["estimated_total_usd"] = round(sum(items.values()), 0)

            if self.tier == Tier.ENTERPRISE:
                result["contractor_bids"] = self._simulate_contractor_bids(result["estimated_total_usd"])

        return result

    def _build_itemized_costs(self, prop: dict, scope: str) -> dict:
        """Build itemized renovation cost breakdown."""
        sqft = prop.get("sqft", 1200)
        condition = prop.get("current_condition", "fair")
        items = {}

        if scope in ("moderate", "full_gut"):
            if scope == "full_gut" or condition == "distressed":
                items["kitchen"] = self.RENOVATION_ITEM_COSTS["kitchen_full_remodel"]
                items["bathrooms"] = self.RENOVATION_ITEM_COSTS["bathroom_full_remodel"] * prop.get("baths", 1)
            else:
                items["kitchen"] = self.RENOVATION_ITEM_COSTS["kitchen_cosmetic"]
                items["bathrooms"] = self.RENOVATION_ITEM_COSTS["bathroom_cosmetic"] * prop.get("baths", 1)

        items["flooring"] = sqft * self.RENOVATION_ITEM_COSTS["flooring_per_sqft"]
        items["interior_paint"] = sqft * self.RENOVATION_ITEM_COSTS["paint_interior_per_sqft"]
        items["exterior_paint"] = self.RENOVATION_ITEM_COSTS["paint_exterior"]
        items["landscaping"] = self.RENOVATION_ITEM_COSTS["landscaping"]

        if condition == "distressed" or scope == "full_gut":
            items["roof"] = self.RENOVATION_ITEM_COSTS["roof_replacement"]
            items["hvac"] = self.RENOVATION_ITEM_COSTS["hvac_full_replacement"]
            items["electrical"] = self.RENOVATION_ITEM_COSTS["electrical_update"]
            items["plumbing"] = self.RENOVATION_ITEM_COSTS["plumbing_update"]
        elif condition == "fair":
            items["hvac_repair"] = self.RENOVATION_ITEM_COSTS["hvac_repair"]

        # 10% contingency
        subtotal = sum(items.values())
        items["contingency_10pct"] = round(subtotal * 0.10, 0)

        return {k: round(v, 0) for k, v in items.items()}

    def _simulate_contractor_bids(self, base_cost: float) -> list:
        """Simulate three contractor bids around the base estimate."""
        return [
            {"contractor": "Budget Pro Renovations", "bid_usd": round(base_cost * 0.88, 0), "timeline_weeks": 12},
            {"contractor": "Mid-Range Builders LLC", "bid_usd": round(base_cost * 1.00, 0), "timeline_weeks": 10},
            {"contractor": "Premium Finish Contractors", "bid_usd": round(base_cost * 1.15, 0), "timeline_weeks": 8},
        ]

    def _compute_flip_score(self, profit: float, arv: float, reno_cost: float, holding_months: int, market_grade: str) -> int:
        """Compute a 0-100 flip score based on multiple factors."""
        score = 0

        # Profit margin component (max 40 pts)
        profit_margin_pct = (profit / arv * 100) if arv > 0 else 0
        score += min(40, int(profit_margin_pct * 1.5))

        # Renovation cost as % of ARV (lower is better, max 20 pts)
        reno_ratio = reno_cost / arv if arv > 0 else 1
        if reno_ratio < 0.15:
            score += 20
        elif reno_ratio < 0.25:
            score += 15
        elif reno_ratio < 0.35:
            score += 10
        else:
            score += 5

        # Holding period (shorter is better, max 20 pts)
        if holding_months <= 3:
            score += 20
        elif holding_months <= 5:
            score += 15
        elif holding_months <= 7:
            score += 10
        else:
            score += 5

        # Neighborhood grade (max 20 pts)
        grade_scores = {"A": 20, "A-": 18, "B+": 16, "B": 14, "B-": 12,
                        "C+": 9, "C": 7, "C-": 5, "D": 2}
        score += grade_scores.get(market_grade, 7)

        return min(100, max(0, score))

    def analyze_flip(self, address_or_id: str) -> dict:
        """Return complete flip analysis: ARV, costs, profit, flip score."""
        pid = self._get_property_id(address_or_id)
        self._check_property_limit(pid)
        prop = self._get_property(address_or_id)

        purchase_price = prop["purchase_price"]
        condition = prop.get("current_condition", "fair")

        # Determine renovation scope from condition
        scope_map = {"distressed": "full_gut", "fair": "moderate", "good": "cosmetic"}
        scope = scope_map.get(condition, "moderate")

        arv = self.calculate_arv(address_or_id)
        reno = self.estimate_renovation_cost(address_or_id, scope)
        reno_cost = reno["estimated_total_usd"]

        # Holding period estimate based on market days_on_market
        dom = prop.get("days_on_market", 30)
        holding_months = max(3, round((dom + 90) / 30))  # reno time + sale time

        holding_cost_monthly = purchase_price * 0.008  # ~0.8% of purchase/month (taxes, insurance, utilities)
        holding_costs_total = holding_cost_monthly * holding_months

        closing_costs_buy = purchase_price * 0.02
        closing_costs_sell = arv * 0.06  # agent commission + transfer taxes

        total_costs = purchase_price + reno_cost + holding_costs_total + closing_costs_buy + closing_costs_sell
        profit = arv - total_costs
        profit_margin_pct = round(profit / arv * 100, 1) if arv > 0 else 0
        roi_pct = round(profit / (purchase_price + reno_cost) * 100, 1)

        flip_score = self._compute_flip_score(profit, arv, reno_cost, holding_months, prop.get("neighborhood_grade", "C"))

        result = {
            "property_id": pid,
            "address": prop["address"],
            "purchase_price_usd": purchase_price,
            "arv_usd": arv,
            "renovation_cost_usd": reno_cost,
            "renovation_scope": scope,
            "holding_months": holding_months,
            "holding_costs_usd": round(holding_costs_total, 0),
            "closing_costs_buy_usd": round(closing_costs_buy, 0),
            "closing_costs_sell_usd": round(closing_costs_sell, 0),
            "total_project_cost_usd": round(total_costs, 0),
            "estimated_profit_usd": round(profit, 0),
            "profit_margin_pct": profit_margin_pct,
            "roi_pct": roi_pct,
            "flip_score": flip_score,
            "neighborhood_grade": prop.get("neighborhood_grade", "C"),
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["itemized_renovation"] = reno.get("itemized_costs", {})
            result["financing_cost_usd"] = round(purchase_price * 0.10 * (holding_months / 12), 0)
            result["flip_score_breakdown"] = {
                "profit_margin_contribution": min(40, int(profit_margin_pct * 1.5)),
                "renovation_ratio_contribution": round(reno_cost / arv, 3) if arv else 0,
                "holding_period_months": holding_months,
                "neighborhood_grade": prop.get("neighborhood_grade", "C"),
            }

        if self.tier == Tier.ENTERPRISE:
            market = prop.get("market", "austin")
            appreciation = self.MARKET_APPRECIATION.get(market, 4.0)
            result["market_timing_score"] = min(100, int(appreciation * 10))
            result["recommended_listing_strategy"] = (
                "List immediately after renovation" if dom <= 20 else "Season market — list in spring"
            )
            if "contractor_bids" not in result:
                result["contractor_bids"] = reno.get("contractor_bids", [])

        return result

    def get_top_flip_opportunities(self, limit: int = 5) -> list:
        """Return properties sorted by flip potential (flip score descending)."""
        results = []
        for pid in self.FLIP_DATABASE:
            prop = self.FLIP_DATABASE[pid]
            purchase_price = prop["purchase_price"]
            arv = prop["arv_estimate"]
            condition = prop.get("current_condition", "fair")
            scope_map = {"distressed": "full_gut", "fair": "moderate", "good": "cosmetic"}
            scope = scope_map.get(condition, "moderate")
            reno_cost_per_sqft = self.RENOVATION_COST_PER_SQFT[scope][condition]
            reno_cost = prop["sqft"] * reno_cost_per_sqft
            dom = prop.get("days_on_market", 30)
            holding_months = max(3, round((dom + 90) / 30))
            holding_costs = purchase_price * 0.008 * holding_months
            total_costs = purchase_price + reno_cost + holding_costs + purchase_price * 0.02 + arv * 0.06
            profit = arv - total_costs
            flip_score = self._compute_flip_score(profit, arv, reno_cost, holding_months, prop.get("neighborhood_grade", "C"))
            results.append({
                "property_id": pid,
                "address": prop["address"],
                "purchase_price_usd": purchase_price,
                "arv_usd": arv,
                "estimated_profit_usd": round(profit, 0),
                "flip_score": flip_score,
                "neighborhood_grade": prop.get("neighborhood_grade", "C"),
            })

        results.sort(key=lambda x: x["flip_score"], reverse=True)
        return results[:limit]

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Home Flipping Analyzer Tier ===",
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
        """Run the GlobalAISourcesFlow pipeline with sample flip data."""
        sample_data = [
            {"property_id": pid, **{k: v for k, v in props.items() if k != "address"}}
            for pid, props in list(self.FLIP_DATABASE.items())[:5]
        ]
        return self.flow.run_pipeline(
            raw_data={"flip_properties": sample_data, "tier": self.tier.value},
            learning_method="supervised",
        )
