# Buddy Free Local Test Kit

Make Buddy testable in free/local-first mode before using paid services or live account actions.

## Free-First Policy

- default_mode: `free_local_first`
- use_cloud_by_default: `false`
- use_paid_model_calls_by_default: `false`
- use_github_actions_by_default: `false`
- store_secret_values_in_repo: `false`
- live_actions_require_approval: `true`

## Test Commands

### Laptop setup verification

- Cost: `free_local`
- Proves: Buddy can validate local setup, safety policy, autonomy config, bot readiness, and smoke tests.

```bash
python3 tools/setup_buddy_laptop.py
```

### Quick free sweep

- Cost: `free_local`
- Proves: Buddy can run low-cost reports and checks without cloud minutes.

```bash
python3 tools/local_buddy_runner.py --profile cheap
```

### Autonomous everything catalog

- Cost: `free_local`
- Proves: Every connected bot/division is represented in the governed autonomy queue.

```bash
python3 tools/generate_buddy_autonomous_everything.py --check
```

### Generated bot smoke tests

- Cost: `free_local`
- Proves: Generated bot contracts can be discovered and smoke-tested locally.

```bash
python3 tools/run_generated_bot_smoke.py
```

### Dashboard TypeScript check

- Cost: `free_local`
- Proves: The dashboard code compiles with the bundled local runtime.

```bash
PATH=/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm run check
```

### Open local dashboard

- Cost: `free_local`
- Proves: Buddy can be tested through the local app without deploying.

```bash
PATH=/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm run dev
```

## Approval Required Before Anything Paid Or Live

- paid model calls
- production deploys
- domain purchases
- app-store submissions
- payment account changes
- customer charges, refunds, payouts, or transfers
- secret creation or rotation
- external account signups
- granting repository, cloud, payment, email, or social access
- sending outreach, calls, messages, proposals, bids, or social posts

## Current Inventory

- Bots connected to queue: 1331
- Divisions connected to queue: 46
