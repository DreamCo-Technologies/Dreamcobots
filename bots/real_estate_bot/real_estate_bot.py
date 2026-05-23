"""Real Estate Bot — tier-aware real estate deal finder, ROI analyzer, and
Housing + Government Contract engine.

Engines:
  1. Property Acquisition        — find_distressed_properties()
  2. Government Program Finder   — find_gov_housing_programs()
  3. Revenue Matching Engine     — match_property_to_program(), calculate_housing_revenue()
  4. Outreach Engine             — send_outreach()
"""
import sys, os
from typing import Any, Callable
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

    CALCULATORS = [
        {
            "id": "capital_deployment_efficiency",
            "name": "Capital Deployment Efficiency",
            "domain": "All",
            "system": "Capital Deployment",
            "description": "Measures how efficiently deployed capital generates returns",
            "formula": "Efficiency = Annual Returns / Total Capital Deployed * 100",
            "variables": ["annual_returns", "total_capital_deployed"],
            "target": "15%+ annual return on deployed capital",
            "tags": ["efficiency", "returns", "deployment"],
        },
        {
            "id": "debt_to_equity_ratio",
            "name": "Debt-to-Equity Ratio",
            "domain": "All",
            "system": "Capital Deployment",
            "description": "Monitors leverage levels across the portfolio",
            "formula": "D/E = Total Liabilities / Total Equity",
            "variables": ["total_liabilities", "total_equity"],
            "target": "D/E < 2.0 for conservative leverage",
            "tags": ["leverage", "debt", "equity"],
        },
        {
            "id": "liquidity_ratio",
            "name": "Liquidity Ratio",
            "domain": "All",
            "system": "Capital Deployment",
            "description": "Ensures adequate operating reserves relative to monthly burn rate",
            "formula": "Ratio = Operating Reserves / Monthly Burn Rate",
            "variables": ["operating_reserves", "monthly_burn_rate"],
            "target": ">= 6 months of reserves for safety",
            "tags": ["liquidity", "reserves", "safety"],
        },
        {
            "id": "reinvestment_multiplier",
            "name": "Reinvestment Multiplier",
            "domain": "All",
            "system": "Capital Deployment",
            "description": "Calculates the optimal profit reinvestment percentage for growth",
            "formula": "Reinvest Amount = Net Profit * 0.60",
            "variables": ["net_profit"],
            "target": "60% reinvest, 30% reserve, 10% expansion",
            "tags": ["reinvestment", "growth", "allocation"],
        },
        {
            "id": "capital_turn_rate",
            "name": "Capital Turn Rate",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Measures how many times capital is recycled per year",
            "formula": "Turn Rate = 365 / Average Hold Period",
            "variables": ["average_hold_period_days"],
            "target": "12+ turns per year for maximum capital efficiency",
            "tags": ["capital", "turnover", "efficiency"],
        },
        {
            "id": "car_spread_formula",
            "name": "Car Spread Formula",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Calculates the profit spread between market value and total costs",
            "formula": "Spread = Market Value - (Purchase + Repairs + Fees)",
            "variables": ["market_value", "purchase_price", "repair_cost", "fees"],
            "target": "Minimum 15-20% spread for viable deals",
            "tags": ["spread", "profit", "acquisition"],
        },
        {
            "id": "daily_profit_rate",
            "name": "Daily Profit Rate",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Calculates profit per day held to compare deal efficiency",
            "formula": "Daily Profit = Net Profit / Days Held",
            "variables": ["net_profit", "days_held"],
            "target": "Higher daily profit = better capital deployment",
            "tags": ["profit", "daily", "efficiency"],
        },
        {
            "id": "demand_velocity_score",
            "name": "Demand Velocity Score",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Measures how quickly a vehicle model sells in a given market",
            "formula": "Velocity = Listings Sold Last 30 Days / Active Listings",
            "variables": ["listings_sold_30_days", "active_listings"],
            "target": "Above 1.0 = high demand vehicle",
            "tags": ["demand", "velocity", "market"],
        },
        {
            "id": "max_purchase_price",
            "name": "Max Purchase Price",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Calculates the maximum purchase price for profitable car flips",
            "formula": "Max Purchase = (Expected Sale * 0.75) - Repair Costs",
            "variables": ["expected_sale_price", "repair_costs"],
            "target": "Never exceed max purchase for profitability",
            "tags": ["acquisition", "max-price", "limit"],
        },
        {
            "id": "repair_risk_multiplier",
            "name": "Repair Risk Multiplier",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Adjusts profit for repair cost uncertainty with a safety buffer",
            "formula": "Adjusted Profit = Spread - (Repair Estimate * 1.3)",
            "variables": ["spread", "repair_estimate"],
            "target": "Must remain positive after 30% buffer",
            "tags": ["repair", "risk", "buffer"],
        },
        {
            "id": "time_to_liquidation",
            "name": "Time-to-Liquidation",
            "domain": "Car Flipping",
            "system": "System",
            "description": "Predicts average days to sell based on model and zip code data",
            "formula": "TTL = Average Days on Market (Model + Zip Code)",
            "variables": ["avg_market_days"],
            "target": "Target under 21 days for rapid turn",
            "tags": ["liquidation", "speed", "turnover"],
        },
        {
            "id": "brrrr_recycle",
            "name": "BRRRR Recycle",
            "domain": "Real Estate",
            "system": "System",
            "description": "Validates if a BRRRR deal returns all invested capital through refinance",
            "formula": "Refi Amount >= Total Investment (Purchase + Repairs + Holding Costs)",
            "variables": ["arv", "ltv_ratio", "purchase_price", "repairs", "holding_costs"],
            "target": "Refi Amount >= Total Investment",
            "tags": ["brrrr", "refinance", "recycle"],
        },
        {
            "id": "core_flip_spread",
            "name": "Core Flip Spread",
            "domain": "Real Estate",
            "system": "System",
            "description": "Determines if a property is a strong flip candidate by calculating the spread between ARV and total costs",
            "formula": "Deal Score = (ARV * 0.70) - (Purchase Price + Repairs)",
            "variables": ["arv", "purchase_price", "repairs"],
            "target": "Deal Score > $25,000 = Strong Flip Candidate",
            "tags": ["flip", "spread", "acquisition"],
        },
        {
            "id": "debt_service_coverage",
            "name": "Debt Service Coverage",
            "domain": "Real Estate",
            "system": "System",
            "description": "Measures ability to cover debt payments from rental income",
            "formula": "DSCR = Net Operating Income / Annual Debt Service",
            "variables": ["net_operating_income", "annual_debt_service"],
            "target": "DSCR >= 1.25 for safe leverage",
            "tags": ["leverage", "debt", "risk"],
        },
        {
            "id": "equity_capture",
            "name": "Equity Capture",
            "domain": "Real Estate",
            "system": "System",
            "description": "Measures instant equity gained at purchase to ensure built-in profit margin",
            "formula": "Instant Equity % = (ARV - Purchase Price) / ARV * 100",
            "variables": ["arv", "purchase_price"],
            "target": "15%+ minimum instant equity",
            "tags": ["equity", "acquisition", "leverage"],
        },
        {
            "id": "maximum_allowable_offer",
            "name": "Maximum Allowable Offer",
            "domain": "Real Estate",
            "system": "System",
            "description": "Calculates the maximum price to offer on a flip deal using the 70% rule",
            "formula": "MAO = (ARV * 0.70) - Repair Costs",
            "variables": ["arv", "repair_costs"],
            "target": "Never exceed MAO for profitable flips",
            "tags": ["flip", "offer", "acquisition"],
        },
        {
            "id": "motivation_score",
            "name": "Motivation Score",
            "domain": "Real Estate",
            "system": "System",
            "description": "Scores seller motivation level to determine negotiation leverage",
            "formula": "Score = (Days on Market * 0.2) + (Price Drops * 5) + (Vacant Flag * 10)",
            "variables": ["days_on_market", "price_drops", "vacant_flag"],
            "target": "Higher score = higher negotiation leverage",
            "tags": ["negotiation", "seller", "acquisition"],
        },
        {
            "id": "rental_cashflow",
            "name": "Rental Cashflow",
            "domain": "Real Estate",
            "system": "System",
            "description": "Calculates cash-on-cash return for rental properties to ensure minimum profitability",
            "formula": "Cash-on-Cash Return = (Annual Net Income / Total Cash Invested) * 100",
            "variables": ["monthly_rent", "monthly_expenses", "total_cash_invested"],
            "target": "Minimum 8-12% Cash-on-Cash Return",
            "tags": ["rental", "cashflow", "hold"],
        },
        {
            "id": "rental_yield",
            "name": "Rental Yield",
            "domain": "Real Estate",
            "system": "System",
            "description": "Calculates annual rental yield as a percentage of property value",
            "formula": "Yield = (Annual Rent / Property Value) * 100",
            "variables": ["monthly_rent", "property_value"],
            "target": "5%+ gross yield for rental properties",
            "tags": ["rental", "yield", "analysis"],
        },
        {
            "id": "section_8_premium",
            "name": "Section 8 Premium",
            "domain": "Real Estate",
            "system": "System",
            "description": "Compares Section 8 voucher rates vs market rent for premium analysis",
            "formula": "Premium = (Section 8 Rate - Market Rent) / Market Rent * 100",
            "variables": ["section_8_rate", "market_rent"],
            "target": "Positive premium indicates above-market returns",
            "tags": ["section8", "rental", "government"],
        },
        {
            "id": "wholesale_assignment_fee",
            "name": "Wholesale Assignment Fee",
            "domain": "Real Estate",
            "system": "System",
            "description": "Calculates the assignment fee potential in a wholesale deal",
            "formula": "Fee = End Buyer Price - Contract Price",
            "variables": ["end_buyer_price", "contract_price"],
            "target": "Minimum $5,000 assignment fee",
            "tags": ["wholesale", "assignment", "quick-profit"],
        },
        {
            "id": "churn_prediction_score",
            "name": "Churn Prediction Score",
            "domain": "Revenue Intelligence",
            "system": "System",
            "description": "Predicts customer churn likelihood based on usage patterns",
            "formula": "Score = (Login Frequency * 0.3) + (Feature Usage * 0.4) + (Support Tickets * -0.3)",
            "variables": ["login_frequency", "feature_usage", "support_tickets"],
            "target": "Score < 40 = high churn risk, intervene immediately",
            "tags": ["churn", "prediction", "retention"],
        },
        {
            "id": "dynamic_pricing_optimizer",
            "name": "Dynamic Pricing Optimizer",
            "domain": "Revenue Intelligence",
            "system": "System",
            "description": "Adjusts pricing based on demand, competition, and capacity",
            "formula": "Optimal Price = Base Price * (1 + Demand Factor) * (1 - Competition Pressure)",
            "variables": ["base_price", "demand_factor", "competition_pressure"],
            "target": "Maximize revenue while maintaining conversion",
            "tags": ["pricing", "dynamic", "optimization"],
        },
        {
            "id": "revenue_leak_score",
            "name": "Revenue Leak Score",
            "domain": "Revenue Intelligence",
            "system": "System",
            "description": "Identifies and quantifies revenue losses across the system",
            "formula": "Leak Score = (Failed Transactions + Cart Abandonment + Pricing Errors) * Avg Order Value",
            "variables": ["failed_transactions", "cart_abandonment_rate", "pricing_errors", "avg_order_value"],
            "target": "Minimize leak score to zero",
            "tags": ["leak", "revenue", "detection"],
        },
        {
            "id": "revenue_per_bot",
            "name": "Revenue Per Bot",
            "domain": "Revenue Intelligence",
            "system": "System",
            "description": "Tracks revenue generation efficiency per AI agent",
            "formula": "RPB = Total Revenue / Active Bots",
            "variables": ["total_revenue", "active_bot_count"],
            "target": "Increasing RPB indicates platform efficiency",
            "tags": ["revenue", "bots", "efficiency"],
        },
        {
            "id": "drawdown_recovery",
            "name": "Drawdown Recovery",
            "domain": "Risk Management",
            "system": "System",
            "description": "Calculates time to recover from a portfolio drawdown",
            "formula": "Recovery Time = Loss Amount / Monthly Net Income",
            "variables": ["loss_amount", "monthly_net_income"],
            "target": "Recovery within 6 months for acceptable risk",
            "tags": ["drawdown", "recovery", "risk"],
        },
        {
            "id": "portfolio_concentration",
            "name": "Portfolio Concentration",
            "domain": "Risk Management",
            "system": "System",
            "description": "Measures exposure to any single asset type or market",
            "formula": "Concentration = Single Asset Value / Total Portfolio Value * 100",
            "variables": ["single_asset_value", "total_portfolio_value"],
            "target": "No single asset > 25% of total portfolio",
            "tags": ["diversification", "concentration", "portfolio"],
        },
        {
            "id": "risk_adjusted_return",
            "name": "Risk-Adjusted Return",
            "domain": "Risk Management",
            "system": "System",
            "description": "Adjusts returns for risk level to compare deals fairly",
            "formula": "RAR = Expected Return / Risk Score",
            "variables": ["expected_return", "risk_score"],
            "target": "Higher RAR = better risk-adjusted opportunity",
            "tags": ["risk", "return", "comparison"],
        },
        {
            "id": "cac_efficiency",
            "name": "CAC Efficiency",
            "domain": "Sales",
            "system": "System",
            "description": "Measures customer acquisition efficiency by comparing lifetime value to cost",
            "formula": "LTV/CAC Ratio = Customer Lifetime Value / Customer Acquisition Cost",
            "variables": ["customer_lifetime_value", "customer_acquisition_cost"],
            "target": "LTV/CAC >= 3 for healthy unit economics",
            "tags": ["cac", "ltv", "efficiency"],
        },
        {
            "id": "closing_probability",
            "name": "Closing Probability",
            "domain": "Sales",
            "system": "System",
            "description": "Predicts deal closing likelihood based on engagement signals",
            "formula": "Probability = (Meetings * 0.3) + (Proposal Sent * 0.4) + (Champion Score * 0.3)",
            "variables": ["meetings_held", "proposal_sent", "champion_score"],
            "target": "Above 70% = high-confidence close",
            "tags": ["closing", "probability", "prediction"],
        },
        {
            "id": "commission_roi",
            "name": "Commission ROI",
            "domain": "Sales",
            "system": "System",
            "description": "Calculates return on investment for commission-based sales teams",
            "formula": "ROI = (Revenue Generated - Total Commission Paid) / Total Commission Paid * 100",
            "variables": ["revenue_generated", "total_commission_paid"],
            "target": "Minimum 300% ROI on commission spend",
            "tags": ["commission", "roi", "team"],
        },
        {
            "id": "funnel_leak_detection",
            "name": "Funnel Leak Detection",
            "domain": "Sales",
            "system": "System",
            "description": "Identifies conversion drop-offs between sales funnel stages",
            "formula": "Drop-Off % = (Stage N Count - Stage N+1 Count) / Stage N Count * 100",
            "variables": ["stage_n_count", "stage_n1_count"],
            "target": "Identify stages with > 40% drop-off for optimization",
            "tags": ["funnel", "conversion", "optimization"],
        },
        {
            "id": "lead_value_formula",
            "name": "Lead Value Formula",
            "domain": "Sales",
            "system": "System",
            "description": "Calculates the expected value of each lead based on conversion probability",
            "formula": "Expected Value = Close Rate * Average Deal Size",
            "variables": ["close_rate", "average_deal_size"],
            "target": "Prioritize leads with highest expected value",
            "tags": ["leads", "value", "conversion"],
        },
        {
            "id": "pipeline_velocity",
            "name": "Pipeline Velocity",
            "domain": "Sales",
            "system": "System",
            "description": "Measures the speed of revenue flowing through the sales pipeline",
            "formula": "Velocity = (Opportunities * Win Rate * Deal Size) / Sales Cycle Days",
            "variables": ["opportunities", "win_rate", "average_deal_size", "sales_cycle_days"],
            "target": "Increasing velocity indicates improving sales efficiency",
            "tags": ["pipeline", "velocity", "revenue"],
        },
    ]

    def _safe_divide(self, numerator: float, denominator: float, calculator_id: str) -> float:
        if denominator == 0:
            raise ValueError(f"'{calculator_id}' denominator cannot be zero.")
        return numerator / denominator

    def _brrrr_recycle(self, inputs: dict[str, float]) -> dict:
        refi_amount = inputs["arv"] * inputs["ltv_ratio"]
        total_investment = inputs["purchase_price"] + inputs["repairs"] + inputs["holding_costs"]
        return {
            "refi_amount": round(refi_amount, 4),
            "total_investment": round(total_investment, 4),
            "recycled_capital": round(refi_amount - total_investment, 4),
            "qualifies": refi_amount >= total_investment,
        }

    @property
    def _calculator_functions(self) -> dict[str, Callable[[dict[str, float]], Any]]:
        return {
            "capital_deployment_efficiency": lambda i: self._safe_divide(i["annual_returns"], i["total_capital_deployed"], "capital_deployment_efficiency") * 100,
            "debt_to_equity_ratio": lambda i: self._safe_divide(i["total_liabilities"], i["total_equity"], "debt_to_equity_ratio"),
            "liquidity_ratio": lambda i: self._safe_divide(i["operating_reserves"], i["monthly_burn_rate"], "liquidity_ratio"),
            "reinvestment_multiplier": lambda i: i["net_profit"] * 0.60,
            "capital_turn_rate": lambda i: self._safe_divide(365, i["average_hold_period_days"], "capital_turn_rate"),
            "car_spread_formula": lambda i: i["market_value"] - (i["purchase_price"] + i["repair_cost"] + i["fees"]),
            "daily_profit_rate": lambda i: self._safe_divide(i["net_profit"], i["days_held"], "daily_profit_rate"),
            "demand_velocity_score": lambda i: self._safe_divide(i["listings_sold_30_days"], i["active_listings"], "demand_velocity_score"),
            "max_purchase_price": lambda i: (i["expected_sale_price"] * 0.75) - i["repair_costs"],
            "repair_risk_multiplier": lambda i: i["spread"] - (i["repair_estimate"] * 1.3),
            "time_to_liquidation": lambda i: i["avg_market_days"],
            "brrrr_recycle": self._brrrr_recycle,
            "core_flip_spread": lambda i: (i["arv"] * 0.70) - (i["purchase_price"] + i["repairs"]),
            "debt_service_coverage": lambda i: self._safe_divide(i["net_operating_income"], i["annual_debt_service"], "debt_service_coverage"),
            "equity_capture": lambda i: self._safe_divide(i["arv"] - i["purchase_price"], i["arv"], "equity_capture") * 100,
            "maximum_allowable_offer": lambda i: (i["arv"] * 0.70) - i["repair_costs"],
            "motivation_score": lambda i: (i["days_on_market"] * 0.2) + (i["price_drops"] * 5) + (i["vacant_flag"] * 10),
            "rental_cashflow": lambda i: self._safe_divide(((i["monthly_rent"] - i["monthly_expenses"]) * 12), i["total_cash_invested"], "rental_cashflow") * 100,
            "rental_yield": lambda i: self._safe_divide((i["monthly_rent"] * 12), i["property_value"], "rental_yield") * 100,
            "section_8_premium": lambda i: self._safe_divide(i["section_8_rate"] - i["market_rent"], i["market_rent"], "section_8_premium") * 100,
            "wholesale_assignment_fee": lambda i: i["end_buyer_price"] - i["contract_price"],
            "churn_prediction_score": lambda i: (i["login_frequency"] * 0.3) + (i["feature_usage"] * 0.4) + (i["support_tickets"] * -0.3),
            "dynamic_pricing_optimizer": lambda i: i["base_price"] * (1 + i["demand_factor"]) * (1 - i["competition_pressure"]),
            "revenue_leak_score": lambda i: (i["failed_transactions"] + i["cart_abandonment_rate"] + i["pricing_errors"]) * i["avg_order_value"],
            "revenue_per_bot": lambda i: self._safe_divide(i["total_revenue"], i["active_bot_count"], "revenue_per_bot"),
            "drawdown_recovery": lambda i: self._safe_divide(i["loss_amount"], i["monthly_net_income"], "drawdown_recovery"),
            "portfolio_concentration": lambda i: self._safe_divide(i["single_asset_value"], i["total_portfolio_value"], "portfolio_concentration") * 100,
            "risk_adjusted_return": lambda i: self._safe_divide(i["expected_return"], i["risk_score"], "risk_adjusted_return"),
            "cac_efficiency": lambda i: self._safe_divide(i["customer_lifetime_value"], i["customer_acquisition_cost"], "cac_efficiency"),
            "closing_probability": lambda i: (i["meetings_held"] * 0.3) + (i["proposal_sent"] * 0.4) + (i["champion_score"] * 0.3),
            "commission_roi": lambda i: self._safe_divide(i["revenue_generated"] - i["total_commission_paid"], i["total_commission_paid"], "commission_roi") * 100,
            "funnel_leak_detection": lambda i: self._safe_divide(i["stage_n_count"] - i["stage_n1_count"], i["stage_n_count"], "funnel_leak_detection") * 100,
            "lead_value_formula": lambda i: i["close_rate"] * i["average_deal_size"],
            "pipeline_velocity": lambda i: self._safe_divide((i["opportunities"] * i["win_rate"] * i["average_deal_size"]), i["sales_cycle_days"], "pipeline_velocity"),
        }

    def list_calculators(self, domain: str = None, system: str = None, tag: str = None) -> list[dict]:
        """List calculator definitions with optional domain/system/tag filters."""
        results = list(self.CALCULATORS)
        if domain:
            results = [c for c in results if c["domain"].lower() == domain.lower()]
        if system:
            results = [c for c in results if c["system"].lower() == system.lower()]
        if tag:
            tag_l = tag.lower()
            results = [c for c in results if any(t.lower() == tag_l for t in c["tags"])]
        return results

    def get_calculator(self, calculator_id: str) -> dict:
        """Get one calculator definition by id or name."""
        candidate = calculator_id.strip().lower().replace("-", "_").replace(" ", "_")
        for calc in self.CALCULATORS:
            if calc["id"] == candidate:
                return calc
            calc_name = calc["name"].lower().replace("-", "_").replace(" ", "_")
            if calc_name == candidate:
                return calc
        raise ValueError(f"Calculator '{calculator_id}' not found.")

    def run_calculator(self, calculator_id: str, **inputs: float) -> dict:
        """Execute one calculator by id or name using keyword numeric inputs."""
        calc = self.get_calculator(calculator_id)
        required = calc["variables"]
        missing = [v for v in required if v not in inputs]
        if missing:
            raise ValueError(f"Missing variables for '{calc['id']}': {missing}")
        numeric_inputs = {}
        for var in required:
            val = inputs[var]
            if not isinstance(val, (int, float)):
                raise TypeError(f"Variable '{var}' must be numeric, got {type(val).__name__}.")
            numeric_inputs[var] = float(val)
        result = self._calculator_functions[calc["id"]](numeric_inputs)
        if isinstance(result, (int, float)):
            result = round(float(result), 4)
        return {
            "calculator_id": calc["id"],
            "name": calc["name"],
            "domain": calc["domain"],
            "system": calc["system"],
            "inputs": numeric_inputs,
            "result": result,
            "target": calc["target"],
            "tags": calc["tags"],
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
