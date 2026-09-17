# Bot production readiness

## What “production ready” means here

DreamCo separates **profile completeness** from **runtime production**:

| Layer | Meaning |
|-------|--------|
| **Profile complete** | `App_bots` JSON has required fields; `bots/<slug>.md` exists; tools, learning, tasks, system prompt, sample sandbox test present |
| **Runtime production** | Adapters configured, sandbox checks pass, auth scoped, deployment telemetry verified |

The fleet generator historically sets `production_ready: false` until evidence exists. This toolkit does **not** flip that flag without checklist evidence.

## Required `App_bots` fields

From `config/bot-accounting-placement-program.json`:

- `slug`
- `displayName`
- `category`
- `description`
- `capabilities`
- `status`

## Production pack (added when missing)

- `tier`, `revenueModel`, `targetUsers`, `priceRange`
- `toolsNeeded`
- `benchmarks`
- `learningPlan`
- `tasks`
- `systemPrompt`
- `sample_test_prompt`
- `production` object with gate + checklist

## Specialty markdown

Each bot should have `bots/<slug>.md` with mission, capabilities, tools, learning, tasks, and system prompt.

## How to run

```bash
# Fill gaps and write markdown
python3 tools/ensure_bots_production_ready.py

# Audit only
python3 tools/ensure_bots_production_ready.py --check
```

Or: **Actions → Bot Production Readiness → Run workflow** (`apply` or `check`).

## Outputs

- `reports/BOT_PRODUCTION_READINESS.md`
- `config/generated/bot-production-readiness.json`
