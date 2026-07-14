# 🤖 DreamCo Bot Operating Platform

> **1,051 designed bot profiles · 45 divisions · evidence-tracked readiness · supervised Buddy control plane**

[![🪐 Command Tower](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/command-tower.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/command-tower.yml)
[![💰 Revenue Engine](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/revenue_engine.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/revenue_engine.yml)
[![🛡️ Framework Compliance](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/framework-compliance.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/framework-compliance.yml)
[![🧠 Auto-Retrain](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/auto-retrain.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/auto-retrain.yml)
[![🔥 Chaos Testing](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/chaos-testing.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/chaos-testing.yml)
[![🤝 Bot Submission CI](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/bot-submission.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/bot-submission.yml)
![Bot Profiles](https://img.shields.io/badge/Bot%20Profiles-1051-blue?logo=robot&logoColor=white)
![Divisions](https://img.shields.io/badge/Divisions-45-purple?logo=building&logoColor=white)
![Tiers](https://img.shields.io/badge/Tiers-free%20%7C%20pro%20%7C%20enterprise%20%7C%20elite-gold)
![Readiness](https://img.shields.io/badge/Readiness-evidence%20tracked-green?logo=githubactions&logoColor=white)

## Current Truth

DreamCo is being consolidated into one reliable AI operating platform. The repository contains many designed bot profiles, generated libraries, dashboards, workflows, and integration plans, but a profile or folder is not the same as a production-ready bot.

- Designed bot profiles: **1,051**
- Divisions: **45**
- Production readiness: tracked through registry, dashboard, tests, reports, and pull request evidence
- Buddy role: supervised top-level controller and dashboard router
- Release posture: stabilize, prove, and document before expanding

## DreamCo Command Center Merge

The DreamCo-built `DreamCo-Technologies/DreamCo-Command-Center` app is now being merged into this main Dreamcobots repository in stages.

- Stage 1 integration scaffold: `integrations/dreamco-command-center/README.md`
- Source/system inventory: `integrations/dreamco-command-center/SYSTEM_INVENTORY.md`
- Merge goal: preserve the command-center dashboard, API server, bot contract system, database schemas, attached DreamCo directives, and helper libraries without breaking the existing bot repository.

## 📁 Repository Structure

| Folder | Files | Description |
|--------|-------|-------------|
| `bots/{slug}/bot_profile.json` | 1051 | Every bot profile synced from Empire OS |
| `python_bots/` | 16 | Python bots (FastAPI, PyTorch, LangChain, etc.) |
| `java_bots/` | 31 | Java/Kotlin bots (Spring Boot, Android, etc.) |
| `empire-os/` | 80+ | Full React + Express source code |
| `integrations/dreamco-command-center/` | staged | Command Center merge plan and imported DreamCo systems |
| `workflows.json` | 1 | Automated revenue workflows |

## 🏢 Divisions (45)
- **CommandCore**
- **DreamSalesPro**
- **DreamFinance**
- **DreamRealEstate**
- **DreamAIInfra**
- **DreamRetail**
- **DreamProServices**
- **DreamData**
- **DreamGlobal**
- **DreamAutomation**
- **DreamContent**
- **DreamTrade**
- **DreamFlow**
- **DreamMarket**
- **DreamEmpire**
- **GameTitan**
- **DreamInfluence**
- **DreamDecision**
- **DreamOps**
- **DreamPlanetary**
- **DreamEntFinance**
- **DreamCustIntel**
- **DreamLegal**
- **DreamCyber**
- **DreamHealth**
- **DreamEducation**
- **DreamConstruction**
- **DreamTransport**
- **DreamFood**
- **DreamScience**
- **DreamArts**
- **DreamProtection**
- **DreamAgriculture**
- **DreamMaintenance**
- **DreamProduction**
- **DreamSocial**
- **DreamAdmin**
- **DreamCrypto**
- **DreamPayments**
- **DreamBizLaunch**
- **DreamCodeLab**
- **DreamLoans**
- **DreamPersonalCare**
- **DreamMilitary**
- **DreamAgents**

## 💰 Bot Tiers
- **free**: 0 bots
- **pro**: 0 bots
- **enterprise**: 0 bots
- **elite**: 1 bots

## ⚡ Quick Start

### Python bots
```bash
export OPENAI_API_KEY=your_api_key_here
python python_bots/dream-bot.py
```

### Java bots
```bash
export OPENAI_API_KEY=your_api_key_here
javac java_bots/DreamBot.java && java DreamBot
```

### Full Empire OS web app
```bash
cd empire-os
cp .env.example .env   # fill in your keys
npm install
npm run dev            # runs on http://localhost:5000
```

## 🧠 Learning and Memory
Bot learning is governed by local-first storage, useful-data-only retention, evidence summaries, and approval gates. Do not treat a bot as production-ready unless its implementation, tests, permissions, memory policy, and dashboard status are documented.

## 🤝 Buddy Bot
Buddy is the supervised control plane for routing, dashboard commands, bot testing, failure rebuilds, approval gates, and repository health work.

---
*DreamCo is being consolidated into a reliable, demonstrable AI operating platform.*
