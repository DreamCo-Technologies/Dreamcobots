# Module 3: Real Estate Deal Finder

## Overview
Finds undervalued properties by analyzing market data, foreclosures, and tax liens. Calculates profit potential for each deal.

## Planned Features
- Pull property data from Zillow, foreclosure databases, tax lien records
- Detect properties below market value and motivated sellers
- Auto-calculate:
  - ARV (After Repair Value)
  - Rehab cost estimates
  - Net profit margin
- Mark deals with profit > $30,000 as "hot deals"

## Architecture
```
RealEstateDealFinder
  ├── sources/       # Zillow API, foreclosure scrapers, tax lien feeds
  ├── analysis/      # ARV calculation, profit formula
  ├── scoring/       # Deal scoring and hot deal detection
  ├── storage/       # Persist deals to database
  └── index.js       # Module entry point
```

## Deal Formula
```
HOT_DEAL_THRESHOLD = $30,000  # configurable minimum net profit

profit = arv - purchase_price - rehab_cost
if profit > HOT_DEAL_THRESHOLD → HOT DEAL
```

## Monetization
- Flip houses for profit
- Wholesale deals ($5K–$25K per deal)
