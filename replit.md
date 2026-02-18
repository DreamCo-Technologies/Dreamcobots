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

## Recent Changes
- Feb 18, 2026: Added individual Bot Detail Pages at /bot/:id with dashboard metrics, capabilities, division features, investment prospectus, system prompt, and traits
- Feb 18, 2026: Enhanced all 251 bots with 18-36 capabilities each (tier-specific + universal features)
- Feb 18, 2026: Made bot cards clickable in DivisionsPage and BotsPage with navigation to detail pages
- Feb 18, 2026: Added bot data tracking architecture (bot_metrics, bot_errors, bot_interactions, bot_financials, alert_rules tables)
- Feb 18, 2026: Built Empire Command Center dashboard with system health, autonomy mode selector, alert rules, division overview
- Feb 18, 2026: Built Division Explorer page with filtering by division/tier/category/search
- Feb 18, 2026: Added 7 auto-remediation alert rules
- Feb 18, 2026: Rebranded from "Buddy" to "DreamCo Empire OS"
