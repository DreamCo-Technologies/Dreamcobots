# AI Enablement Hub

Revived from PR #344. Provides centralized AI model routing, prompt registry, and per-tier usage metering for every DreamCo bot.

## Endpoints
- `POST /v1/complete` — tier-gated chat completion
- `GET /v1/prompts/:slug` — fetch a registered prompt
- `GET /v1/usage` — current account usage and remaining quota
