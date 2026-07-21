# Public Lead Engine Bot

**DreamCo CineCore™ — Legal Public Business Search Mode**

The legal public lead search engine for DreamCo CineCore™. Uses official public
APIs (Google Places API, Yelp Fusion) to discover businesses, filters for those
with low ratings and weak marketing presence, and generates commercial opportunities.

> ⚖️ **Compliance First:** This bot only uses public, opt-in business data from
> official APIs. All outreach messages are generated as **drafts for human review**
> before sending — never sent automatically. Fully compliant with CAN-SPAM, GDPR,
> and API terms of service.

---

## What It Does

1. **Searches official directories** via Google Places API and Yelp Fusion API
2. **Filters by low ratings** — targets businesses ≤ 3.5 stars (most in need of marketing help)
3. **Detects weak marketing** — no website, no social presence, few reviews
4. **Scores ad opportunity** — AI ranks businesses by commercial potential
5. **Generates targeted scripts** — custom commercial copy per business
6. **Drafts outreach messages** — human-reviewed pitch messages
7. **Exports to CRM** — push qualified leads to any CRM system

---

## Quick Start

```python
from bots.public_lead_engine import PublicLeadEngine, DataSource, Tier

# Initialize
engine = PublicLeadEngine(tier=Tier.PRO)

# Step 1: Search Google Places for restaurants with low ratings
result = engine.search_businesses(
    query="restaurant Austin TX",
    count=20,
    source=DataSource.GOOGLE_PLACES,
    max_rating=3.5  # Only businesses rated 3.5 stars or below
)
print(f"Found {result['new_leads']} businesses")

# Step 2: Also search Yelp (PRO+)
yelp_result = engine.search_businesses(
    query="local services",
    count=10,
    source=DataSource.YELP,
    max_rating=4.0
)

# Step 3: Filter for weak marketing signals
filtered = engine.filter_weak_marketing(max_rating=3.5, min_weakness_score=30.0)
print(f"Kept {filtered['kept']} high-opportunity leads")

# Step 4: Compute ad opportunity scores
scored = engine.compute_ad_scores()

# Step 5: Generate targeted ad scripts
scripts = engine.generate_scripts(top_n=10)
print(f"Generated {scripts['scripts_generated']} scripts")

# Step 6: Draft outreach messages (requires human review)
outreach = engine.generate_outreach()
print(f"Drafted {outreach['outreach_drafts_generated']} messages")
print(f"Human approval required: {outreach['requires_human_approval']}")

# Export to CRM
export = engine.export_to_crm("Salesforce")
print(f"Exported {export['leads_exported']} leads")
```

---

## Standalone Entry Point

Run the bot directly:

```bash
python bots/public_lead_engine/public_lead_engine.py
```

---

## Tiers

| Tier | Price | Searches/Day | Features |
|------|-------|-------------|---------|
| **FREE** | $0 | 50 | Google Places search, rating filter |
| **PRO** | $39/mo | 1,000 | + Yelp search, weak marketing filter, ad scoring, scripts, outreach drafts, CRM export |
| **ENTERPRISE** | $149/mo | Unlimited | + Multi-API (Bing, Foursquare), AI opportunity scoring, bulk search, analytics, white-label |

---

## API Reference

### `search_businesses(query, count, source, max_rating)` *(FREE+)*
Search Google Places (FREE), Yelp (PRO+), or other APIs (ENTERPRISE) for businesses.
Set `max_rating` (PRO+) to filter by star rating automatically.

### `search_all_sources(query, leads_per_source)` *(PRO+)*
Search all available API sources in one call.

### `filter_weak_marketing(max_rating, min_weakness_score)` *(PRO+)*
Filter leads to only those with weak marketing:
- Low star ratings (≤ 3.5 by default)
- Few reviews
- No website
- No social media presence

### `score_opportunities()` *(ENTERPRISE+)*
AI-score filtered leads by ad opportunity (0–100).

### `compute_ad_scores()` *(PRO+)*
Compute basic ad opportunity scores for filtered leads.

### `generate_scripts(top_n)` *(PRO+)*
Generate targeted commercial scripts for the highest-opportunity leads.

### `generate_outreach()` *(PRO+)*
Generate human-readable outreach message drafts. **Always requires human review before sending.**

### `bulk_search(queries, leads_per_query)` *(ENTERPRISE+)*
Run multiple search queries across all sources at once.

### `export_to_crm(crm_name)` *(PRO+)*
Export outreach-ready leads to a CRM.

### `get_low_rated_businesses(max_rating)`
Return all businesses at or below the specified star rating, sorted by rating.

### `get_top_opportunities(n)`
Return top N leads by ad opportunity score.

### `get_summary()`
Statistics: total leads, by status/source/category, avg star rating.

### `get_analytics()` *(ENTERPRISE+)*
Extended analytics with search log and CRM export history.

### `chat(message)` / `process(payload)`
Natural-language + GLOBAL AI SOURCES FLOW interface.

---

## Supported API Sources

| Source | Tier | Description |
|--------|------|-------------|
| `GOOGLE_PLACES` | FREE+ | Google Places API — local business search |
| `YELP` | PRO+ | Yelp Fusion API — ratings, reviews, contact info |
| `BING_LOCAL` | ENTERPRISE | Bing Local Search API |
| `FOURSQUARE` | ENTERPRISE | Foursquare Places API |

### Production API Integration

Replace `_simulate_api_search()` in `public_lead_engine.py` with real API calls:

**Google Places:**
```python
import requests

def search_google_places(query, api_key, count=10, max_rating=None):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": api_key}
    response = requests.get(url, params=params)
    results = response.json().get("results", [])[:count]
    if max_rating:
        results = [r for r in results if r.get("rating", 5) <= max_rating]
    return results
```

**Yelp Fusion:**
```python
import requests

def search_yelp(query, api_key, location="", count=10, max_rating=None):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"term": query, "location": location, "limit": count}
    response = requests.get(url, headers=headers, params=params)
    results = response.json().get("businesses", [])
    if max_rating:
        results = [r for r in results if r.get("rating", 5) <= max_rating]
    return results
```

---

## Compliance Notes

This bot is designed for **legal, ethical lead generation**:

1. ✅ Only queries **public, opt-in** business listings via official APIs
2. ✅ Outreach drafts require **human review** before sending
3. ✅ No automated mass messaging
4. ✅ Compliant with CAN-SPAM Act, GDPR, and API terms of service
5. ✅ Businesses listed in public directories have consented to be discoverable

---

## Running Tests

```bash
python -m pytest tests/test_public_lead_engine.py -v
```

---

## CineCore System Integration

This bot integrates with the full CineCore pipeline:

- **Script Engine** → generated scripts feed directly into ad production
- **Video Engine** → scene breakdowns ready for Runway / Pika AI video generation
- **Outreach Engine** → human-approved messages ready for email/CRM
- **CRM** → auto-export qualified leads
- **Stripe Billing** → charge clients via `BillingEngine` after deal close
- **BuddyAI** → fully routable via the `chat()` interface
