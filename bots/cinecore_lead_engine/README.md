# CineCore Lead Engine Bot

**DreamCo CineCore™ — Original Lead Engine**

The classic DreamCo CineCore lead-generation engine. This is the *original* standalone bot
that powers the DreamCo CineCore™ commercial creation system.

---

## What It Does

The CineCore Lead Engine autonomously:

1. **Scans businesses** from multiple internal and simulated public sources
2. **Scores leads** by commercial opportunity (ad potential, niche, marketing weakness)
3. **Generates ad scripts** — compelling 15–60 second commercial copy
4. **Drafts outreach messages** — personalized pitch messages for each lead
5. **Builds ad packages** — full scene-by-scene commercial concepts
6. **Exports to CRM** — pushes qualified leads to any CRM system

---

## Quick Start

```python
from bots.cinecore_lead_engine import CineCoreLeadEngine, BusinessNiche, Tier

# Initialize the engine
engine = CineCoreLeadEngine(tier=Tier.PRO)

# Step 1: Scan for business leads
result = engine.scan_businesses(count=20)
print(f"Found {result['new_leads']} leads")

# Step 2: Score by opportunity
scored = engine.score_leads()
print(f"Scored {scored['scored']} leads")

# Step 3: Generate ad scripts
scripts = engine.generate_scripts(top_n=10)
print(f"Generated {scripts['scripts_generated']} scripts")

# Step 4: Build outreach drafts
outreach = engine.generate_outreach()
print(f"Drafted {outreach['outreach_drafts_generated']} messages")

# Step 5: Export to CRM
export = engine.export_to_crm("HubSpot")
print(f"Exported {export['leads_exported']} leads to {export['crm']}")
```

---

## Standalone Entry Point

Run the bot directly:

```bash
python bots/cinecore_lead_engine/cinecore_lead_engine.py
```

---

## Tiers

| Tier | Price | Leads/Day | Features |
|------|-------|-----------|---------|
| **FREE** | $0 | 100 | Business scan, script generation |
| **PRO** | $29/mo | 2,000 | + Lead scoring, outreach drafts, CRM export, niche filter, ad packages |
| **ENTERPRISE** | $99/mo | Unlimited | + Bulk generation, advanced analytics, white-label |

---

## Full API Reference

### `scan_businesses(count, niche_filter)`
Scan for raw business leads. `niche_filter` (PRO+) restricts by `BusinessNiche`.

### `score_leads()` *(PRO+)*
Rank leads 0–100 by commercial opportunity.

### `generate_scripts(top_n)` *(FREE+)*
Generate ad scripts for the top `top_n` leads.

### `generate_outreach()` *(PRO+)*
Create personalized pitch message drafts.

### `build_ad_packages()` *(PRO+)*
Build full commercial concept packages (scenes, platforms, visuals).

### `bulk_generate(business_list)` *(ENTERPRISE+)*
Mass-generate scripts and outreach for a list of business names.

### `export_to_crm(crm_name)` *(PRO+)*
Export outreach-ready leads to a CRM system.

### `get_top_leads(n)`
Return the top N leads by opportunity score.

### `get_summary()`
Return statistics: total leads, by status, by niche, avg opportunity score.

### `get_analytics()` *(ENTERPRISE+)*
Return extended analytics including top leads and CRM export log.

### `chat(message)` / `process(payload)`
Natural-language + GLOBAL AI SOURCES FLOW interface.

---

## Available Niches

`RESTAURANT`, `REAL_ESTATE`, `AUTO_DEALER`, `ROOFING`, `PLUMBING`,
`ECOMMERCE`, `RETAIL`, `HEALTH_WELLNESS`, `FITNESS`, `LEGAL`, `DENTAL`,
`SALON`, `GENERAL`

---

## Integration with DreamCo CineCore™

This bot integrates with the full CineCore system:

- **Script Engine** → feeds generated scripts to the video production pipeline
- **Ad Package Builder** → scene breakdowns ready for Runway/Pika AI video
- **CRM** → auto-pushes qualified leads for follow-up
- **Stripe Billing** → auto-charge closed clients via `BillingEngine`
- **BuddyAI** → routable via the `chat()` interface

---

## Running Tests

```bash
python -m pytest tests/test_cinecore_lead_engine.py -v
```

---

## Pricing Model

| Package | Price |
|---------|-------|
| Basic Ad | $50–$150 |
| Pro Commercial | $300–$1,000 |
| Monthly Ads Package | $500–$5,000 |
| Affiliate Ads | Passive income |
