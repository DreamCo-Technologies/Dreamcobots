# Buddy Bot Connections

Buddy now has an all-bot connection guard.

## What it verifies

- Every inventory bot has the fields Buddy needs to route it.
- Every bot can create an Actions page sandbox test packet.
- Every bot has a customized resource kit with at least 100 resources.
- High-risk bots keep approval gates before live money, outreach, deploy, or credential actions.

## Commands

```bash
npm run check:buddy-bot-connections
```

This generates:

- `reports/BUDDY_BOT_CONNECTION_REPORT.md`
- `reports/buddy_bot_connection_report.json`

## Actions page

The Actions page shows Buddy all-bot connection proof inside the **Buddy and bot test catalog** section. Use **Test Buddy** or **Test selected bot** to prepare sandbox test packets through Buddy.
