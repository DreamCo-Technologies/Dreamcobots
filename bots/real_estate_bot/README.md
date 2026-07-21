# Real Estate Bot

Tier-aware real estate deal finder, ROI analyzer, and **Housing + Government Contract engine**.
Finds distressed properties, matches them to government housing programs, calculates monthly
revenue, and automates outreach to property owners and housing departments.

## Engines

| Engine | Description |
|--------|-------------|
| Property Acquisition Bot | Find foreclosures, tax sales, and abandoned homes |
| Government Contract Bot | Discover HUD, SAM.gov, and Grants.gov housing programs |
| Revenue Matching Engine | Match property → program → monthly income |
| Outreach Bot | Generate (and auto-send on ENTERPRISE) messages to owners & agencies |

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Locations | 1 | 10 | Unlimited |
| Market trends | ✗ | ✓ | ✓ |
| AI Valuation | ✗ | ✗ | ✓ |
| Predictive analytics | ✗ | ✗ | ✓ |
| Distressed property search | 3 results | ✓ full | ✓ full + filters |
| Housing revenue calculator | ✓ | ✓ | ✓ |
| Gov housing program finder | ✗ | ✓ (5 results) | ✓ unlimited |
| Property-to-program matching | ✗ | ✓ | ✓ + AI strategy |
| Outreach generator | ✗ | ✓ (generate) | ✓ (auto-send) |

## Usage

```python
from bots.real_estate_bot.real_estate_bot import RealEstateBot
from tiers import Tier

bot = RealEstateBot(tier=Tier.PRO)

# --- Classic deal-finding ---
deals = bot.search_deals("austin", budget=400000)
evaluation = bot.evaluate_property("1204 Oak Blvd, Austin TX")
roi = bot.estimate_roi(deals[0])
trends = bot.get_market_trends("phoenix")

# --- Housing + Gov Contract System ---
# 1. Find cheap distressed properties
distressed = bot.find_distressed_properties(state="MI", max_price=20000)

# 2. Find government housing programs
programs = bot.find_gov_housing_programs(category="emergency_housing")

# 3. Calculate revenue
revenue = bot.calculate_housing_revenue(beds=5, program_id="GHP001")
# → $3,400/month net on a 5-bedroom with HUD Emergency Vouchers

# 4. Match a specific property to the best program
match = bot.match_property_to_program("DP001")

# 5. Generate outreach messages
outreach = bot.send_outreach(
    "housing_department",
    address="312 Elmwood St, Milwaukee WI",
    program_name="HUD Emergency Voucher",
    unit_count=3,
    beds=3,
)
```

## Revenue Model Example

```
5-bedroom distressed property (acquired for $18,500)
→ Matched to HUD Emergency Housing Voucher ($850/person/month)
→ 5 tenants × $850 = $4,250/month gross
→ $3,400/month net (after 20% operating costs)
→ Payback in ~5.4 months
```

## Methods

- `search_deals(location, budget)` — returns properties under budget
- `evaluate_property(address)` — returns valuation and cash flow analysis
- `estimate_roi(property)` — returns estimated annual ROI percentage
- `get_market_trends(location)` — returns price trends and inventory data (PRO+)
- `find_distressed_properties(state, city, max_price, property_type)` — foreclosures, tax sales, abandoned homes
- `find_gov_housing_programs(state, category, portal)` — HUD / SAM.gov / Grants.gov programs (PRO+)
- `calculate_housing_revenue(beds, program_id)` — projected monthly government-paid income
- `match_property_to_program(property_id)` — best-program match with payback projection (PRO+)
- `send_outreach(contact_type, address, ...)` — outreach messages for owners and agencies (PRO+)

## Directory Structure

```
bots/real_estate_bot/
├── real_estate_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
