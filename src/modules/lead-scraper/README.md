# Module 1: Local Business Lead Scraper

## Overview
Finds local businesses that need marketing, websites, or SEO services and scores them as leads.

## Planned Features
- Scrape Google Maps, Yelp, and Facebook Pages for local businesses
- Detect missing signals: no website, poor reviews, no social presence
- Score leads based on opportunity (0–100):
  - +50 if no website
  - +30 if rating < 3.5
  - +20 if no Instagram/social presence
- Mark leads with score > 70 as "hot leads"

## Architecture
```
LeadScraper
  ├── sources/       # Google Maps, Yelp, Facebook scrapers
  ├── scoring/       # Lead scoring logic
  ├── storage/       # Persist leads to database
  └── index.js       # Module entry point
```

## Monetization
- Sell websites to hot leads ($500–$3,000)
- Monthly SEO retainers ($100–$1,000/mo)
