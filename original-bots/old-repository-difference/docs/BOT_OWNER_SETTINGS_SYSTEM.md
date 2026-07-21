# Bot Owner Settings System

Every DreamCo bot is treated as a supervised business owner. High-risk or previously blocked bots are not excluded from work; they are enabled for safe research, drafting, testing, packaging, and approval-packet preparation.

## Default Mode

Bots start in safe mode:

- Business owner mode on.
- Sandbox testing on.
- Contract discovery on.
- Data package mode on.
- People lookup safe mode on.
- Outreach off.
- Paid actions off.
- Production deploy off.
- Money movement off.
- Third-party account mutations off.

## Guardrail

Settings switches expose what a bot may prepare or request. They do not bypass owner approval. Live actions such as outreach, spending, production deploys, money movement, store submissions, people contact, and regulated claims require approval and audit evidence.

## Commands

```bash
npm run report:bot-owner-settings
npm run check:bot-owner-settings
```
