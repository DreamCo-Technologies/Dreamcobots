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

## 🧠 Buddy Bot - Governed Task Router

Buddy Bot ([profile](bots/buddy-bot.md)) provides one interface for the repository fleet:
- Routes requests across all 1,051 cataloged specialist profiles
- Shows repository-controlled capability certification evidence
- Defaults to free local planning and supports optional approved provider routing
- Creates previews and approval gates before external side effects
- Connects to this computer through a loopback-only, short-lived local session

### Probabilistic Workflow Learning

Buddy now includes an explainable first-order **Markov-chain learner** at `buddy_os/learning/markov_engine.py`. It learns transition probabilities from observed workflow traces and can predict likely next states, score trace likelihood, rank candidate routes, and flag unusually surprising transitions. The policy is deliberately advisory: governance, safety controls, approvals, and deterministic rules remain authoritative.

This addition is informed by Russian research covering coupled Markov chains for machine-learning knowledge extraction, Markov Decision Processes and convex optimization, hierarchical multi-agent reinforcement learning in MDPs, and synthetic-data generation with binary Markov models. citeturn0search0turn0search6turn0search8turn0search5

The implementation and tests are dependency-free and can be used as a compact feature layer for Buddy's existing learning, routing, and evaluation systems. Configuration lives in `buddy_os/learning/markov_learning_policy.yaml`.

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
