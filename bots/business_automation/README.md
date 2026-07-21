# Business Automation Bot

Tier-aware workflow and task-automation assistant for the Dreamcobots platform.

---

## Overview

The Business Automation Bot automates repetitive business tasks — meeting
scheduling, invoice generation, CRM syncing, report production, and full ERP
orchestration — all through a simple natural-language chat interface.

---

## Tiers & Pricing

| Tier | Price/month | Requests/month | Highlights |
|---|---|---|---|
| **Free** | $0 | 500 | Meeting scheduler, task reminders, email drafts |
| **Pro** | $49 | 10,000 | CRM sync, invoicing, Slack/Teams notifications |
| **Enterprise** | $299 | Unlimited | ERP integration, workflow orchestration, white-label |

---

## Quick Start

```python
from bots.business_automation import BusinessAutomationBot
from bots.ai_chatbot.tiers import Tier

bot = BusinessAutomationBot(tier=Tier.PRO)

# Natural-language chat
response = bot.chat("Generate an invoice for client ACME Corp")
print(response["message"])

# Direct workflow execution
result = bot.run_workflow("crm_sync", {"account_id": "12345"})
print(result["result"])

# List available workflows
print(bot.list_workflows())
```

---

## Available Workflows

### Free
- `meeting_scheduler` — integrate with calendars to schedule meetings
- `task_reminder` — create and send task reminders
- `email_drafter` — draft professional emails

### Pro (includes all Free)
- `invoice_generator` — create and track invoices
- `crm_sync` — sync contacts and deals with Salesforce / HubSpot
- `report_automation` — export PDF/CSV business reports
- `slack_notifier` — push notifications to Slack / Teams

### Enterprise (includes all Pro)
- `erp_integration` — connect to SAP, Oracle, NetSuite
- `workflow_orchestrator` — build multi-step conditional workflows
- `audit_exporter` — export audit trails and compliance packages
- `white_label_deploy` — deploy a branded automation portal

---

## Monetization

- **SaaS subscription** — FREE / PRO ($49/mo) / ENTERPRISE ($299/mo)
- **API pay-per-use** — available on PRO and ENTERPRISE tiers via the
  Dreamcobots API gateway
- **Client deployment** — white-label deployment on ENTERPRISE tier

---

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.business_automation import BusinessAutomationBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("business", BusinessAutomationBot(tier=Tier.PRO))

response = buddy.chat("business", "Schedule a team standup for Monday 9 AM")
print(response["message"])
```

---

## Directory Structure

```
bots/business_automation/
├── business_automation_bot.py   # Main bot class
├── tiers.py                     # Tier config (workflows & features)
├── __init__.py
└── README.md
```

## Running Tests

```bash
python -m pytest tests/test_business_automation.py -v
```
