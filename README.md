# 🤖 DreamCo Empire OS — Bot Repository

> **1 AI bots · 3 divisions · Self-learning · Revenue-generating · Fully deployed on DreamCo**

[![🪐 Command Tower](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/command-tower.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/command-tower.yml)
[![💰 Revenue Engine](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/revenue_engine.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/revenue_engine.yml)
[![🛡️ Framework Compliance](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/framework-compliance.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/framework-compliance.yml)
[![🧠 Auto-Retrain](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/auto-retrain.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/auto-retrain.yml)
[![🔥 Chaos Testing](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/chaos-testing.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/chaos-testing.yml)
[![🤝 Bot Submission CI](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/bot-submission.yml/badge.svg)](https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/bot-submission.yml)
![Active Bots](https://img.shields.io/badge/Active%20Bots-1-blue?logo=robot&logoColor=white)
![Divisions](https://img.shields.io/badge/Divisions-3-purple?logo=building&logoColor=white)
![Tiers](https://img.shields.io/badge/Tiers-free%20%7C%20pro%20%7C%20enterprise%20%7C%20elite-gold)
![Revenue Target](https://img.shields.io/badge/Revenue%20Target-%24500%2Fday-green?logo=stripe&logoColor=white)

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

## 🏢 Divisions (3)
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
export OPENAI_API_KEY=sk-...
python python_bots/dream-bot.py
```

### Java bots
```bash
export OPENAI_API_KEY=sk-...
javac java_bots/DreamBot.java && java DreamBot
```

### Full Empire OS web app
```bash
cd empire-os
cp .env.example .env   # fill in your keys
npm install
npm run dev            # runs on http://localhost:5000
```

## 🧠 Self-Learning System
Every bot logs learnings after each conversation using the `SELF_LEARNING_PROMPT` protocol. Memory is stored per-bot in PostgreSQL and injected at the start of every new session.

## 🤝 Buddy Bot
The master coding brain covering 500+ libraries. Every other bot routes coding tasks through Buddy Bot automatically.

---
*Synced from DreamCo Empire OS on DreamCo — Autonomous wealth generation at scale*
