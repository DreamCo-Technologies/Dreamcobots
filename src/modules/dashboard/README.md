# Module 4: Empire Dashboard

## Overview
Central control center displaying real-time stats on leads, deals, revenue, and bot activity.

## Planned Features
- Live stats: leads found today, deals identified, revenue generated
- Bot status monitoring (active/idle/error)
- Alert system for hot leads and hot deals
- Revenue tracking and projections

## Architecture
```
Dashboard
  ├── components/    # React UI components
  │   ├── LeadStats.jsx
  │   ├── DealStats.jsx
  │   ├── RevenueChart.jsx
  │   ├── BotStatus.jsx
  │   └── AlertFeed.jsx
  ├── api/           # API calls to backend
  ├── hooks/         # Custom React hooks for data fetching
  └── index.js       # Module entry point
```

## Key Panels
- 🔥 **HOT LEADS** — leads with score > 70 from the Lead Scraper
- 🏠 **HOT DEALS** — real estate deals with profit > $30K
- 💰 **MONEY TODAY** — revenue closed today via Outreach Bot
- 🤖 **BOT STATUS** — real-time status of all running bots
