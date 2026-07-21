# Buddy Laptop Setup

Buddy is configured to run on this laptop as a local-first DreamCo command center.

## Start Buddy

- One safe sweep: `python3 tools/local_buddy_runner.py --profile cheap`
- Full local sweep: `python3 tools/local_buddy_runner.py --profile aggressive`
- Background mode: `python3 tools/local_buddy_runner.py --profile aggressive --daemon-start --sleep-minutes 60`
- Status: `python3 tools/local_buddy_runner.py --status`
- Stop: `python3 tools/local_buddy_runner.py --stop`
- Dashboard: `PATH=/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm run dev`

## What Buddy Can Do Locally

- scan and summarize the whole repository
- coordinate all registered bots through Buddy
- run generated bot smoke tests
- run local TypeScript/build/Python/JSON checks
- generate readiness, capability, source-fusion, cost, storage, and revenue-practice reports
- prepare app, website, game, course, simulation, workflow, API, webhook, image, voice, and bot-builder packets
- prepare safe commits and pull request packets
- create repair plans for failed checks
- store only useful reports, test evidence, approvals, and reusable fix recipes

## Approval Required

- paid model calls
- GitHub pushes or pull-request changes
- production deploys
- secrets or credential changes
- money movement, trading, refunds, subscriptions, or customer charges
- customer outreach, social posting, robocalls, or app-store/domain submissions
- legal, medical, financial, credit, employment, tenant, identity, or public-safety decisions
- destructive file operations or overwriting user work

## Key Status Files

- runner_report: `reports/local_buddy_runner_report.json`
- runner_log: `logs/local_buddy_runner/local_buddy_runner.out`
- bot_readiness: `config/generated/bot_end_to_end_readiness/index.json`
- smoke_results: `reports/generated_bot_smoke_results.json`
- unified_workforce: `config/buddy_unified_bot_workforce.json`
- source_fusion: `config/generated/buddy_source_fusion_report.json`
