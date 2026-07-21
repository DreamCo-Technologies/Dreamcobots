# Contributing to DreamCObots

Thank you for contributing to the DreamCObots project. This repository operates as a production-grade AI orchestration system. All contributions — human or automated — must strictly follow the framework below.

---

## Table of Contents
* Code of Conduct
* GLOBAL AI SOURCES FLOW (Mandatory Architecture)
* How to Add a New Bot
* Required Framework Integration Checklist
* Testing Requirements
* Static Analysis
* Pull Request Process

---

## Code of Conduct

All contributors are expected to act respectfully and constructively.

* No harassment, discrimination, or exclusionary behavior
* Maintain professional, technical communication
* Focus on system stability, correctness, and improvement
* All contributions must align with the platform architecture

Violations may result in rejection of contributions or access restrictions.

---

## GLOBAL AI SOURCES FLOW (Mandatory Architecture)

Every bot in the repository must implement the GLOBAL AI SOURCES FLOW pipeline located in:

`framework/global_ai_sources_flow.py`

This pipeline is not optional. It is required for all bots.

### GLOBAL AI SOURCES FLOW Architecture

```
GLOBAL AI SOURCES
┌─────────────────────────────────────────────┐
│ Research Papers │ GitHub │ Kaggle │ AI Labs │
│ US │ China │ India │ EU │ Global Labs       │
└─────────────────────────────────────────────┘
                      ↓
        DATA INGESTION LAYER
        - Scrapers + Parsers
        - Dataset normalization
        - Language translation
                      ↓
        LEARNING METHOD CLASSIFIER
        - Supervised / Unsupervised
        - Reinforcement / Self-supervised
        - Multi-modal / Transfer / Federated
                      ↓
        SANDBOX TEST LAB
        - Containerized testing
        - Model vs model evaluation
        - A/B + adversarial testing
                      ↓
        PERFORMANCE ANALYTICS
        - Accuracy / cost / speed metrics
        - Global learning matrix
                      ↓
        HYBRID EVOLUTION ENGINE
        - Genetic algorithms
        - Reinforcement optimization
        - Hybrid model generation
                      ↓
        DEPLOYMENT ENGINE
        - Push validated improvements
        - Continuous retraining
                      ↓
        PROFIT & MARKET INTELLIGENCE
        - Real estate, trading, lead gen
        - Commercial optimization systems
                      ↓
        GOVERNANCE + SECURITY
        - Encryption
        - Audit logging
        - Compliance + AI safety controls
```

#### Why This Matters

This pipeline ensures:

* All data sources are globally traceable
* Learning methods are explicitly classified
* Every model is sandbox-tested before deployment
* Performance is consistently measurable
* Models evolve through hybrid optimization (genetic + RL)
* Continuous retraining is enforced
* Outputs feed directly into monetization systems
* Governance and safety are always active

---

## How to Add a New Bot

1. **Create Bot Directory**
   ```
   bots/<your-bot-name>/
   ```

2. **Import Framework**
   ```python
   from framework import GlobalAISourcesFlow
   ```

3. **Initialize Flow in Bot**
   ```python
   class MyBot:
       def __init__(self):
           self.flow = GlobalAISourcesFlow(bot_name="MyBot")
   ```

4. **Run Pipeline During Execution**
   ```python
   result = self.flow.run_pipeline(
       raw_data={
           "domain": "my_domain",
           "input": payload
       },
       learning_method="supervised"
   )
   ```

5. **Add Documentation**
   Include a `README.md` in the bot directory:
   * Purpose of the bot
   * Input/output behavior
   * Learning method used
   * Execution instructions

6. **Add Tests**
   Create:
   ```
   tests/test_<your_bot_name>.py
   ```

---

## Required Framework Integration Checklist

Before submitting a PR:

* `from framework import GlobalAISourcesFlow` is present
* `self.flow = GlobalAISourcesFlow(...)` is initialized in `__init__`
* `self.flow.run_pipeline(...)` is executed in runtime logic
* `self.flow.validate()` passes successfully
* All 8 REQUIRED_STAGES exist in pipeline validation
* Governance security settings remain enabled:
  * `encryption_enabled = True`
  * `audit_logs_enabled = True`
  * `ai_safety_controls_enabled = True`

---

## Testing Requirements

All bots must include tests:

**Minimum requirements:**

* Bot initializes successfully
* `self.flow` exists on instantiation
* `self.flow.validate()` returns `True`
* `self.flow.run_pipeline()` returns:
  ```json
  {"pipeline_complete": true}
  ```

Run tests:
```bash
python -m pytest tests/ -v
```

---

## Static Analysis

All bots are validated using:
```bash
python tools/check_bot_framework.py
```

### This tool enforces:
* Presence of `GlobalAISourcesFlow` usage
* Framework compliance across all bot directories
* Detection of non-compliant bot implementations

### Scanned Directories
* `bots/`
* `Business_bots/`
* `App_bots/`
* `Marketing_bots/`
* `Occupational_bots/`
* `Real_Estate_bots/`
* `Fiverr_bots/`

---

## Pull Request Process

1. Fork repository
2. Create feature branch
3. Add or modify bot following framework rules
4. **Run static analysis:**
   ```bash
   python tools/check_bot_framework.py
   ```

5. **Run tests:**
   ```bash
   python -m pytest tests/ -v
   ```

6. Open PR with:
   * Bot purpose
   * Architecture explanation
   * Learning method used
   * Any performance considerations

---

## Final Rule

No bot will be merged unless it fully implements the `GLOBAL AI SOURCES FLOW` pipeline and passes both:

* Static analysis
* Full test suite