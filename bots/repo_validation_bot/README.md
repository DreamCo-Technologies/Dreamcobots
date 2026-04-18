# Repo Validation Bot

Scans every bot directory in the DreamCo repository to ensure structural
correctness and proper `app` export configuration.

## What it checks

| Check | Description |
|-------|-------------|
| Required files | `main.py` / `index.js` / `bot.py` and `README.md` must be present |
| `__init__.py` | Python bots should include an `__init__.py` (warning if missing) |
| `app` export | Python entry-point files that instantiate Flask/FastAPI must assign the instance to `app`, not `application`, `flask_app`, etc. |

## Usage

```bash
# Plain-text report
python bots/repo_validation_bot/repo_validation_bot.py --root .

# JSON report
python bots/repo_validation_bot/repo_validation_bot.py --root . --json
```

Exit code `0` = all bots pass. Exit code `1` = one or more failures.

## Integration

The bot is imported by `ai/debug_bot.py` and runs automatically as part of
the **Repo Validation** GitHub Actions workflow on every push and pull request
to `main`.
