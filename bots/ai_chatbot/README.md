# AI Chatbot

A tier-aware conversational AI chatbot that leverages the Dreamcobots AI model
integration layer to provide free and paid editions of each supported NLP model.

---

## Tier Overview

| Tier       | Price/month | Requests/month | NLP Models | History Turns | Support            |
|------------|-------------|----------------|------------|---------------|--------------------|
| Free       | $0.00       | 500            | 3          | 5             | Community          |
| Pro        | $49.00      | 10,000         | 6          | 50            | Email (48 h SLA)   |
| Enterprise | $299.00     | Unlimited       | 6          | Unlimited     | Dedicated 24/7     |

---

## Chatbot Features per Tier

| Feature                        | Free | Pro | Enterprise |
|-------------------------------|------|-----|------------|
| Text responses                 | ✓    | ✓   | ✓          |
| API access                     | ✓    | ✓   | ✓          |
| 5 conversation history turns   | ✓    |     |            |
| Markdown-formatted responses   |      | ✓   | ✓          |
| Code highlighting              |      | ✓   | ✓          |
| File attachments (PDF, TXT)    |      | ✓   | ✓          |
| 50 conversation history turns  |      | ✓   |            |
| Unlimited conversation history |      |     | ✓          |
| Multimodal responses           |      |     | ✓          |
| Custom system prompts          |      |     | ✓          |
| SAML/SSO integration           |      |     | ✓          |
| Audit logging                  |      |     | ✓          |

---

## NLP Models per Tier

### Free
- GPT-3.5 Turbo
- BERT Base
- T5 Small

### Pro (adds)
- GPT-4
- BERT Large
- T5-XL

### Enterprise
Same as Pro (with unlimited history and multimodal capabilities)

---

## Quick Start

```python
from chatbot import Chatbot
from bots.ai_chatbot.tiers import Tier

# Free tier
bot = Chatbot(tier=Tier.FREE)
response = bot.chat("Explain gradient descent in simple terms.")
print(response["message"])

# Pro tier — use GPT-4
pro_bot = Chatbot(tier=Tier.PRO, default_model="nlp/gpt-4")
response = pro_bot.chat("Write a Python function to sort a list.")
print(response["message"])

# See tier details
bot.describe_tier()

# See what upgrading unlocks
bot.show_upgrade_path()
```

---

## Switching / Upgrading Tiers

```python
from chatbot import Chatbot
from bots.ai_chatbot.tiers import Tier

# Upgrade from Free to Pro
bot = Chatbot(tier=Tier.PRO)

# Or read from environment
import os
tier = Tier[os.environ.get("DREAMCOBOTS_TIER", "FREE").upper()]
bot = Chatbot(tier=tier)
```

---

## Directory Structure

```
bots/ai_chatbot/
├── chatbot.py      # Main chatbot class
├── tiers.py        # Chatbot-specific tier config
├── __init__.py
└── README.md       # This file
```
