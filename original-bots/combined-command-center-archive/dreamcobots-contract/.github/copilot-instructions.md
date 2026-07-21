# Copilot instructions — Dreamcobots

You are contributing bots to **Dreamcobots**, a parallel bot factory. Every PR must follow the **bot contract** so it merges without conflicts.

## The one rule

**One PR = one new folder under `bots/<name>/` = one `bot.manifest.json`. Never touch shared files.**

## What "shared files" means (do not edit)

- Workflows (`.github/workflows/**`)
- Registries, catalogues, or aggregator files at the repo root
- Other bots under `bots/**` (different folder)
- The schema file `bot.manifest.schema.json`
- Top-level config (`package.json`, `pyproject.toml`, `requirements.txt`, `pnpm-workspace.yaml`)

If you believe a shared file genuinely needs to change, open a separate PR labeled `infra` and explain why. CI will block any non-`infra` PR that touches shared files.

## Template for a new bot

```
bots/<new_bot_name>/
├── bot.manifest.json    # REQUIRED, validates against ../../bot.manifest.schema.json
├── README.md            # what the bot does, how to run it
└── src/                 # bot code (any language matching entrypoint.runtime)
```

### `bot.manifest.json` minimal example

```json
{
  "manifestVersion": "1",
  "name": "my_new_bot",
  "displayName": "My New Bot",
  "description": "One-sentence description of what this bot does for the user.",
  "division": "DreamSalesPro",
  "tier": "PRO",
  "category": "Lead Generation",
  "capabilities": ["scrape_linkedin", "enrich_email"],
  "entrypoint": {
    "runtime": "python",
    "command": "python -m my_new_bot.main",
    "workdir": "src"
  },
  "revenueModel": { "type": "subscription", "targetMrr": 2500, "currency": "USD" },
  "dependencies": ["requests", "beautifulsoup4"],
  "owner": { "team": "DreamSalesPro", "githubHandles": ["@your-handle"] },
  "status": "draft",
  "tags": ["b2b", "outbound"]
}
```

Allowed `division` values: `DreamRealEstate`, `DreamSalesPro`, `DreamFinance`, `DreamAI`, `DreamSoft`, `DreamGov`, `DreamMedia`, `DreamOps`.

## Why this matters

The Command Center auto-discovers bots by reading their `bot.manifest.json`. When you follow this contract:

- Your PR merges automatically the moment it passes validation.
- Your bot shows up in `/bots` and `/divisions` with no follow-up work.
- You never collide with another Copilot PR.

If you violate the contract, the `validate-bot-pr` check fails and you'll be asked to rewrite. Don't try to be clever — the lane is narrow on purpose.
