# LeadGenBot

Identifies and returns qualified prospects for the DreamCo sales pipeline.

## Overview

LeadGenBot is the entry point of the revenue pipeline. It generates a list of
business leads that are passed downstream to the EnrichmentBot, OutreachBot,
FollowUpBot, and CloserBot.

## Usage

```python
from bots.LeadGenBot.main import get_leads

leads = get_leads()
```

## Integration

Replace the mock data in `main.py` with real API integrations:

- **Google Maps** — local business discovery
- **LinkedIn / Apollo** — B2B lead sourcing
- **Facebook Marketplace** — real estate, vehicles

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — `get_leads()` |
| `config.json` | Bot configuration |
| `metrics.py` | Activity tracking |
| `README.md` | This file |
