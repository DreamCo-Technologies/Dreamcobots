# Empire OS — Full Stack Source Code

This folder contains the complete DreamCo Empire OS web application source code, synced from DreamCo.

## Stack
- **Frontend**: React 19 + Vite + TailwindCSS + shadcn/ui (29 pages)
- **Backend**: Express.js API server
- **Database**: PostgreSQL (Neon) with Drizzle ORM
- **AI**: OpenAI GPT-4.1-mini powering all 1,051 bots

## Run Locally
```bash
cp .env.example .env  # fill in your secrets
npm install
npm run dev
```

## Pages (29 total)
- `AILeadersPage`
- `AIModelsPage`
- `AutonomyPage`
- `BotActivityPage`
- `BotBuilderPage`
- `BotDetailPage`
- `BotsPage`
- `BusinessPage`
- `ChatIndexPage`
- `CodeLabPage`
- `ConnectionsPage`
- `ConversationPage`
- `CostTrackingPage`
- `CryptoPage`
- `DashboardPage`
- `DealsPage`
- `DebugPage`
- `DivisionsPage`
- `EcosystemPage`
- `FormulasPage`
- `LearningMatrixPage`
- `LoansPage`
- `MarketplacePage`
- `OrchestrationPage`
- `PaymentsPage`
- `PricingPage`
- `RevenuePage`
- `TimeCapsulePage`
- `not-found`

## Key Files
- `shared/schema.ts` — database schema for all 17 tables
- `shared/tool-belt.ts` — self-learning + Buddy Bot protocols injected into all bots
- `server/seed-bots.ts` — 884 core bot definitions
- `server/seed-buddy-bot.ts` — Buddy Bot with 500+ library curriculum
- `server/routes.ts` — all API endpoints
- `server/github-sync.ts` — GitHub push engine
