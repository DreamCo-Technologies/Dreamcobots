# Grok help catalog + suggestions index

| Document | Path |
|----------|------|
| What Grok can do | [docs/GROK_CAPABILITIES_FOR_DREAMCO.md](../docs/GROK_CAPABILITIES_FOR_DREAMCO.md) |
| Improvement suggestions | [docs/REPOSITORY_IMPROVEMENT_SUGGESTIONS.md](../docs/REPOSITORY_IMPROVEMENT_SUGGESTIONS.md) |
| Bot production readiness policy | [docs/BOT_PRODUCTION_READINESS.md](../docs/BOT_PRODUCTION_READINESS.md) |
| Issue cleaner | [tools/issue_cleaner/README.md](../tools/issue_cleaner/README.md) |
| Agent rules | [AGENTS.md](../AGENTS.md) |

## Quick commands

```bash
python3 tools/ensure_bots_production_ready.py
python3 tools/issue_cleaner/clean_issues.py  # needs GH_TOKEN + GITHUB_REPOSITORY
```

## Actions workflows added for ops

- `Intelligent Issue Cleaner` — hourly CI issue noise reduction
- `Bot Production Readiness` — profile completeness across fleet
