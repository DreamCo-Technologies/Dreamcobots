# Capability-First Developer Guide

## The architectural decision

DreamCo should preserve its bot ecosystem while moving the canonical engineering model toward capabilities.

A **capability** is a reusable unit of behavior that can be tested, benchmarked, composed, versioned, and improved independently.

A **bot/agent** is a composition of capabilities plus instructions, memory, tools, model selection, policies, and an execution strategy.

## Example

```text
Real Estate Agent
├── property discovery
├── public-record research
├── comparable-property analysis
├── valuation reasoning
├── lead qualification
├── CRM management
├── outreach generation
├── follow-up scheduling
├── document analysis
└── reporting
```

The individual capabilities should not be duplicated simply because multiple agents need them.

## Why this helps DreamCo

- Fewer duplicated implementations
- Easier testing
- Easier benchmarking
- Faster agent construction
- Shared improvements propagate to every compatible agent
- Capability gaps become measurable
- Developers can contribute one capability without understanding the whole bot fleet
- Users can assemble specialized AI systems from proven building blocks

## Bot preservation rule

Existing bots remain valuable source records. Migration is additive and lossless. A bot may expose hundreds of capabilities, and every one must remain traceable to its original source and evidence.

## Developer workflow

1. Search before creating.
2. Identify whether the behavior already exists.
3. If it exists, improve the canonical capability.
4. If it is new, create a capability contract first.
5. Add executable tests.
6. Add benchmark/holdout tasks when appropriate.
7. Connect the capability to the originating bot or agent.
8. Record dependencies and provenance.
9. Let Buddy evaluate it in the sandbox.
10. Promote only after evidence exists.

## What developers should be able to build

A contributor should eventually be able to add:

```text
one capability
    ↓
tests + benchmark
    ↓
capability registry
    ↓
Buddy sandbox
    ↓
multiple agents can reuse it
```

That is the core mechanism for turning a large bot repository into an AI capability platform.
