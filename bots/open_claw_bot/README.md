# Open Claw Bot

AI-powered Open Claw strategy generation bot for the DreamCobots ecosystem.

## Overview

Open Claw Bot analyses market and operational data and generates ranked
strategies for DreamCobots bots and human clients.  It uses a suite of
AI/ML models (trend prediction, risk classification, signal generation,
ensemble ranking, NLP advice) and supports per-client customisation.

## Features

| Module | Description |
|---|---|
| **Strategy Engine** | Generates ranked strategies: aggressive, balanced, conservative, scalping, long-term, arbitrage, momentum, mean-reversion |
| **AI Model Hub** | TrendPredictor, RiskClassifier, SignalGenerator, EnsembleRanker, NLPAdvisor — all ready out of the box |
| **Client Manager** | Per-client profiles with risk preferences, goals, and custom strategy rules |
| **Scenario Simulation** | Monte-Carlo-style simulation of strategy performance under market conditions |
| **Data Ingestion** | Feed real-time or historical data points into the analysis buffer |

## Tiers

| Tier | Price | Max Clients | Analyses/Day |
|---|---|---|---|
| Free | $0/month | 3 | 5 |
| Pro | $49/month | 50 | Unlimited |
| Enterprise | $199/month | Unlimited | Unlimited |

## Quick Start

```python
from bots.open_claw_bot import OpenClawBot, Tier

bot = OpenClawBot(tier=Tier.PRO)

# Add a client
client = bot.add_client("Alice", "alice@example.com", max_risk_pct=8.0)

# Generate a strategy for the client
strategy = bot.generate_strategy(
    name="Alice Growth Strategy",
    strategy_type="balanced",
    risk_level="medium",
    client_id=client.client_id,
)
print(f"Strategy: {strategy.name}")
print(f"Expected ROI: {strategy.expected_roi_pct}%  Confidence: {strategy.confidence_score:.0%}")

# Analyse trend from data series
result = bot.analyse_trend([100, 105, 110, 108, 115, 120])
print(result.explanation)

# Generate trading signals
signals = bot.get_signals({"price": 115, "moving_avg": 108, "rsi": 62})
print(signals.prediction)

# Simulate a scenario
sim = bot.simulate_scenario(
    strategy.strategy_id,
    {"volatility": 0.3, "trend": 0.1, "volume": 1.2},
)
print(sim)

# Chat interface (BuddyAI compatible)
response = bot.chat("Generate an aggressive strategy for crypto")
print(response["message"])

# Register with BuddyAI orchestrator
from BuddyAI.buddy_bot import BuddyBot
orchestrator = BuddyBot()
bot.register_with_buddy(orchestrator)
```

## Directory Structure

```
bots/open_claw_bot/
├── open_claw_bot.py     # Main OpenClawBot class
├── tiers.py             # FREE/PRO/ENTERPRISE tiers
├── strategy_engine.py   # Strategy generation, ranking, lifecycle
├── ai_models.py         # AI/ML model hub and inference
├── client_manager.py    # Client profiles and customisation
├── __init__.py
└── README.md
```
