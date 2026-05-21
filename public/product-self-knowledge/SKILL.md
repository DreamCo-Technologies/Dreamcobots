# Product Self-Knowledge Skill

Describes the **DreamCo Technologies Dreamcobots** platform so Copilot can answer questions about what it does and how to navigate the codebase.

## Platform Overview

Dreamcobots is an AI-powered automation platform with specialized bots for:

- Business workflows (proposals, invoicing, CRM)
- Marketing (social content, SEO, campaigns)
- Finance (budgets, models, expense tracking)
- Real estate (listings, client emails, market analysis)
- Freelance/side hustles
- Government contracts (RFP, compliance)
- Education, healthcare, global/multilingual tasks

## Key Entry Points

| Path | What It Is |
|------|-----------|
| `index.js` | Main application entry |
| `main.py` | Python entry point |
| `api/` | REST API layer |
| `frontend/` | Web UI source |
| `bots/` | Core bot implementations |
| `ai/` | AI/LLM integration |
| `AutoBotFactory/` | Bot templating engine |
| `marketplace/` | AIMarketplace storefront |

## Adding a New Bot

1. Choose the right category directory (e.g., `Marketing_bots/`)
2. Follow the format in `bots_details_instructions.md`
3. Register the bot in the appropriate index file
4. Add tests in `__tests__/` or `tests/`
