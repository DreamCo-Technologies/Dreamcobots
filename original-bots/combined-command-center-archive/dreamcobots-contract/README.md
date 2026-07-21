# Dreamcobots contract — staging directory

These files are the **source of truth for the bot contract**. They live in this Command Center workspace because the Command Center's `lib/db` Zod schema must match. They should be **copied into the [Dreamcobots](https://github.com/DreamCo-Technologies/Dreamcobots) repo** as fresh, conflict-free PRs.

## What to push to Dreamcobots

| Source (this repo)                                       | Destination (Dreamcobots repo)                |
| -------------------------------------------------------- | --------------------------------------------- |
| `dreamcobots-contract/bot.manifest.schema.json`          | `bot.manifest.schema.json`                    |
| `dreamcobots-contract/.github/copilot-instructions.md`   | `.github/copilot-instructions.md`             |
| `dreamcobots-contract/.github/workflows/validate-bot-pr.yml` | `.github/workflows/validate-bot-pr.yml`   |
| `dreamcobots-contract/.github/workflows/auto-merge-intake.yml` | `.github/workflows/auto-merge-intake.yml` |
| `dreamcobots-contract/bots/<name>/`                      | `bots/<name>/` (one PR per bot)               |

## Recommended PR sequence

1. **PR `infra/bot-contract`** — push the schema + Copilot instructions + both workflows in one PR labeled `infra`.
2. **PRs `bot/ai_enablement_hub`, `bot/elite_scraper`, `bot/company_lookup`, `bot/god_mode_autocloser`, `bot/auto_client_hunter`, `bot/payment_autocollector`** — one PR each, copying that bot's folder verbatim. Each one is single-folder and contract-compliant, so `auto-merge-intake` will land them automatically.

## Why this layout

The Command Center's `lib/db/src/schema/bot_manifest.ts` Zod schema is the **machine-readable mirror** of `bot.manifest.schema.json`. Keep them in lockstep — if you change one, change the other in the same Command Center PR so `/bots` and `/divisions` keep validating correctly.
