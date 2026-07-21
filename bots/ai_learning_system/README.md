# DreamCo Global AI Learning System

An autonomous, self-improving AI pipeline that continuously discovers, evaluates, and deploys the best learning methods from across the global research landscape — powering every DreamCo intelligent bot.

---

## Overview

The AI Learning System monitors arXiv, GitHub, Kaggle, and leading AI labs in real time. It classifies each discovered method, stress-tests it in isolated containers, ranks it against a global performance matrix, and evolves hybrid strategies using a genetic algorithm. The best strategy is then deployed via Kubernetes rolling update to live DreamCo bots.

```
arXiv / GitHub / Kaggle / AI Labs
          │
    ┌─────▼──────┐
    │  Ingestion  │  scrape & normalise records
    └─────┬──────┘
          │
    ┌─────▼──────────┐
    │   Classifier    │  keyword-based ML method detection
    └─────┬──────────┘
          │
    ┌─────▼──────────┐
    │ Sandbox Testing │  containerised benchmarking (PRO+)
    └─────┬──────────┘
          │
    ┌─────▼──────────────┐
    │ Performance Analytics│  global & regional ranking
    └─────┬──────────────┘
          │
    ┌─────▼────────────────┐
    │ Hybrid Evolution Engine│  genetic algorithm (ENTERPRISE)
    └─────┬────────────────┘
          │
    ┌─────▼──────────────────┐
    │ Deployment Orchestrator │  Kubernetes rolling update (PRO+)
    └────────────────────────┘
```

---

## Tier Comparison

| Feature | FREE ($0/mo) | PRO ($199/mo) | ENTERPRISE ($999/mo) |
|---|---|---|---|
| Ingestion jobs / month | 100 | 5,000 | Unlimited |
| Web scraper | ✓ | ✓ | ✓ |
| Method classifier | ✓ | ✓ | ✓ |
| Performance analytics | ✓ | ✓ | ✓ |
| Automation scheduler | ✓ | ✓ | ✓ |
| Sandbox containers | — | 10 | Unlimited |
| Hybrid evolution engine | — | ✓ | ✓ |
| Deployment orchestration | — | ✓ | ✓ |
| Governance & RBAC | — | ✓ | ✓ |
| Kubernetes orchestration | — | — | ✓ |
| Genetic algorithms | — | — | ✓ |
| Support | Community | Email 48 h SLA | Dedicated 24/7 |

---

## Quick Start

```python
from bots.ai_learning_system import AILearningSystem
from bots.ai_learning_system.tiers import Tier

# Instantiate with desired tier
system = AILearningSystem(tier=Tier.PRO)

# Run the full end-to-end pipeline
result = system.run_full_pipeline(query="transformer", top_n=5)
print(result["summary"])

# Inspect tier details
system.describe_tier()
system.show_upgrade_path()

# Check all subsystem stats
status = system.get_system_status()
```

### Ingestion only

```python
from bots.ai_learning_system.ingestion import DataIngestionLayer, DataSourceType
from bots.ai_learning_system.tiers import Tier

ingestion = DataIngestionLayer(Tier.FREE)
records = ingestion.ingest(DataSourceType.ARXIV, query="reinforcement learning")
print(f"Ingested {len(records)} records")
```

### Governance / RBAC

```python
from bots.ai_learning_system.governance import GovernanceLayer, AccessRole
from bots.ai_learning_system.tiers import Tier

gov = GovernanceLayer(Tier.PRO)
gov.enforce("alice", AccessRole.ML_ENGINEER, "sandbox")   # allowed
gov.enforce("bob",   AccessRole.VIEWER,      "ingest")    # raises RBACError
```

---

## Directory Structure

```
bots/ai_learning_system/
├── __init__.py               Package entry point
├── ai_learning_system.py     Main orchestrator (AILearningSystem)
├── tiers.py                  Tier definitions and feature flags
├── ingestion.py              Data ingestion layer
├── classifier.py             Learning method classifier
├── sandbox.py                Sandbox testing layer
├── analytics.py              Performance analytics & ranking
├── hybrid_engine.py          Hybrid evolution engine
├── deployment.py             Deployment orchestrator
├── governance.py             Governance & RBAC layer
├── scheduler.py              Automation scheduler
└── README.md                 This file
```

---

## Data Sources

| Source | Content Types |
|---|---|
| **arXiv** | Research papers |
| **GitHub** | Code repositories |
| **Kaggle** | Datasets & competitions |
| **AI Labs** | Foundation models & reports |

---

## Learning Method Types

The classifier detects and labels the following AI/ML paradigms:

- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning
- Semi-Supervised Learning
- Self-Supervised Learning
- Transfer Learning
- Federated Learning
- Meta-Learning

---

## Running Tests

```bash
pytest tests/test_ai_learning_system.py -v
```
