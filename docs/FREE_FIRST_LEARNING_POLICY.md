# DreamCo Free-First Learning Policy

## Objective

Maximize verified capability gained per unit of time, tokens, memory, compute, energy, and money.

## Resource ladder

1. Existing verified DreamCo capability
2. Cached/local knowledge
3. Local models and available hardware
4. Open-source models and software
5. Available free compute quotas
6. Smallest viable low-cost experiment
7. Paid inference APIs
8. Dedicated GPU hardware
9. Large-scale training

Escalation requires evidence that the next tier can answer an important unresolved question or materially improve a verified capability.

## Learning velocity

Track:

`verified capability gain / resource consumed`

Resources include time, tokens, GPU-hours, VRAM, RAM, energy, and dollars when measurable.

## Experiment portfolio

Maintain separate queues for:

- exploration
- exploitation
- validation
- distillation
- regression

The scheduler can rebalance queues according to expected information gain and resource budget.

## Knowledge reuse

Before creating new training data, a new module, or a new agent, search the capability registry for reusable verified skills. Compose existing capabilities whenever that is cheaper and preserves quality.

## Payment gates

A paid experiment should record:

- why free/local execution is insufficient
- expected information gain
- estimated cost
- exact capability being tested
- success criterion
- fallback/stop condition
- measured result

No automatic spending is authorized merely because a paid resource is available.

## Distillation gate

If a paid or expensive experiment produces a durable improvement, test whether its useful behavior can be distilled into a cheaper local or smaller model before repeating the expensive workload.

## Open-source and licensing

Use only data, code, models, weights, and outputs whose licenses and terms permit the intended use. Keep private credentials, private datasets, restricted prompts, and encryption keys outside public research artifacts.

## Scaling principle

Free-first does not impose a fixed model, bot, module, or capability count. The registry grows according to available resources and verified evidence.
