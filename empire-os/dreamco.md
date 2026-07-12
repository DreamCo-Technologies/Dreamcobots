# DreamCo Empire OS

## Overview
DreamCo Empire OS is a 6-layer autonomous wealth-generation system orchestrating over 875+ AI bots across 45 divisions (including the new DreamAgents autonomous agent division). Its primary purpose is revenue generation through a SaaS model, covering a vast array of job categories, including specialized areas like crypto, payments, coding, business launch, and loan services. The system features three autonomy modes (Guided, Semi-Autonomous, Full Autonomy) and provides comprehensive bot tracking and metrics. The vision is to offer a powerful, adaptive, and revenue-focused AI ecosystem.

## User Preferences
I prefer detailed explanations.
I want iterative development.
Ask before making major changes.

## System Architecture
The system employs a modern web stack:
- **Frontend**: React, Vite, TailwindCSS, and shadcn/ui for a responsive and consistent user experience.
- **Backend**: An Express.js API server handles all business logic and data interactions.
- **Database**: PostgreSQL, specifically Neon-backed, managed with Drizzle ORM.
- **AI**: Integrates OpenAI GPT-4.1-mini capabilities through DreamCo AI.

**Core Architectural Decisions & Design Patterns:**
- **Modular Design**: The system is structured into 45 divisions, each comprising multiple specialized AI bots, allowing for scalability and clear separation of concerns.
- **Autonomy Modes**: Three distinct operational modes (Guided, Semi-Autonomous, Full Autonomy) offer flexibility in bot control and user intervention, with tier-based access.
- **Data Schemas**: A centralized `shared/schema.ts` defines 17 core database tables for managing conversations, bots, tasks, metrics, financials, system settings, platform connections, plugins, bot memory, system snapshots, and cost events.
- **API-Driven Control**: All bot and system controls, including autonomy levels and operational modes (sandbox/live/offline), are managed via a comprehensive RESTful API.
- **Revenue Architecture**: Built-in SaaS pricing tiers (Free, Pro, Enterprise, Elite) gate access to features and higher autonomy levels. A dedicated API Integration Registry supports diverse service connections.
- **Debug Intelligence System (DIS)**: A robust error handling and monitoring system with 12 error categories, an auto-fix engine, revenue leak detection, and security scanning, all presented through an 8-tab dashboard.
- **Deal Analyzer System**: Specialized calculators for real estate and car flipping, featuring KPI aggregation, scoring, and capital efficiency comparisons.
- **AI Ecosystem & Orchestration (MOE)**: A registry of 200+ AI providers, a Model Orchestration Engine for intelligent task routing based on various criteria (accuracy, speed, cost), and a marketplace for subscription tiers, skill packs, and industry verticals.
- **Global AI Learning Matrix**: A sophisticated system for tracking global AI developments, learning methods, features, and labs across multiple countries, designed to inform the evolution of the Empire OS. It also houses a vast library of division-specific, high-profit formulas.

**UI/UX Decisions:**
- A consistent `AppShell` with sidebar navigation ensures easy access to all system modules.
- Dedicated pages for Dashboard, Divisions, Bots, Autonomy, Chat (with Plan/Build/Execute/Teach mode selector), Ecosystem, Orchestration, Marketplace (with Plugins tab), Formulas, Deals, Debug, Learning Matrix, AI Leaders (Top 100 AI companies), AI Models Hub (100 models with free/paid tiers, package deals, Stripe checkout), Connections (multi-platform access + kill switch), Time Capsule (system snapshots), and Cost Tracking provide specialized views and controls.
- **Universal Tool Belt** (`shared/tool-belt.ts`): Runtime-injected system prompt enhancement giving all 857 bots entrepreneurship tools, AI safety principles, mode-specific instructions, and Top 100 AI companies context. Uses `buildEnhancedSystemPrompt()` to compose final prompts.
- **Chat Mode Selector**: Plan/Build/Execute/Teach modes shape bot behavior and suggested prompts. Mode is passed in streaming requests and injected into system prompts at runtime.
- **Bot Normalization Endpoint**: POST `/api/bots/normalize` validates and fills missing fields across all bot profiles.
- Bot cards are interactive, leading to detailed profile pages with control panels, metrics, and capabilities.
- Color-coded status indicators are used in the Deal Analyzer for quick assessment of deal viability.

## Bot Sources (1,051+ Total Bots)
- `server/seed-bots.ts` — 884 original DreamCo bots across all 45 divisions
- `server/seed-github-bots.ts` — 67 bots merged from github.com/DreamCo-Technologies/Dreamcobots (App_bots + specialty bots from bots/ directory)
- `server/seed-codelabs.ts` — 100+ coding library bots in DreamCodeLab division, one bot per major library/framework/tool
- Deduplication logic in `server/routes.ts` merges all three sources and removes slugs already present
- **Buddy Bot** (`slug: buddy-bot`, `server/seed-buddy-bot.ts`) — Elite CommandCore master coding brain. System prompt covers 500+ libraries across every language, framework, and tool in existence. All 1,051 bots are wired to route coding tasks through Buddy. Always upserted on startup so curriculum stays current.
- Every non-Buddy bot's system prompt now contains `BUDDY_BOT_PROTOCOL` (from `shared/tool-belt.ts`) instructing them to route coding tasks to Buddy Bot
- Frontend: "Call Buddy" button on every ConversationPage toolbar; "Buddy Bot" quick-switch shortcut in AppShell sidebar

## PWA (Progressive Web App)
- `client/public/manifest.json` — Full PWA manifest with shortcuts to Dashboard, Bots, Divisions, Chat
- `client/public/sw.js` — Service worker for offline caching (skips /api/ routes)
- `client/index.html` — Updated with PWA meta tags for iOS, Android, Windows, Open Graph, Twitter Card
- `client/src/main.tsx` — Registers service worker on load
- **ConnectionsPage** — New "Install App" tab with step-by-step install guides for: Android, iPhone/iPad, Windows, Mac, Smart TV (Samsung/LG/Fire TV), Gaming Consoles (Xbox/PS5/Switch), Chromebook, Roku/Apple TV/Streaming Sticks. Includes a live "Install Now" button that triggers the browser's native PWA install prompt when available.

## GitHub Integration
- GitHub OAuth integration (`connector:ccfg_github_01K4B9XD3VRVD2F99YM91YTCAF`) was proposed but dismissed by the user.
- To push codebase to GitHub in the future, either: (1) re-authorize the GitHub integration via DreamCo, or (2) provide a GitHub Personal Access Token to store as a secret (`GITHUB_TOKEN`) and use the GitHub REST API to create/push the repo.

## External Dependencies
- **OpenAI GPT-4.1-mini**: Utilized for core AI functionalities and integrations.
- **PostgreSQL (Neon-backed)**: The primary database solution, offering scalable and managed data storage.
- **Drizzle ORM**: Used for interacting with the PostgreSQL database.
- **Various Third-Party APIs**: Over 200 APIs are integrated across all divisions, especially within DreamSalesPro (e.g., CRM, Lead Databases, Email, SMS, Payments).