# Lead Generator Bot

Tier-aware business lead discovery, scoring, and export bot.

## Features by Tier

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Leads per month | 10 | 100 | Unlimited |
| Contact info | Basic | + Verified emails & phones | Full enrichment |
| Industries | 2 | 10 | All |
| Lead scoring | ✗ | ✓ | ✓ + Predictive |
| CRM export (CSV) | ✗ | ✓ | ✓ |
| Company intelligence | ✗ | ✗ | ✓ |

## Usage

```python
from bots.lead_generator_bot import LeadGeneratorBot
from bots.ai-models-integration.tiers import Tier

bot = LeadGeneratorBot(tier=Tier.PRO)
leads = bot.search_leads(industry="tech", location="San Francisco")
scored = bot.score_lead(leads[0])
csv_data = bot.export_to_csv(leads)
```
