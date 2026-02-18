# DreamCo Empire OS

## Overview
DreamCo Empire OS is a 6-layer autonomous wealth-generation system with 251 coordinated AI bots across 16 divisions. It features three autonomy modes (Guided, Semi-Autonomous, Full Autonomy), comprehensive bot tracking/metrics, and a revenue-focused SaaS architecture.

## Architecture
- **Frontend**: React + Vite + TailwindCSS + shadcn/ui, served on port 5000
- **Backend**: Express.js API server
- **Database**: PostgreSQL (Neon-backed via Drizzle ORM)
- **AI**: OpenAI GPT-4.1-mini via Replit AI integrations

## Key Files
- `shared/schema.ts` - Database schema with 11 tables (conversations, messages, bot_profiles, autonomous_tasks, task_runs, empire_settings, bot_metrics, bot_errors, bot_interactions, bot_financials, alert_rules)
- `server/routes.ts` - All API endpoints
- `server/storage.ts` - Database operations (IStorage interface + DatabaseStorage)
- `server/seed-bots.ts` - 251 bot definitions across 16 divisions
- `client/src/App.tsx` - Frontend routing
- `client/src/components/AppShell.tsx` - Main layout shell with sidebar navigation
- `client/src/pages/DashboardPage.tsx` - Empire Command Center dashboard
- `client/src/pages/DivisionsPage.tsx` - Division Explorer with filtering
- `client/src/pages/AutonomyPage.tsx` - Task management with autonomy modes
- `client/src/pages/BotsPage.tsx` - Bot profile management
- `client/src/pages/ChatIndexPage.tsx` - Chat interface
- `client/src/pages/ConversationPage.tsx` - Individual conversation view
- `client/src/hooks/use-empire.ts` - Empire/division/autonomy hooks
- `client/src/hooks/use-bots.ts` - Bot CRUD hooks
- `client/src/hooks/use-tasks.ts` - Task CRUD hooks

## 16 Divisions
DreamFinance (25), DreamRealEstate (25), DreamSalesPro (25), DreamAIInfra (25), DreamRetail (25), DreamProServices (25), DreamData (15), DreamGlobal (15), DreamAutomation (20), DreamContent (15), DreamTrade (10), DreamFlow (5), DreamMarket (5), DreamEmpire (5), CommandCore (8), GameTitan (3)

## Autonomy Modes
- **Guided**: User approval on all actions
- **Semi-Autonomous**: Low-risk auto-execution, high-risk flags for approval
- **Full Autonomy**: Reporting only, full auto-execution

## Bot Tiers
- Free ($0), Pro ($29-299/mo), Enterprise ($499-999/mo), Elite ($999-2,500/mo)

## Tracking System (200+ features)
- Bot metrics (CPU, memory, API calls, uptime, task duration, revenue)
- Error logging with auto-remediation rules
- Interaction tracking (input/output audit trail)
- Financial tracking (transactions, revenue per bot)
- 7 default alert rules (task failure cascade, CPU overload, unauthorized access, model drift, high error rate, revenue drop, bot offline)

## API Endpoints
- `/api/bots` - Bot CRUD
- `/api/bots/:id` - Get single bot by ID
- `/api/bots/:id/controls` - PATCH to update bot autonomy level and operational mode
- `/api/bots/division/:division` - Bots by division
- `/api/conversations` - Conversation CRUD
- `/api/tasks` - Task CRUD with run execution
- `/api/empire/overview` - Full empire stats
- `/api/empire/divisions` - Division bot counts
- `/api/empire/settings/:key` - Empire settings (GET/PUT)
- `/api/metrics/health` - Bot health summary
- `/api/metrics/bot/:botId` - Per-bot metrics
- `/api/errors` - Error logs
- `/api/financials` - Financial tracking
- `/api/alerts` - Alert rules management

## Bot Control System
Each bot has per-bot controls:
- **Autonomy Level**: guided | semi-autonomous | full-autonomy
- **Operational Mode**: sandbox | live | offline
- Controls are managed via PATCH /api/bots/:id/controls
- Bot Detail Page (/bot/:id) has a Control Panel with buttons for each setting
- Schema fields: autonomyLevel (default: "guided"), operationalMode (default: "sandbox")

## Revenue Architecture
- `shared/api-registry.ts` - API Integration Registry with 200+ APIs across all divisions
- `client/src/pages/RevenuePage.tsx` - Revenue Dashboard with per-bot/division revenue tracking
- `client/src/pages/PricingPage.tsx` - SaaS Pricing page with tier comparison (Free/Pro/Enterprise/Elite)
- Tier-based autonomy gating: Free=Guided only, Pro=Semi-autonomous, Enterprise/Elite=Full autonomy
- API integrations panel on BotDetailPage showing connected services per bot with tier requirements
- DreamSalesPro has 100+ APIs across 12 categories (CRM, Lead Databases, Email, SMS, Payments, AI, etc.)
- TIER_PRICING and TIER_AUTONOMY_LIMITS exported from api-registry.ts for consistent tier enforcement

## Deal Analyzer System
- `shared/deal-calculations.ts` - All flipping formulas (MAO, Net Profit, ROI, Safety Score, Capital Efficiency, Leverage ROI, Cash-on-Cash for RE; Max Purchase, Daily Profit, Capital Turn, Annual Return for cars)
- `client/src/pages/DealsPage.tsx` - Deal Analyzer page at /deals with 3 tabs (Property Flip, Car Flip, Portfolio)
- Database: deals table with jsonb inputs/results, color-coded status (green/yellow/red), KPI aggregation
- API: GET/POST/DELETE /api/deals, GET /api/deals/kpis
- Real Estate scoring: Green = ROI>=20%, profit>0, purchase<=MAO, safety>=15; Red = ROI<5% or profit<0; Yellow = between
- Car scoring: Green = ROI>=20%, margin>=15%; Red = ROI<5% or margin<5%; Yellow = between
- Capital Efficiency Comparison: daily profit / cash invested / days held, ranks Property vs Car vs Hold
- Formulas: MAO = (ARV * 0.70) - Repairs; Car Max Purchase = Sale * 0.75 - Repairs

## Recent Changes
- Feb 18, 2026: Built Deal Analyzer with RE/Car calculators, color-coded scoring, portfolio KPIs, capital efficiency comparison
- Feb 18, 2026: Built Revenue Dashboard page at /revenue with division revenue, top bots, API summary
- Feb 18, 2026: Built SaaS Pricing page at /pricing with tier comparison, autonomy access, annual discount
- Feb 18, 2026: Added tier-based autonomy gating - locked controls show "Pro+" or "Enterprise+" badges
- Feb 18, 2026: Added API Integrations panel to BotDetailPage with per-API tier requirements
- Feb 18, 2026: Created API Integration Registry (shared/api-registry.ts) with 200+ APIs across all divisions
- Feb 18, 2026: Added per-bot Control Panel with autonomy level (Guided/Semi-Autonomous/Full Autonomy) and operational mode (Sandbox/Live/Offline) buttons
- Feb 18, 2026: Added individual Bot Detail Pages at /bot/:id with dashboard metrics, capabilities, division features, investment prospectus, system prompt, and traits
- Feb 18, 2026: Enhanced all 251 bots with 18-36 capabilities each (tier-specific + universal features)
- Feb 18, 2026: Made bot cards clickable in DivisionsPage and BotsPage with navigation to detail pages
- Feb 18, 2026: Added bot data tracking architecture (bot_metrics, bot_errors, bot_interactions, bot_financials, alert_rules tables)
- Feb 18, 2026: Built Empire Command Center dashboard with system health, autonomy mode selector, alert rules, division overview
- Feb 18, 2026: Built Division Explorer page with filtering by division/tier/category/search
- Feb 18, 2026: Added 7 auto-remediation alert rules
- Feb 18, 2026: Rebranded from "Buddy" to "DreamCo Empire OS"
