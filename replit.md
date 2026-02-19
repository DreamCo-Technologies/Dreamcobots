# DreamCo Empire OS

## Overview
DreamCo Empire OS is a 6-layer autonomous wealth-generation system orchestrating over 843 AI bots across 44 divisions. Its primary purpose is revenue generation through a SaaS model, covering a vast array of job categories, including specialized areas like crypto, payments, coding, business launch, and loan services. The system features three autonomy modes (Guided, Semi-Autonomous, Full Autonomy) and provides comprehensive bot tracking and metrics. The vision is to offer a powerful, adaptive, and revenue-focused AI ecosystem.

## User Preferences
I prefer detailed explanations.
I want iterative development.
Ask before making major changes.

## System Architecture
The system employs a modern web stack:
- **Frontend**: React, Vite, TailwindCSS, and shadcn/ui for a responsive and consistent user experience.
- **Backend**: An Express.js API server handles all business logic and data interactions.
- **Database**: PostgreSQL, specifically Neon-backed, managed with Drizzle ORM.
- **AI**: Integrates OpenAI GPT-4.1-mini capabilities through Replit AI.

**Core Architectural Decisions & Design Patterns:**
- **Modular Design**: The system is structured into 44 divisions, each comprising multiple specialized AI bots, allowing for scalability and clear separation of concerns.
- **Autonomy Modes**: Three distinct operational modes (Guided, Semi-Autonomous, Full Autonomy) offer flexibility in bot control and user intervention, with tier-based access.
- **Data Schemas**: A centralized `shared/schema.ts` defines 12 core database tables for managing conversations, bots, tasks, metrics, financials, and system settings.
- **API-Driven Control**: All bot and system controls, including autonomy levels and operational modes (sandbox/live/offline), are managed via a comprehensive RESTful API.
- **Revenue Architecture**: Built-in SaaS pricing tiers (Free, Pro, Enterprise, Elite) gate access to features and higher autonomy levels. A dedicated API Integration Registry supports diverse service connections.
- **Debug Intelligence System (DIS)**: A robust error handling and monitoring system with 12 error categories, an auto-fix engine, revenue leak detection, and security scanning, all presented through an 8-tab dashboard.
- **Deal Analyzer System**: Specialized calculators for real estate and car flipping, featuring KPI aggregation, scoring, and capital efficiency comparisons.
- **AI Ecosystem & Orchestration (MOE)**: A registry of 200+ AI providers, a Model Orchestration Engine for intelligent task routing based on various criteria (accuracy, speed, cost), and a marketplace for subscription tiers, skill packs, and industry verticals.
- **Global AI Learning Matrix**: A sophisticated system for tracking global AI developments, learning methods, features, and labs across multiple countries, designed to inform the evolution of the Empire OS. It also houses a vast library of division-specific, high-profit formulas.

**UI/UX Decisions:**
- A consistent `AppShell` with sidebar navigation ensures easy access to all system modules.
- Dedicated pages for Dashboard, Divisions, Bots, Autonomy, Chat, Ecosystem, Orchestration, Marketplace, Formulas, Deals, Debug, and Learning Matrix provide specialized views and controls.
- Bot cards are interactive, leading to detailed profile pages with control panels, metrics, and capabilities.
- Color-coded status indicators are used in the Deal Analyzer for quick assessment of deal viability.

## External Dependencies
- **OpenAI GPT-4.1-mini**: Utilized for core AI functionalities and integrations.
- **PostgreSQL (Neon-backed)**: The primary database solution, offering scalable and managed data storage.
- **Drizzle ORM**: Used for interacting with the PostgreSQL database.
- **Various Third-Party APIs**: Over 200 APIs are integrated across all divisions, especially within DreamSalesPro (e.g., CRM, Lead Databases, Email, SMS, Payments).