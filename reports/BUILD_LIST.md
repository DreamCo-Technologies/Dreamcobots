# Build list

Scan of main. 77 sections, 120 duplicate file names. Nothing was deleted. This is not a production approval.

## Run locally

```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
python3 tools/expert_section_scan.py --write
python3 tools/daily_repo_cycle.py
python3 buddy/security/production_checklist.py
python3 tools/production_readiness_gate.py --strict
```

The gate stays `external_config_required` until the host has the secrets. Do not paste secret values into the repo.

## Run on GitHub

1. Open https://github.com/DreamCo-Technologies/Dreamcobots/actions
2. Run Daily health balancer.
3. Read https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/reports/DAILY_PRODUCTION_SCAN.md
4. Paste host values only at https://github.com/DreamCo-Technologies/Dreamcobots/settings/secrets/actions

## Build order

- Keep the owner study path free of weight downloads.
- Store user bots and social labels, not passwords.
- Route a task only when an approved model has a measured score.
- Fill plugin gaps with the local skill buttons.
- Set DATABASE_URL, STRIPE_LIVE_SECRET_KEY, STRIPE_LIVE_PK, STRIPE_WEBHOOK_SECRET, OWNER_BILLING_TOKEN, and OWNER_SECRET_KEY on the host.
- Switch Pages to GitHub Actions.
