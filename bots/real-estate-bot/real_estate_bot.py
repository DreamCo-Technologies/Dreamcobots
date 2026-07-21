"""Real Estate Bot - Property valuation, investment analysis, and market insights."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot


class RealEstateBot(BaseBot):
    """AI bot for real estate investment analysis, valuations, and market research."""

    def __init__(self):
        """Initialize the RealEstateBot."""
        super().__init__(
            name="real-estate-bot",
            description="Analyzes real estate investments, estimates property values, and provides market insights.",
            version="2.0.0",
        )
        self.priority = "medium"

    def run(self):
        """Run the real estate bot main workflow."""
        self.start()
        return self.get_status()

    def estimate_value(self, property_data: dict) -> dict:
        """Estimate a property's market value using comparable analysis."""
        sqft = property_data.get("sqft", 1500)
        bedrooms = property_data.get("bedrooms", 3)
        bathrooms = property_data.get("bathrooms", 2)
        location = property_data.get("location", "Unknown")
        year_built = property_data.get("year_built", 2000)
        price_per_sqft = 250
        base_value = sqft * price_per_sqft
        bed_adj = (bedrooms - 3) * 10000
        bath_adj = (bathrooms - 2) * 8000
        age_adj = max(-50000, (2024 - year_built) * -500)
        estimated_value = base_value + bed_adj + bath_adj + age_adj
        return {
            "location": location,
            "property_specs": property_data,
            "estimated_value": f"${estimated_value:,.0f}",
            "price_per_sqft": f"${price_per_sqft}",
            "value_range": {
                "low": f"${estimated_value * 0.90:,.0f}",
                "high": f"${estimated_value * 1.10:,.0f}",
            },
            "methodology": "Comparable sales analysis (mock data - use licensed appraiser for official valuation)",
            "disclaimer": "This is an automated estimate. Get a professional appraisal for financing or legal purposes.",
        }

    def analyze_investment(self, purchase_price: float, monthly_rent: float, expenses: float) -> dict:
        """Analyze a rental property investment for ROI, cap rate, and cash flow."""
        annual_rent = monthly_rent * 12
        annual_expenses = expenses * 12
        noi = annual_rent - annual_expenses
        cap_rate = (noi / purchase_price * 100) if purchase_price > 0 else 0
        cash_flow_monthly = monthly_rent - expenses
        cash_on_cash = (cash_flow_monthly * 12 / (purchase_price * 0.20) * 100) if purchase_price > 0 else 0
        gross_rent_multiplier = purchase_price / annual_rent if annual_rent > 0 else 0
        return {
            "purchase_price": purchase_price,
            "monthly_rent": monthly_rent,
            "monthly_expenses": expenses,
            "monthly_cash_flow": round(cash_flow_monthly, 2),
            "annual_noi": round(noi, 2),
            "cap_rate_percent": round(cap_rate, 2),
            "cash_on_cash_return_percent": round(cash_on_cash, 2),
            "gross_rent_multiplier": round(gross_rent_multiplier, 2),
            "investment_rating": "Excellent" if cap_rate >= 8 else "Good" if cap_rate >= 5 else "Fair" if cap_rate >= 3 else "Poor",
            "break_even_months": round(purchase_price / (monthly_rent - expenses)) if cash_flow_monthly > 0 else "Negative cash flow",
            "rule_of_1_percent": f"{'✅ Meets' if monthly_rent >= purchase_price * 0.01 else '❌ Does not meet'} 1% rule (rent/price)",
        }

    def analyze_market(self, location: str, property_type: str) -> dict:
        """Analyze real estate market trends for a given location and property type."""
        return {
            "location": location,
            "property_type": property_type,
            "market_temperature": "Seller's Market",
            "median_home_price": "$425,000",
            "price_change_yoy": "+6.8%",
            "days_on_market_avg": 18,
            "inventory_months": 1.8,
            "mortgage_rate_30yr": "6.95%",
            "rental_vacancy_rate": "4.2%",
            "rental_yield_avg": "5.8%",
            "population_growth_yoy": "+2.1%",
            "job_growth_yoy": "+3.4%",
            "market_forecast_12mo": "Moderate appreciation expected (3-5%)",
            "best_investment_strategy": "Buy-and-hold rental" if True else "Flip",
        }

    def calculate_rental_income(self, monthly_rent: float, vacancy_rate: float, expenses: float) -> dict:
        """Calculate net rental income after vacancy and expenses."""
        effective_rent = monthly_rent * (1 - vacancy_rate / 100)
        net_monthly = effective_rent - expenses
        net_annual = net_monthly * 12
        return {
            "gross_monthly_rent": monthly_rent,
            "vacancy_rate_percent": vacancy_rate,
            "vacancy_loss_monthly": round(monthly_rent * vacancy_rate / 100, 2),
            "effective_gross_income_monthly": round(effective_rent, 2),
            "monthly_expenses": expenses,
            "net_operating_income_monthly": round(net_monthly, 2),
            "net_operating_income_annual": round(net_annual, 2),
            "expense_ratio_percent": round(expenses / monthly_rent * 100, 1) if monthly_rent > 0 else 0,
        }

    def compare_properties(self, properties: list) -> list:
        """Compare multiple properties side by side."""
        scored = []
        for prop in properties:
            price = prop.get("price", 1)
            rent = prop.get("monthly_rent", 0)
            expenses = prop.get("monthly_expenses", 0)
            analysis = self.analyze_investment(price, rent, expenses)
            scored.append({
                "address": prop.get("address", "Unknown"),
                "price": price,
                "cap_rate": analysis["cap_rate_percent"],
                "monthly_cash_flow": analysis["monthly_cash_flow"],
                "rating": analysis["investment_rating"],
            })
        scored.sort(key=lambda x: x["cap_rate"], reverse=True)
        for i, p in enumerate(scored):
            p["rank"] = i + 1
        return scored

    def analyze_neighborhood(self, location: str) -> dict:
        """Analyze neighborhood quality for real estate investment."""
        return {
            "location": location,
            "overall_score": 82,
            "categories": {
                "safety_score": 78,
                "school_rating": "B+ (7.8/10)",
                "walkability_score": 74,
                "transit_score": 65,
                "amenities_score": 88,
                "job_market_score": 85,
                "appreciation_potential": 80,
            },
            "nearby_amenities": [
                "Grocery stores: 3 within 1 mile",
                "Restaurants: 25+ within 1 mile",
                "Parks: 2 within walking distance",
                "Hospital: 2.3 miles",
                "Major employer: Amazon warehouse (1.8 miles)",
            ],
            "risk_factors": ["Flood zone check recommended", "Review HOA rules if applicable"],
            "data_sources": ["Walk Score", "GreatSchools", "FBI Crime Data (mock)"],
        }

    def score_deal(self, property_data: dict) -> dict:
        """Score a real estate deal on a scale of 1-10."""
        price = property_data.get("price", 1)
        rent = property_data.get("monthly_rent", 0)
        expenses = property_data.get("monthly_expenses", 0)
        location_score = property_data.get("location_score", 70)
        analysis = self.analyze_investment(price, rent, expenses)
        cap_rate = analysis["cap_rate_percent"]
        cap_score = min(10, cap_rate * 1.2)
        location_pts = location_score / 10
        cashflow_pts = 3 if analysis["monthly_cash_flow"] > 0 else 0
        final_score = round((cap_score * 0.4) + (location_pts * 0.4) + cashflow_pts, 1)
        final_score = max(1, min(10, final_score))
        return {
            "deal_score": final_score,
            "rating": "🔥 Hot Deal" if final_score >= 8 else "✅ Good" if final_score >= 6 else "⚠️ Average" if final_score >= 4 else "❌ Pass",
            "cap_rate": analysis["cap_rate_percent"],
            "monthly_cash_flow": analysis["monthly_cash_flow"],
            "recommendation": "Buy" if final_score >= 7 else "Negotiate" if final_score >= 5 else "Pass",
        }

    def flip_vs_rent(self, purchase_price: float, renovation_cost: float,
                     arv: float, monthly_rent: float) -> dict:
        """Analyze whether to flip or rent a property."""
        flip_profit = arv - purchase_price - renovation_cost - (arv * 0.08)
        flip_roi = (flip_profit / (purchase_price + renovation_cost) * 100) if (purchase_price + renovation_cost) > 0 else 0
        rental_analysis = self.analyze_investment(purchase_price, monthly_rent, monthly_rent * 0.45)
        return {
            "property_info": {
                "purchase_price": purchase_price,
                "renovation_cost": renovation_cost,
                "arv": arv,
                "monthly_rent": monthly_rent,
            },
            "flip_analysis": {
                "projected_profit": round(flip_profit, 2),
                "roi_percent": round(flip_roi, 2),
                "timeline": "3-6 months",
                "risk": "Medium-High",
            },
            "rent_analysis": {
                "cap_rate": rental_analysis["cap_rate_percent"],
                "monthly_cash_flow": rental_analysis["monthly_cash_flow"],
                "timeline": "Long-term hold",
                "risk": "Low-Medium",
            },
            "recommendation": "Flip" if flip_roi > 20 and flip_profit > 30000 else "Rent",
            "reasoning": f"Flip ROI of {flip_roi:.1f}% {'exceeds' if flip_roi > 20 else 'does not exceed'} 20% threshold",
        }
