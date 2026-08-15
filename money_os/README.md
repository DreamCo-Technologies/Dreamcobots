# DreamCo Money OS

A revenue-opportunity discovery layer for DreamCo. It combines deal/price-drop discovery, coupon stacking, receipt analysis, resale/flip analysis, settlement/class-action discovery, grants/contracts, lead generation, jobs/gigs, and revenue tracking.

## Safety and accuracy
- No fabricated live deals, payouts, lawsuits, prices, or earnings are bundled.
- External sources must be connected through approved APIs, feeds, affiliate programs, or compliant browser integrations.
- Receipt and settlement submissions require user confirmation unless a source explicitly provides an authorized API and permits automation.
- Profit is an estimate until price, fees, inventory, eligibility, and payout are verified.
- Never store payment credentials, claim passwords, or secrets in Git.

## Components
- `backend/` — Node.js opportunity engine and REST API.
- `config/bot_registry.json` — revenue lanes for the existing DreamCo bot ecosystem.
- `data/opportunity_sources.json` — source registry; intentionally no fake live deals.
- `automation/workflows.json` — scheduler/event contract for hourly discovery and validation.
- `frontend/README.md` — FlutterFlow screen/data contract.
- `docs/launch.md` — deployment, monetization, compliance, and launch checklist.

## Run locally
```bash
cd money_os/backend
npm install
npm start
```

Environment variables are documented in `backend/.env.example`. The default mode is dry-run so the system cannot accidentally publish unverified opportunities.

## Production principle
Discovery -> normalize -> verify -> score -> monetize -> alert -> user action -> outcome tracking.
