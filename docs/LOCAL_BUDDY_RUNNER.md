# Local Buddy Runner

Use the local runner when you want your Mac to do the work instead of spending GitHub Actions minutes.

## Commands

```bash
python3 tools/local_buddy_runner.py --profile cheap
python3 tools/local_buddy_runner.py --profile aggressive
python3 tools/local_buddy_runner.py --profile aggressive --loop-hours 24 --sleep-minutes 60
```

## What It Does

- Refreshes Buddy reports.
- Runs local checks before remote CI.
- Scans GitHub-cost risks from the repository files.
- Updates local evidence in `reports/local_buddy_runner_report.json`.
- Keeps per-cycle logs in `logs/local_buddy_runner/`.

## Hard Limits

The local runner does not do live money movement, outreach, ad spend, credential changes, destructive git actions, production deploys, or paid always-on AI loops. Those stay approval-gated.

## Best Cheap Workflow

1. Run `python3 tools/local_buddy_runner.py --profile cheap` during normal work.
2. Run `python3 tools/local_buddy_runner.py --profile aggressive` before a push or pull request.
3. Use the 24-hour loop only when your laptop is plugged in.
4. Push the generated reports after review.
