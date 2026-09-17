# Reasoning techniques & learning strategies

Discover, test, select, and package (sell) the full DreamCo catalog.

## Commands

```bash
# Run structure tests (default)
python3 buddy/learning/reasoning_and_learning_registry.py

# Discover all IDs
python3 buddy/learning/reasoning_and_learning_registry.py discover

# Search
python3 buddy/learning/reasoning_and_learning_registry.py search evidence failure

# Select for a task
python3 buddy/learning/reasoning_and_learning_registry.py select "debug failing CI"

# Marketplace packs
python3 buddy/learning/reasoning_and_learning_registry.py sell

# Unit tests
python3 -m unittest buddy.learning.reasoning_and_learning_registry_test
# or from this directory:
cd buddy/learning && python3 reasoning_and_learning_registry_test.py
```

## Catalogs

| File | Contents |
|------|----------|
| `reasoning_techniques_catalog.json` | 20 techniques (CoT, ToT, ReAct, evidence-first, …) |
| `learning_strategies_catalog.json` | 20 strategies (spaced repetition, error analysis, continuous cycle, …) |

## Sell (honest)

Marketplace packs are **catalog SKUs**, not automatic mastery:

- free / pro / enterprise / elite tier packs
- complete library pack

Each pack lists technique IDs, strategy IDs, price hints, and inclusions. Production promotion still needs sandbox evidence + owner approval (see `continuous_learning_policy.md`).

## Integration

- Buddy task routing can call `select_for_task(user_text)` for recommended techniques
- Bootcamp lessons can reference strategy IDs
- Bot `learningPlan` entries can cite strategy IDs
- Failure learning should prefer `error_analysis` + `failure_memory`

## Truth boundary

Catalogued ≠ production-proven. Tests verify structure, uniqueness, selector, and search — not that every bot runtime executes every technique live.
