# Buddy Autonomy & Model Complementation

Buddy's autonomy program complements the protected DreamCo model fleet. The original DreamCo model catalog is never removed by the OpenRouter integration.

## Fleet layers

1. **Protected DreamCo catalog** — the existing model fleet remains intact and remains a source of benchmark truth.
2. **OpenRouter supplemental gateway** — provides additional models/providers, routing and fallbacks without replacing the protected catalog.
3. **DreamCo bots** — existing specialists remain available as teachers, validators and fallbacks.
4. **Buddy-native capabilities** — capabilities are progressively reproduced, tested and consolidated inside Buddy.

## Learning loop

`discover -> delegate -> capture evidence -> reproduce -> benchmark -> validate -> promote -> shadow-test -> recommend migration`

Buddy should minimize unnecessary external calls, not blindly minimize the number of available models. Unique capabilities and resilience reserves remain protected.

## Independence metrics

- `external_dependency_ratio`: external model/bot calls divided by eligible completed tasks.
- `native_capability_coverage`: capabilities meeting the native quality/evidence threshold.
- `native_success_rate`: validated Buddy-native task success rate.
- `teacher_calls_per_task`: average external teaching calls required for a task.
- `cost_per_successful_task`: total inference/tool cost divided by successful tasks.
- `regression_rate`: previously mastered capabilities that fail regression tests.

## Governance

A model or bot is never deleted merely because Buddy performed well once. Promotion requires repeated evidence. Replacement uses shadow testing and regression checks. Production retirement requires explicit policy approval and a preserved fallback for unique or critical capabilities.

External training data must be authorized for the intended use. Secrets and credentials must never enter training artifacts, and client data must follow applicable DreamCo consent/retention policies.
