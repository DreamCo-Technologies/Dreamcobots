# 🤖 SaaS Selling Bot

> The ultimate autonomous SaaS selling bot – discover, compare, and sell 200+ free SaaS tools with AI-powered recommendations, affiliate tracking, and subscription monetisation.

---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Database](#database)
7. [AI Integration](#ai-integration)
8. [Payment Gateways](#payment-gateways)
9. [Affiliate & Revenue Tracking](#affiliate--revenue-tracking)
10. [Frontend](#frontend)
11. [Adding More Tools](#adding-more-tools)
12. [Contributing](#contributing)

---

## Overview

SaaSBot is a fully autonomous SaaS selling platform that:

- **Lists 200+ free SaaS tools** across 6 categories (Analytics, Marketing, Development, Collaboration, Finance, AI)
- **Provides a REST API** for searching, filtering, and managing tools
- **Integrates AI** (OpenAI GPT) for personalised tool recommendations and chatbot support
- **Tracks affiliate links** and commission revenue
- **Handles subscriptions** via Stripe for the Pro and Enterprise tiers
- **Serves a professional responsive UI** out of the box

---

## Features

| Feature | Status |
|---|---|
| 200+ free SaaS tools database | ✅ |
| REST API (search, filter, CRUD) | ✅ |
| Category management | ✅ |
| AI recommendations (OpenAI GPT) | ✅ |
| Chatbot interface | ✅ |
| Affiliate link tracking | ✅ |
| Revenue & conversion dashboard | ✅ |
| Stripe subscription payments | ✅ |
| Free / Pro / Enterprise plans | ✅ |
| Responsive professional UI | ✅ |
| Extensible tool database | ✅ |

---

## Quick Start

### 1. Clone and navigate
```bash
git clone https://github.com/ireanjordan24/Dreamcobots.git
cd Dreamcobots/bots/saas-selling-bot
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)
```bash
export OPENAI_API_KEY="sk-..."           # Enable AI recommendations
export STRIPE_SECRET_KEY="sk_test_..."  # Enable paid subscriptions
export PORT=5000                         # Default port
```

Or copy `config.json` and fill in your API keys (the app reads `config.json` as a fallback).

### 5. Initialise the database
```bash
python bot.py --init-db
```

### 6. Run the server
```bash
python bot.py
```

Visit **http://localhost:5000** to open the UI.

### 7. Run the demo (no server)
```bash
python bot.py --demo
```

---

## Configuration

The bot reads configuration from environment variables first, then `config.json`.

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key for AI features | — |
| `STRIPE_SECRET_KEY` | Stripe secret key for payments | — |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | — |
| `STRIPE_PRO_PRICE_ID` | Stripe Price ID for Pro plan | placeholder |
| `STRIPE_ENTERPRISE_PRICE_ID` | Stripe Price ID for Enterprise plan | placeholder |
| `STRIPE_SUCCESS_URL` | Redirect URL after successful payment | `http://localhost:5000/payment/success` |
| `STRIPE_CANCEL_URL` | Redirect URL after cancelled payment | `http://localhost:5000/payment/cancel` |
| `PORT` | Server port | `5000` |
| `DEBUG` | Enable Flask debug mode | `false` |

---

## API Reference

All endpoints return JSON. Base URL: `http://localhost:5000`

### Tools

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tools` | List all tools. Filter with `?category=Analytics` |
| `GET` | `/api/tools/<id>` | Get a single tool by ID |
| `POST` | `/api/tools` | Add a new tool |
| `GET` | `/api/categories` | List all categories with tool counts |
| `GET` | `/api/search?q=<query>` | Full-text search across name, description, category |

**POST `/api/tools` body:**
```json
{
  "name": "My Tool",
  "category": "Analytics",
  "description": "A great tool for analytics.",
  "api_url": "https://api.mytool.com",
  "pricing": "Free – 1000 events/month",
  "affiliate_link": "https://mytool.com",
  "docs_url": "https://docs.mytool.com"
}
```

### Subscriptions & Plans

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/plans` | List all subscription plans |
| `POST` | `/api/subscribe` | Subscribe with email and plan |

**POST `/api/subscribe` body:**
```json
{ "email": "user@example.com", "plan": "free" }
```
Plans: `free`, `pro`, `enterprise`

### AI & Chat

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/recommend` | AI-powered tool recommendations |
| `POST` | `/api/chat` | Multi-turn chatbot conversation |

**POST `/api/recommend` body:**
```json
{ "query": "best tools for email marketing", "context": {} }
```

**POST `/api/chat` body:**
```json
{
  "message": "What are the best free analytics tools?",
  "history": [
    { "role": "user", "content": "Hi!" },
    { "role": "assistant", "content": "Hello! How can I help?" }
  ]
}
```

### Affiliate & Revenue

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/affiliate/click/<id>` | Track a click and redirect to affiliate URL |
| `POST` | `/api/affiliate/convert/<id>` | Mark a conversion with commission |
| `GET` | `/api/revenue` | Revenue dashboard (total, clicks, conversions) |

### Webhooks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/webhook/stripe` | Stripe webhook handler |

---

## Database

The SQLite database (`saas_tools.db`) is created automatically on first run.

### Tables

| Table | Description |
|---|---|
| `tools` | 200+ SaaS tools with name, category, description, API URL, pricing, affiliate link |
| `subscriptions` | User email, plan, and Stripe customer ID |
| `affiliate_clicks` | Tracks every affiliate link click with session ID |
| `revenue` | Records all revenue events (subscriptions, commissions) |

### Categories and Tool Counts

| Category | Tools |
|---|---|
| Analytics | 35 |
| Marketing | 35 |
| Development | 35 |
| Collaboration | 35 |
| Finance | 30 |
| AI | 30 |

---

## AI Integration

The bot uses **OpenAI GPT-4o-mini** by default for:

- **Personalised recommendations** (`/api/recommend`) – analyses user needs and suggests the best matching tools from the 200-tool catalogue
- **Multi-turn chatbot** (`/api/chat`) – maintains conversation history and provides contextual tool guidance

**Fallback mode**: When `OPENAI_API_KEY` is not configured, the bot falls back to rule-based keyword matching to provide recommendations.

---

## Payment Gateways

The bot uses **Stripe Checkout** for subscription payments:

1. User visits `/api/subscribe` with email and plan
2. Stripe Checkout session is created and user is redirected
3. On payment success, Stripe sends a webhook to `/api/webhook/stripe`
4. User subscription is recorded in the database

### Setting up Stripe

1. Create products and prices at [dashboard.stripe.com/products](https://dashboard.stripe.com/products)
2. Copy the Price IDs into `STRIPE_PRO_PRICE_ID` and `STRIPE_ENTERPRISE_PRICE_ID`
3. Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`
4. Configure webhook endpoint in Stripe dashboard pointing to `/api/webhook/stripe`

---

## Affiliate & Revenue Tracking

Every "Get Tool" click passes through `/api/affiliate/click/<tool_id>`, which:

1. Records the click with session ID and timestamp in `affiliate_clicks`
2. Redirects the user to the tool's affiliate link

Conversions can be marked via `/api/affiliate/convert/<tool_id>` with a commission amount, which:

1. Updates the click record as converted
2. Records revenue in the `revenue` table

View the revenue dashboard at `/api/revenue`.

---

## Frontend

The frontend is a single-page app served from the `frontend/` directory:

| File | Description |
|---|---|
| `frontend/index.html` | Main HTML structure |
| `frontend/style.css` | Responsive CSS with design system |
| `frontend/app.js` | JavaScript for API calls, rendering, chat, and modals |

### Key UI Components

- **Hero section** – overview stats and call-to-action
- **Category browser** – click to filter by category
- **Tools grid** – paginated card list with search and sort
- **Pricing section** – three-tier plan comparison
- **AI Chat** – real-time chatbot with conversation history
- **Subscribe modal** – plan selection and email sign-up
- **Tool detail modal** – expanded tool information

---

## Adding More Tools

To add tools to the database programmatically:

```python
from database import add_tool, init_db

init_db()
add_tool({
    "name": "My New Tool",
    "category": "Analytics",
    "description": "Short description of what the tool does.",
    "api_url": "https://api.mytool.com",
    "pricing": "Free – 1000 events/month",
    "affiliate_link": "https://mytool.com?ref=saasbot",
    "docs_url": "https://docs.mytool.com"
})
```

Or via the API:
```bash
curl -X POST http://localhost:5000/api/tools \
  -H "Content-Type: application/json" \
  -d '{"name":"My Tool","category":"AI","description":"AI tool","pricing":"Free"}'
```

Valid categories: `Analytics`, `Marketing`, `Development`, `Collaboration`, `Finance`, `AI`

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/add-new-saas-tools`
3. Add tools to `SAAS_TOOLS` list in `database.py`
4. Run the demo to verify: `python bot.py --demo`
5. Submit a pull request with a description of the tools added

---

## License

Part of the [DreamCObots](https://github.com/ireanjordan24/Dreamcobots) project.
