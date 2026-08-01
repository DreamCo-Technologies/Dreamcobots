# DreamCo Empire OS - Bot Registry

[![Bots](https://img.shields.io/badge/bots-1051+-blue)](App_bots/)
[![Divisions](https://img.shields.io/badge/divisions-45-purple)](App_bots/)
[![Autonomy](https://img.shields.io/badge/autonomy-governed-green)](docs/)

DreamCo is a governed AI workbench with 1,051 specialist profiles across 45 divisions. Buddy routes requests, prepares testable task packets, and pauses before external writes, publishing, outreach, account changes, or spending.

## 🗂️ Directory Structure

```
Dreamcobots/
├── App_bots/          # All 1051 bots organized by division (JSON)
├── bots/              # Specialty & elite bot profiles (Markdown)
├── website/           # 26-page standalone HTML/CSS website
│   ├── index.html     # Landing page
│   ├── dashboard.html
│   ├── bots.html
│   ├── buddy.html
│   ├── chat.html
│   ├── divisions.html
│   ├── autonomy.html
│   ├── deals.html     # Real estate & car flip calculators
│   ├── settings.html
│   ├── marketplace.html
│   ├── connections.html
│   ├── ecosystem.html
│   ├── debug.html
│   ├── formulas.html
│   ├── orchestration.html
│   ├── models.html
│   ├── leaders.html
│   ├── revenue.html
│   ├── costs.html
│   ├── timecapsule.html
│   ├── learning.html
│   ├── pricing.html
│   ├── loans.html
│   ├── codelab.html
│   ├── crypto.html
│   ├── payments.html
│   ├── nav.js         # Shared navigation
│   └── styles.css     # Full dark-mode design system
├── shared/            # TypeScript shared types & schemas
├── server/            # Express.js backend
├── client/            # React + Vite frontend
├── docs/              # Architecture & API documentation
├── app.yaml           # Google App Engine config
├── cloudbuild.yaml    # 5-step CI/CD pipeline
└── firebase.json      # Firebase Hosting config
```

## 🤖 All 1051 Bots by Division

| Division | Bots | Files |
|----------|------|-------|
| CommandCore | 13 | [View →](App_bots/CommandCore.json) |
| DreamSalesPro | 37 | [View →](App_bots/DreamSalesPro.json) |
| DreamFinance | 25 | [View →](App_bots/DreamFinance.json) |
| DreamRealEstate | 25 | [View →](App_bots/DreamRealEstate.json) |
| DreamAIInfra | 25 | [View →](App_bots/DreamAIInfra.json) |
| DreamRetail | 26 | [View →](App_bots/DreamRetail.json) |
| DreamProServices | 25 | [View →](App_bots/DreamProServices.json) |
| DreamData | 16 | [View →](App_bots/DreamData.json) |
| DreamGlobal | 16 | [View →](App_bots/DreamGlobal.json) |
| DreamAutomation | 21 | [View →](App_bots/DreamAutomation.json) |
| DreamContent | 16 | [View →](App_bots/DreamContent.json) |
| DreamTrade | 12 | [View →](App_bots/DreamTrade.json) |
| DreamFlow | 5 | [View →](App_bots/DreamFlow.json) |
| DreamMarket | 5 | [View →](App_bots/DreamMarket.json) |
| DreamEmpire | 5 | [View →](App_bots/DreamEmpire.json) |
| GameTitan | 4 | [View →](App_bots/GameTitan.json) |
| DreamInfluence | 25 | [View →](App_bots/DreamInfluence.json) |
| DreamDecision | 25 | [View →](App_bots/DreamDecision.json) |
| DreamOps | 26 | [View →](App_bots/DreamOps.json) |
| DreamPlanetary | 25 | [View →](App_bots/DreamPlanetary.json) |
| DreamEntFinance | 25 | [View →](App_bots/DreamEntFinance.json) |
| DreamCustIntel | 25 | [View →](App_bots/DreamCustIntel.json) |
| DreamLegal | 25 | [View →](App_bots/DreamLegal.json) |
| DreamCyber | 25 | [View →](App_bots/DreamCyber.json) |
| DreamHealth | 20 | [View →](App_bots/DreamHealth.json) |
| DreamEducation | 20 | [View →](App_bots/DreamEducation.json) |
| DreamConstruction | 19 | [View →](App_bots/DreamConstruction.json) |
| DreamTransport | 19 | [View →](App_bots/DreamTransport.json) |
| DreamFood | 20 | [View →](App_bots/DreamFood.json) |
| DreamScience | 20 | [View →](App_bots/DreamScience.json) |
| DreamArts | 18 | [View →](App_bots/DreamArts.json) |
| DreamProtection | 20 | [View →](App_bots/DreamProtection.json) |
| DreamAgriculture | 20 | [View →](App_bots/DreamAgriculture.json) |
| DreamMaintenance | 21 | [View →](App_bots/DreamMaintenance.json) |
| DreamProduction | 20 | [View →](App_bots/DreamProduction.json) |
| DreamSocial | 33 | [View →](App_bots/DreamSocial.json) |
| DreamAdmin | 21 | [View →](App_bots/DreamAdmin.json) |
| DreamCrypto | 20 | [View →](App_bots/DreamCrypto.json) |
| DreamPayments | 23 | [View →](App_bots/DreamPayments.json) |
| DreamBizLaunch | 21 | [View →](App_bots/DreamBizLaunch.json) |
| DreamCodeLab | 146 | [View →](App_bots/DreamCodeLab.json) |
| DreamLoans | 23 | [View →](App_bots/DreamLoans.json) |
| DreamPersonalCare | 30 | [View →](App_bots/DreamPersonalCare.json) |
| DreamMilitary | 20 | [View →](App_bots/DreamMilitary.json) |
| DreamAgents | 20 | [View →](App_bots/DreamAgents.json) |

## 🚀 Autonomy Modes

| Mode | Description | Tier Required |
|------|-------------|---------------|
| **Guided** | Plan and preview work; approve each external action | Free |
| **Scheduled** | Run approved read-only checks on a bounded schedule | Configured deployment |
| **Governed execution** | Use scoped adapters, audit receipts, budgets, and pause controls | Configured deployment |

## 💰 Pricing

| Tier | Bots | Price |
|------|------|-------|
| Free | 5 bots | $0/mo |
| Pro | 50 bots | $299/mo |
| Enterprise | 150 bots | $999/mo |
| Elite | All 1051+ bots | Custom |

## 🧠 Buddy Bot - Governed Task Router

Buddy Bot ([profile](bots/buddy-bot.md)) provides one interface for the repository fleet:
- Routes requests across all 1,051 cataloged specialist profiles
- Shows repository-controlled capability certification evidence
- Defaults to free local planning and supports optional approved provider routing
- Creates previews and approval gates before external side effects
- Connects to this computer through a loopback-only, short-lived local session

## Local Owner Workspace

Run Buddy from this computer with a private local bridge:

```bash
python3 tools/buddy_cli.py local-start
```

The bridge binds to `127.0.0.1`, creates an ephemeral session token, keeps a memory-only 50-event action log, and supports approved browser searches, HTTPS opens, safe app launches, and action planning. It does not provide arbitrary background clicking, typing, credential access, or device takeover.

Creative Studio can record adult owner voice samples, capture owner camera images, preview them locally, export the source files, and create a portable consent receipt with SHA-256 media fingerprints. Raw media is not embedded in project packets.

The Model Benchmark Lab audits 200 targets across 12 capability suites: 100 curated catalog records plus 100 task-specific discovery lanes that refresh exact model IDs from official provider catalogs. Catalog checks run locally. Live quality, latency, and cost scores remain empty until authenticated adapters return evidence under a per-run budget and approval.

The Buddy Success Center stores a 30-question, non-sensitive profile in the user's browser, shares only an opted-in summary with specialist routes, and keeps opportunity estimates separate from user-confirmed revenue. Its generated production program covers all 45 divisions with a professional charter, 100 capability contracts, 100 must-have records, 100 upgrade records, 12 production gates, a deterministic robot identity, and an evidence-first competitor benchmark process. A local daily harness checks all 4,500 division capability contracts with bounded parallelism; external comparisons still require a scheduler, configured adapters, current terms, and run-specific approval.

The AI Organization Intelligence registry combines 94 normalized providers from the existing 200-target program with a dated 196-entry snapshot of the official AI Alliance directory. It maps declared strengths and common user jobs to 20 user-need categories and 15 benchmark dimensions while keeping membership, connectivity, and live evidence separate. Refresh with `python3 tools/generate_ai_organization_intelligence.py --refresh`; normal repository checks use the committed snapshot so builds do not depend on the network.

App Connections includes an Access Center for connection profiles, public-safe backend records, browser-local setup plans, authentication methods, and governed secret-store metadata. It shows whether a secret reference exists but never reads, lists, or renders credential values. Raw secret intake remains limited to the approved loopback bridge and macOS Keychain workflow.

The open AI watch claims no membership or endorsement and records zero live member benchmarks until evidence exists. Buddy's defensive security reviews require written owner authority and prohibit credential attacks, destructive payloads, denial of service, persistence, third-party targets, and access to real customer data. Public pages accept references only. The local Buddy bridge can place a user-approved key directly into macOS Keychain and returns only an `os_keychain:` reference; it never persists the raw value in browser storage, generated files, URLs, or audit logs. The Sales Academy uses synthetic role-play before any permissioned outreach workflow.

## 🌐 Live Website

The `website/` directory contains the standalone DreamCo HTML/CSS experience. Open `website/index.html` directly for static features, or serve the directory locally to test service workers and HTTP-only behavior.

## ☁️ Cloud Deployment

Cloud Build auto-deploys on every push to `main`:
1. **Docker** → build & push to Container Registry
2. **Cloud Run** → live API server (us-central1)
3. **App Engine** → static website hosting
4. **Firebase Hosting** → CDN-accelerated website

## 📡 API

All bots are accessible via the Empire OS REST API:
- `GET /api/bots` — list all bots
- `POST /api/chat` — chat with any bot
- `GET /api/bots/:slug` — bot profile
- `GET /api/divisions` — all 45 divisions
- `POST /api/bots/normalize` — validate all bot profiles

---

*Built by DreamCo Technologies.*
