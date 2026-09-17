# Intelligent Issue Cleaner

Hourly job that cleans up to **500 open issues** per run on DreamCo-Technologies/Dreamcobots.

## What it does

| Rule | Action |
|------|--------|
| `Actions run <id> failed: <workflow>` | Keep newest **2** per workflow; close older as superseded |
| `DreamCo failure root cause [key]: ...` | Keep **1** per key; close older as duplicate |
| Human issues | Never auto-close |
| Survivors | Label `ci-failure` / `ci:workflow` |

## Schedule

- Cron: every hour at :17 UTC
- Manual: Actions → **Intelligent Issue Cleaner** → Run workflow
  - Optional: `dry_run=true` first

## Throughput

~500 issues/hour. Pair with reducing how often Failure Sweep opens new per-run issues.
