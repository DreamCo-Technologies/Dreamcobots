# Buddy Core System

The **Buddy Core System** is the central intelligence layer of the DreamCobots ecosystem. It wires together six specialised modules under a single, tier-gated API that speaks the **GLOBAL AI SOURCES FLOW** framework.

---

## Modules

| Module | File | Purpose |
|---|---|---|
| Tiers | `tiers.py` | FREE / PRO / ENTERPRISE config and feature flags |
| Intent Parser | `intent_parser.py` | Keyword-based NL → structured intent |
| Tool DB | `tool_db.py` | 15+ pre-built API/tool catalogue with auto-injection |
| Bot Generator | `bot_generator.py` | Bot-on-Demand: DNA blueprint → template code → deploy |
| Feedback Loop | `feedback_loop.py` | Performance tracking, revenue, auto-optimisation |
| Privacy Engine | `privacy_engine.py` | Permissions, activity logs, encrypted vault, guardrails |
| Lead Engine | `lead_engine.py` | Scrape → score → monetise lead campaigns |

---

## Tiers

| Tier | Price | Bots/day | Leads/day | Features |
|---|---|---|---|---|
| FREE | $0 | 3 | 50 | Intent Parser, Bot Generator, Lead Engine |
| PRO | $49/mo | 20 | 5,000 | + Tool Injection, Feedback Loop, Privacy Vault, Advanced AI |
| ENTERPRISE | $199/mo | Unlimited | Unlimited | + White Label, Custom Encryption, Enterprise Logs |

---

## Quick Start

```python
from bots.buddy_core import BuddyCore, Tier

buddy = BuddyCore(tier=Tier.PRO, operator_name="MyApp")

# Create a bot
result = buddy.create_bot("PropertyScout", purpose="Find real-estate leads")

# Run a lead campaign
campaign = buddy.run_lead_campaign(industry="real_estate", count=50)

# Natural-language chat
reply = buddy.chat("Create a marketing bot called CampaignMaster")
print(reply["message"])

# Full dashboard
overview = buddy.dashboard()
```

---

## GLOBAL AI SOURCES FLOW Entry Point

Every bot exposes a `process(payload: dict) -> dict` method as the standard framework entry point.

```python
buddy.process({"command": "create_bot", "name": "LeadBot", "industry": "finance"})
buddy.process({"command": "run_lead_campaign", "industry": "marketing", "count": 30})
buddy.process({"command": "dashboard"})
```

Supported commands: `chat`, `create_bot`, `run_lead_campaign`, `run_feedback_cycle`, `inject_tools`, `dashboard`, `get_tier_info`.

---

## Privacy & Safety

- **PermissionManager** — `READ_ONLY`, `RESTRICTED`, `FULL_AUTONOMY` levels
- **ActivityLogger** — immutable audit trail of every user action
- **DataVault** — simulated AES-256 encrypted key-value store (base64 + XOR)
- **SafetyGuardrail** — FINANCIAL and SYSTEM actions require explicit confirmation

---

## Running Tests

```bash
pytest tests/test_buddy_core.py -v
```
