# DreamCo Customer Production Runbook

Use this runbook before putting DreamCo/Buddy in front of customers. The repository can prove code readiness, but customer readiness also requires live infrastructure, real secrets, and smoke tests on the deployment host.

## Required Architecture

- `website/` and GitHub Pages are the public control surface and marketing/dashboard shell.
- The Express API must run on a backend host that supports Node.js, outbound HTTPS, and long-running server processes.
- Postgres is required for production bot, customer, subscription, chat, and tracking data.
- Stripe live mode is required for paid customer flows.
- Secrets must live in the production host or GitHub Actions secrets, never in static files.

## Production Secrets

Configure these in the backend host:

| Secret | Purpose |
|---|---|
| `DATABASE_URL` | Production Postgres connection string |
| `STRIPE_SECRET_KEY` or `STRIPE_LIVE_SECRET_KEY` | Stripe server-side billing |
| `STRIPE_PUBLISHABLE_KEY` or `STRIPE_LIVE_PK` | Stripe checkout/client setup |
| `STRIPE_WEBHOOK_SECRET` | Verifies Stripe webhook events |
| `AI_INTEGRATIONS_OPENAI_API_KEY` or `OPENAI_API_KEY` | Enables real model calls |
| `GITHUB_TOKEN` | Optional governed GitHub sync to review branches |

## Preflight Commands

Run these before deployment:

```bash
npm run production:readiness
npm run buddy:laptop:check
npm run buddy:site:check
npm run check
```

For a strict code contract gate:

```bash
npm run production:readiness:strict
```

## Live Smoke Tests

After deploying the backend, verify:

| Route | Expected result |
|---|---|
| `GET /api/health` | `ok: true`, production environment, DB and Stripe flags accurate |
| `GET /api/ready` | HTTP 200 only when DB, Stripe secret, and webhook secret are configured |
| `GET /api/stripe/subscription-status` | Returns real customer entitlement or a clear unauthenticated state |
| `POST /api/stripe/webhook` | Rejects unsigned events and accepts valid Stripe CLI/dashboard events |
| `/buddy` | Loads the customer dashboard without exposing secrets |

## Customer Launch Rule

Do not call the platform customer-ready until:

1. GitHub Actions production readiness evidence has uploaded a fresh report.
2. The backend host has real production secrets configured.
3. Postgres migrations or `npm run db:push` have completed against the production database.
4. Stripe live checkout, portal, and webhook events pass a live smoke test.
5. `/api/ready` returns HTTP 200 on the production backend.
6. At least one real customer workflow has been tested end to end: sign in, choose plan, pay, open Buddy, run a permitted action, and view tracking evidence.
