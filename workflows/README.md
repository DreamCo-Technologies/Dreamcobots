# DreamCo Workflow System

The `workflows/` directory contains the declarative automation pipelines that drive every DreamCo money-making engine.  Each workflow is a self-contained JSON file that describes **what** to do, **when** to trigger it, **how** to monetize it, and **how** to recover from failures.

---

## Workflow File Structure

```json
{
  "id": "workflow_id",
  "name": "Human-readable name",
  "description": "What this workflow does",
  "trigger": {
    "type": "cron | webhook | manual",
    "schedule": "cron expression (e.g. '0 */6 * * *')",
    "endpoint": "/webhook/path (for webhook triggers)"
  },
  "steps": [ ... ],
  "monetization": { ... },
  "automation": { ... },
  "created_at": "ISO timestamp",
  "version": "semver"
}
```

### Step Schema

```json
{
  "id": "step_id",
  "name": "Step Name",
  "action": "module.method",
  "params": { "key": "value" },
  "on_success": "next_step_id",
  "on_failure": "error_handler_step_id"
}
```

Each step calls an `action` — a dot-notation reference to `module.method`.  The orchestrator resolves this against the bot registry.  `on_success` and `on_failure` control branching.

### Monetization Schema

```json
{
  "model": "service_sales | deal_commission | trading_profits | grant_awards | contingency_fee",
  "revenue_per_cycle": 350,
  "affiliate_programs": ["program_name"],
  "payment_processor": "stripe | paypal"
}
```

### Automation Schema

```json
{
  "retry_attempts": 3,
  "timeout_seconds": 300,
  "notify_on_completion": true
}
```

---

## Available Workflows

| File | ID | Trigger | Est. Revenue/Cycle |
|------|-----|---------|-------------------|
| `fiverr.json` | `fiverr` | Every 6 hours | $350 |
| `real_estate.json` | `real_estate` | Daily at 8am | $15,000 |
| `grants.json` | `grants` | Weekly (Mondays) | $50,000 |
| `legal_money.json` | `legal_money` | Mon/Wed/Fri at 9am | $8,500 |
| `crypto.json` | `crypto` | Every 15 minutes | $450 |

---

## Running Workflows

### Via the API
```bash
# Trigger a workflow manually
curl -X POST http://localhost:3000/api/workflows/fiverr/run

# Get workflow status
curl http://localhost:3000/api/workflows/fiverr/status

# List all workflows
curl http://localhost:3000/api/workflows
```

### Via the Orchestrator
```js
const { runWorkflow } = require('./DreamCo/orchestrator');
runWorkflow('fiverr');
```

### Via Cron
The `cron/run_bots.js` scheduler automatically triggers all enabled workflows based on their `trigger.schedule`.

---

## The Global Registry

`workflows.json` (root) is the master registry.  Only workflows listed here and marked `"enabled": true` will be picked up by the scheduler.

```json
{
  "version": "1.0.0",
  "workflows": [
    { "id": "fiverr", "file": "workflows/fiverr.json", "enabled": true, "priority": 1 }
  ]
}
```

---

## Adding a New Workflow

1. Copy `fiverr.json` as a template
2. Change `id`, `name`, `description`
3. Define your `steps` — each step must have a unique `id` and valid `action`
4. Set `monetization.model` and `revenue_per_cycle`
5. Register it in `workflows.json`
6. Add tests in `__tests__/workflows.test.js`

---

## Error Handling

Every workflow should have an `error_handler` step as the final fallback.  The orchestrator will call this step when any other step's `on_failure` points to `error_handler` and all retry attempts are exhausted.

The `automation.retry_attempts` field controls how many times the orchestrator retries a failed step before escalating to `on_failure`.

---

## Monetization Models

| Model | Description |
|-------|-------------|
| `service_sales` | Revenue from selling services (Fiverr, freelance) |
| `deal_commission` | Commission from brokered deals (real estate, B2B) |
| `trading_profits` | Net P&L from automated trading |
| `grant_awards` | Full grant award amounts |
| `contingency_fee` | Percentage of legal settlements |

---

## Security Notes

- Workflows never store credentials — all secrets come from environment variables
- The `legal_money` workflow is disabled by default (`"enabled": false`) and requires manual review before activation
- All payment processing is routed through the `auto_checkout` module with full audit logging
