This directory contains all active bot scripts and automation tools for the DreamCobots platform.

## Available Bots

| Bot | Description |
|-----|-------------|
| [government-contract-grant-bot](government-contract-grant-bot/) | Automates SAM.gov contract & grant searches and proposal generation |
| [211-resource-eligibility-bot](211-resource-eligibility-bot/) | Finds local social services and checks program eligibility |
| [selenium-job-application-bot](selenium-job-application-bot/) | Automates job searching and applications on Indeed, LinkedIn, Glassdoor |
| [ai-side-hustle-bots](ai-side-hustle-bots/) | AI-powered tools to identify and monetize side hustle opportunities |

## Configuration

Each bot reads settings from its own `config.json` or environment variables. The shared `config.json` in this directory contains common settings:

```json
{
  "api_keys": {},
  "notifications": {},
  "integrations": {}
}
```

## Specialization contracts and tracking

Generated specialization contracts for every bot profile are tracked in:

- `/home/runner/work/Dreamcobots/Dreamcobots/config/generated/bot_specializations.json`
- `/home/runner/work/Dreamcobots/Dreamcobots/config/generated/bot_specialization_tracking.json`

Regenerate or validate with:

```bash
python3 /home/runner/work/Dreamcobots/Dreamcobots/tools/generate_bot_specializations.py
python3 /home/runner/work/Dreamcobots/Dreamcobots/tools/generate_bot_specializations.py --check
```

## Adding a New Bot

1. Create a new directory under `bots/` using kebab-case naming.
2. Add a `bot.py` entry point.
3. Add a `README.md` with setup, usage, and deployment instructions.
4. Add a `requirements.txt` with dependencies.
5. Add a `Dockerfile` for containerized deployment.
