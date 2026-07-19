# DreamCo Empire OS — Architecture

## System Overview
6-layer autonomous wealth-generation system built on:
- **Frontend**: React 18 + Vite + TailwindCSS + shadcn/ui
- **Backend**: Express.js REST API
- **Database**: PostgreSQL (Neon-backed) via Drizzle ORM
- **AI**: OpenAI GPT-4.1-mini for all bot intelligence
- **Hosting**: Cloud Run + App Engine + Firebase Hosting

## Core Components

### Universal Tool Belt (shared/tool-belt.ts)
Runtime-injected system prompt enhancement giving all 1051 bots:
- Entrepreneurship tools & frameworks
- AI safety principles
- Mode-specific instructions (Plan/Build/Execute/Teach)
- Top 100 AI companies context
- Buddy Bot Protocol (routes coding tasks to Buddy)

### Autonomy Engine
Three operational modes:
1. **Guided** — User approves each bot action
2. **Semi-Autonomous** — Bots execute, user reviews weekly reports
3. **Full Autonomy** — 24/7 operation, self-healing, zero human input

### Debug Intelligence System (DIS)
12 error categories with auto-fix engine, revenue leak detection, and security scanning.

### Model Orchestration Engine (MOE)
Intelligent routing across 200+ AI providers:
- Accuracy-First → GPT-4o / Claude 3.5 Sonnet
- Speed-First → GPT-4.1-mini / Gemini Flash / Groq Llama
- Cost-First → Llama 70B / Mistral / self-hosted

## Database Schema (17 Tables)
- conversations, messages
- bot_profiles, bot_memory
- tasks, metrics
- financials (revenue, costs)
- system_settings, platform_connections
- plugins, system_snapshots, cost_events
- github_sync_log

## Revenue Architecture
SaaS tiers gate bot count and autonomy level:
- Free: 5 bots, guided only
- Pro ($299/mo): 50 bots, semi-autonomous
- Enterprise ($999/mo): 150 bots, full autonomy
- Elite (custom): All 1051+ bots, 24/7 full autonomy

## CI/CD Pipeline (cloudbuild.yaml)
5 steps on every push to main:
1. Docker build → tag with commit SHA
2. Push to Google Container Registry  
3. Deploy to Cloud Run (us-central1)
4. Deploy to App Engine (static website)
5. Deploy to Firebase Hosting
