# EnrichmentBot

Assigns qualification scores and enriches leads with additional context data.

## Overview

EnrichmentBot sits between LeadGenBot and OutreachBot in the sales pipeline.
It adds a `score` and `needs` field to every lead so that downstream bots can
personalise outreach and prioritise high-value targets.

## Usage

```python
from bots.EnrichmentBot.main import enrich

enriched_lead = enrich(raw_lead)
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — `enrich(lead)` |
| `config.json` | Bot configuration |
| `metrics.py` | Activity tracking |
| `README.md` | This file |
