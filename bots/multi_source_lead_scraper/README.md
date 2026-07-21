# Multi-Source Lead Scraper

Empire-grade lead generation engine that scrapes qualified leads from
multiple data sources, validates, enriches, AI-scores, and exports them.

## Sources

| Source   | Tier Required |
|----------|---------------|
| Google   | FREE          |
| LinkedIn | PRO           |
| Twitter  | PRO           |
| Reddit   | PRO           |
| Yelp     | PRO           |
| Custom   | PRO           |

## Tiers

| Tier       | Price    | Leads/Day | Sources |
|------------|----------|-----------|---------|
| FREE       | $0/mo    | 50        | 2       |
| PRO        | $49/mo   | 5,000     | 10      |
| ENTERPRISE | $199/mo  | Unlimited | All     |

## Quick Start

```python
from bots.multi_source_lead_scraper import MultiSourceLeadScraper, LeadSource, Tier

scraper = MultiSourceLeadScraper(tier=Tier.PRO)

# Scrape leads
result = scraper.scrape(LeadSource.LINKEDIN, count=50, industry_filter="SaaS")
print(result)

# Scrape all available sources
all_results = scraper.scrape_all_sources(leads_per_source=20)

# Validate + enrich + AI score
scraper.validate_leads()
scraper.enrich_leads()
scraper.score_leads()  # ENTERPRISE only

# Get top leads
top = scraper.get_top_leads(n=10)

# Export to CRM
scraper.export_to_crm("HubSpot")

# Summary
print(scraper.get_summary())
```

## Running Tests

```bash
python -m pytest tests/test_multi_source_lead_scraper.py -v
```
