# High-Risk Bot Approvals

High-risk bots are coded and smoke-tested, but they cannot run live money-related,
regulated, legal, medical, security, loan, tax, crypto, trading, or payment actions
until the user explicitly approves them through Buddy.

## Required User Request

The user must ask Buddy:

```text
Buddy, help me make money with this bot. I approve the listed live actions and understand the risks.
```

## Approval Registry

Approvals live in:

```text
config/production_approvals/high_risk_bot_approvals.json
```

Every high-risk bot defaults to `approved: false`.

## Approval Checklist

Before a bot is approved, confirm:

- The generated smoke test passed.
- No live money movement is allowed without final user confirmation.
- Secrets and API keys are environment-only.
- Audit logging is enabled.
- Human review is required before external action.
- Allowed live actions are listed explicitly.

## Commands

Regenerate the approval registry:

```bash
npm run generate:high-risk-approvals
```

Approve one bot:

```bash
npm run approve:high-risk-bot -- \
  --slug payment_autocollector \
  --approved-by "Irean Jordan" \
  --buddy-request "Buddy, help me make money with this bot. I approve the listed live actions and understand the risks." \
  --allow "draft_dunning_sequence" \
  --allow "prepare_invoice_recovery_plan"
```

Refresh readiness after approvals:

```bash
npm run generate:buddy-inventory
```

Only bots with valid approval evidence can move from
`production_candidate_approval_required` to `production_ready`.
