# Buddy AI Agent Model Library

Buddy needs a model router that knows more than one provider and more than one prompt style. This library gives Buddy a governed catalog for prompts, tools, agent types, task routes, and 100 model-resource candidates.

## What It Tracks

- Prompt types: task briefs, tool contracts, structured outputs, eval rubrics, visual prompts, workflow plans, handoffs, and safety checks.
- Tool types: code editing, tests, browser research, APIs, webhooks, vector search, media generation, payments, notifications, and approval gates.
- Agent types: planner, researcher, coder, debugger, workflow, sandbox eval, creative studio, sales, data, security, legal safety, memory curator, and model router agents.
- Model resources: 100 quality, fast, budget, and private/local routes across 25 model families.
- Task routes: how Buddy chooses a primary model resource and fallbacks for coding, research, image, video, music, voice, dashboards, workflows, simulations, and deployments.

## Important Rule

Provider model IDs, prices, and availability change often. The generated report is a routing and evaluation library, not a promise that every provider model ID is currently enabled in production. Buddy must verify the provider docs and approved credentials before using any resource live.

## Commands

```bash
npm run report:ai-agent-model-library
npm run check:ai-agent-model-library
```

## Why This Matters

This lets Buddy pick the best AI path for each bot and task:

- strong reasoning for architecture and production decisions
- fast models for repeated sandbox loops
- budget models for low-risk batch work
- private/local routes for sensitive inputs
- image, video, voice, music, and search routes for creative and client work
- evals and approval gates before risky actions
