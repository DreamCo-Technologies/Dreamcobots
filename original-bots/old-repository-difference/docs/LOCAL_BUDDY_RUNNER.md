# Local Buddy Runner

Use the local runner when you want your Mac to do the work instead of spending GitHub Actions minutes.

## Commands

```bash
python3 tools/local_buddy_runner.py --profile cheap
python3 tools/local_buddy_runner.py --profile aggressive
python3 tools/local_buddy_runner.py --profile aggressive --loop-hours 24 --sleep-minutes 60
python3 tools/local_buddy_runner.py --profile aggressive --daemon-start --sleep-minutes 60
python3 tools/local_buddy_runner.py --status
python3 tools/local_buddy_runner.py --stop
```

## What It Does

- Refreshes Buddy reports.
- Runs local checks before remote CI.
- Scans GitHub-cost risks from the repository files.
- Updates local evidence in `reports/local_buddy_runner_report.json`.
- Keeps per-cycle logs in `logs/local_buddy_runner/`.
- Can run aggressive mode in the background until you stop it.

## Hard Limits

The local runner does not do live money movement, outreach, ad spend, credential changes, destructive git actions, production deploys, or paid always-on AI loops. Those stay approval-gated.

## Best Cheap Workflow

1. Run `python3 tools/local_buddy_runner.py --profile cheap` during normal work.
2. Run `python3 tools/local_buddy_runner.py --profile aggressive` before a push or pull request.
3. Use daemon aggressive mode when your laptop is plugged in and you want Buddy running until you cut it off.
4. Check status with `python3 tools/local_buddy_runner.py --status`.
5. Stop it with `python3 tools/local_buddy_runner.py --stop`.
6. Push the generated reports after review.

## Run Until Stopped

```bash
python3 tools/local_buddy_runner.py --profile aggressive --daemon-start --sleep-minutes 60
```

This starts a background process that repeats aggressive local sweeps every hour. It writes:

- current status: `reports/local_buddy_runner_report.json`
- rolling logs: `logs/local_buddy_runner/`
- process id: `.local_buddy_runner.pid`

Stop it:

```bash
python3 tools/local_buddy_runner.py --stop
```
