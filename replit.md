# DreamCo Empire OS

## Overview
DreamCo Empire OS is a 6-layer autonomous wealth-generation system with 251 coordinated AI bots across 16 divisions. It features three autonomy modes (Guided, Semi-Autonomous, Full Autonomy), comprehensive bot tracking/metrics, and a revenue-focused SaaS architecture.

## Architecture
- **Frontend**: React + Vite + TailwindCSS + shadcn/ui, served on port 5000
- **Backend**: Express.js API server
- **Database**: PostgreSQL (Neon-backed via Drizzle ORM)
- **AI**: OpenAI GPT-4.1-mini via Replit AI integrations

## Key Files
- `shared/schema.ts` - Database schema with 12 tables (conversations, messages, bot_profiles, autonomous_tasks, task_runs, empire_settings, bot_metrics, bot_errors, bot_interactions, bot_financials, alert_rules, formulas)
- `shared/ai-ecosystem.ts` - AI Ecosystem Registry with 200+ providers across 20 categories
- `shared/bundles.ts` - Subscription tiers, 10 skill packs, 9 industry verticals, 20 MOE routing rules
- `shared/formula-library.ts` - 40+ system formulas across 6 categories
- `server/routes.ts` - All API endpoints
- `server/storage.ts` - Database operations (IStorage interface + DatabaseStorage)
- `server/seed-bots.ts` - 451 bot definitions across 24 divisions
- `client/src/App.tsx` - Frontend routing
- `client/src/components/AppShell.tsx` - Main layout shell with sidebar navigation
- `client/src/pages/DashboardPage.tsx` - Empire Command Center dashboard
- `client/src/pages/DivisionsPage.tsx` - Division Explorer with filtering
- `client/src/pages/AutonomyPage.tsx` - Task management with autonomy modes
- `client/src/pages/BotsPage.tsx` - Bot profile management
- `client/src/pages/ChatIndexPage.tsx` - Chat interface
- `client/src/pages/ConversationPage.tsx` - Individual conversation view
- `client/src/pages/EcosystemPage.tsx` - AI Provider Registry at /ecosystem
- `client/src/pages/OrchestrationPage.tsx` - Model Orchestration Engine at /orchestration
- `client/src/pages/MarketplacePage.tsx` - AI Marketplace at /marketplace
- `client/src/pages/FormulasPage.tsx` - Formula Vault with CRUD at /formulas
- `client/src/hooks/use-empire.ts` - Empire/division/autonomy hooks
- `client/src/hooks/use-bots.ts` - Bot CRUD hooks
- `client/src/hooks/use-tasks.ts` - Task CRUD hooks

## 24 Divisions (451 bots)
DreamFinance (25), DreamRealEstate (25), DreamSalesPro (25), DreamAIInfra (25), DreamRetail (25), DreamProServices (25), DreamData (15), DreamGlobal (15), DreamAutomation (20), DreamContent (15), DreamTrade (10), DreamFlow (5), DreamMarket (5), DreamEmpire (5), CommandCore (8), GameTitan (3), DreamInfluence (25), DreamDecision (25), DreamOps (25), DreamPlanetary (25), DreamEntFinance (25), DreamCustIntel (25), DreamLegal (25), DreamCyber (25)

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
- `/api/formulas` - Formula CRUD (GET/POST)
- `/api/formulas/:id` - Formula by ID (GET/PATCH/DELETE)

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

## Debug Intelligence System (DIS)
- `shared/schema.ts` - 4 DIS tables: debug_events, auto_fixes, revenue_leaks, security_scans + DebugOverview interface
- `client/src/pages/DebugPage.tsx` - Debug Intelligence Dashboard at /debug with 8 tabs
- 12 Error Categories: syntax_error, runtime_crash, api_failure, auth_error, logic_bug, performance_issue, ux_friction, revenue_leak, security_risk, infinite_loop, model_drift, cost_explosion
- Auto-Fix Engine: Confidence >=90% auto-deploys, <90% queued for manual approval
- Revenue Leak Detector: Tracks failed_checkout, broken_funnel, pricing_error, cart_abandonment, api_overuse, subscription_churn
- Security Scanner: dependency_audit, code_scan, config_review, penetration_test, compliance_check
- Global Health Score: resolution rate minus penalties (critical x5, leaks x2, security x3)
- Dashboard Tabs: Overview, Active Issues, Auto-Fixes, Revenue Impact, Security, Bot Health, Patch History, Learning Log
- API: GET/POST /api/debug/events, PATCH /api/debug/events/:id/resolve, GET/POST /api/debug/auto-fixes, PATCH apply/reject, GET/POST /api/debug/revenue-leaks, PATCH resolve, GET/POST /api/debug/security-scans, PATCH remediate, GET /api/debug/overview, POST /api/debug/seed

## AI Ecosystem & Orchestration (Phase 1: MOE)
- `shared/ai-ecosystem.ts` - 200+ AI providers across 20 categories (Foundation Models, Cloud, Hardware, Enterprise, Healthcare, FinTech, Legal, Security, etc.)
- `shared/bundles.ts` - 3 bundle systems: 4 Subscription Tiers (Free/Pro/Elite/Enterprise), 10 Skill Packs, 9 Industry Verticals, 20 MOE Routing Rules
- `shared/formula-library.ts` - 40+ formulas across 6 categories (Real Estate, Car Flipping, Sales, Capital Deployment, Risk Management, Revenue Intelligence)
- `shared/division-formulas.ts` - 1,200 division-specific formulas (50 per division across all 24 divisions)
- `client/src/pages/EcosystemPage.tsx` - AI Provider Registry at /ecosystem with search, category/pricing filters, provider cards
- `client/src/pages/OrchestrationPage.tsx` - Model Orchestration Engine at /orchestration with routing rules, priority/cost filters, architecture diagram
- `client/src/pages/MarketplacePage.tsx` - AI Marketplace at /marketplace with 3 tabs (Tiers, Skill Packs, Industry Verticals)
- `client/src/pages/FormulasPage.tsx` - Formula Vault at /formulas with full CRUD, category tabs, search, system formula protection
- `client/src/pages/LearningMatrixPage.tsx` - Global AI Learning Matrix at /learning-matrix with 8 tabs, 200 features, 7 countries, 42 AI labs
- Database: formulas table with name, category, description, formula, variables (jsonb), target, tags (jsonb), isSystem flag
- 40+ system formulas auto-seeded on startup from formula-library.ts
- 1,200 division-specific formulas with clickable buttons on Bot Detail Pages
- MOE routes tasks to best providers based on priority (accuracy/speed/quality/safety/scale/compliance) and cost tier (standard/premium)

## Global AI Learning Matrix
- `shared/division-formulas.ts` - 1,200 high-profit formulas (50 unique per division, no repeats)
- `client/src/pages/LearningMatrixPage.tsx` - 8-tab dashboard at /learning-matrix
- Tabs: Learning Matrix, Architecture Pipeline, Learning Methods, Global AI Labs, 200 Features, Sandbox Lab, Evolution Engine, Governance
- 7 Countries tracked: America, China, India, Europe, Japan, Israel, Canada
- 42 AI Labs monitored (6 per country)
- 9 Learning Methods: Supervised, Unsupervised, RL, Self-Supervised, Federated, Transfer, Multi-Modal, AutoML/NAS, Meta-Learning
- 200 features across 5 categories: Global Learning Intelligence (40), Sandbox Testing Lab (40), Self-Evolution Engine (40), Profit & Performance Intelligence (40), Control Security & Infrastructure (40)
- Bot Detail Page shows 50 formula buttons per bot (division-specific) with modal details

## Recent Changes
- Feb 19, 2026: Built Global AI Learning Matrix page at /learning-matrix with 8 tabs, 200 features, 7 countries, 42 AI labs, sandbox testing, evolution engine, governance
- Feb 19, 2026: Created 1,200 division-specific formulas (50 unique per division across all 24 divisions) in shared/division-formulas.ts
- Feb 19, 2026: Added High-Profit Formula Toolkit to Bot Detail Pages with 50 clickable formula buttons per bot with modal details
- Feb 19, 2026: Built AI Ecosystem page at /ecosystem with 200+ providers, search, category/pricing filters
- Feb 19, 2026: Built Model Orchestration Engine page at /orchestration with 20 routing rules, architecture flow diagram
- Feb 19, 2026: Built AI Marketplace page at /marketplace with subscription tiers, skill packs, industry verticals
- Feb 19, 2026: Built Formula Vault page at /formulas with full CRUD, 40+ system formulas, category filtering
- Feb 19, 2026: Added formulas table to database schema with auto-seeding of system formulas
- Feb 19, 2026: Created AI Ecosystem Registry (shared/ai-ecosystem.ts) with 200+ providers across 20 categories
- Feb 19, 2026: Created Bundle definitions (shared/bundles.ts) with tiers, skill packs, verticals, MOE routing rules
- Feb 19, 2026: Created Formula Library (shared/formula-library.ts) with 40+ formulas across 6 categories
- Feb 18, 2026: Added 8 new divisions (DreamInfluence, DreamDecision, DreamOps, DreamPlanetary, DreamEntFinance, DreamCustIntel, DreamLegal, DreamCyber) with 200 new bots, bringing total to 451 bots across 24 divisions
- Feb 18, 2026: Built Debug Intelligence System (DIS) with 4 tables, 12 error categories, auto-fix engine, revenue leak detector, security scanner, 8-tab dashboard at /debug
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
