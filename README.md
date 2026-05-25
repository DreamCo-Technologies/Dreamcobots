# DreamCobots Repository

Welcome to **DreamCobots** — a versatile, user-friendly platform for automation and income generation. This repository contains a growing collection of collaborative bots (cobots) designed to automate tasks, generate income, and empower users across multiple industries.

> **Contributors:** All bots must follow the **GLOBAL AI SOURCES FLOW** mandatory architecture.
> See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---
## 🚀 Why DreamCobots?

- **Non-Technical Friendly**: Each bot ships with detailed setup guides and Docker support — no coding required to get started.
- **Platform Integrations**: All bots support Zapier, N8n, and other SaaS workflows out of the box.
- **Income Generation**: Bots are designed not just for automation, but to actively generate revenue streams.
- **Self-Marketing**: Built-in marketing capabilities help bots promote themselves across platforms.
- **Open & Extensible**: Standardized templates make it easy to add new bots and customize existing ones.

---
## 🤖 Specialized Bot Categories (`bots/`)

| Bot | Description | Docs |
|-----|-------------|------|
| [Government Contract Automation Bot](bots/government-contract-grant-bot/) | Automates SAM.gov contract searches and proposal generation | [README](bots/government-contract-grant-bot/README.md) |
| [211 Resource Eligibility Bot](bots/211-resource-eligibility-bot/) | Helps users find local social services and check eligibility | [README](bots/211-resource-eligibility-bot/README.md) |
| [Selenium Job Application Bot](bots/selenium-job-application-bot/) | Automates job searching and applications across Indeed, LinkedIn, Glassdoor | [README](bots/selenium-job-application-bot/README.md) |
| [AI Side Hustle Bots](bots/ai-side-hustle-bots/) | AI-powered tools to identify, launch, and monetize side hustles | [README](bots/ai-side-hustle-bots/README.md) |

### Quick Start (any bot)

```bash
# Clone the repo
git clone https://github.com/ireanjordan24/Dreamcobots.git
cd Dreamcobots

# Install deps for a specific bot
pip install -r bots/selenium-job-application-bot/requirements.txt

# Run it
python bots/selenium-job-application-bot/bot.py
```

### Docker

```bash
docker build -t selenium-job-bot bots/selenium-job-application-bot/
docker run --rm selenium-job-bot
```

See [MARKETING.md](MARKETING.md) for promotion strategies and platform integration guides (Zapier, N8n, Make.com).

---
## GLOBAL AI SOURCES FLOW — Mandatory Architecture

Every DreamCo bot must implement the eight-stage pipeline defined in
`framework/global_ai_sources_flow.py`:

```
GLOBAL AI SOURCES → Data Ingestion → Learning Classifier → Sandbox Test Lab
  → Performance Analytics → Hybrid Evolution Engine → Deployment Engine
  → Profit & Market Intelligence → Governance + Security
```

See [`framework/global_ai_sources_flow.py`](framework/global_ai_sources_flow.py)
and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full specification and
contribution requirements.

To check that all bots in the repository comply with the framework, run:

```bash
python tools/check_bot_framework.py
```

---
## Installation Instructions
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ireanjordan24/Dreamcobots.git
   ```
2. Navigate to the directory:
   ```bash
   cd Dreamcobots
   ```
3. Install dependencies (if any bot scripts depend on a specific package manager, such as `pip` for Python):
   ```bash
   npm run deps:all
   ```
4. For profile-targeted bootstrap:
   ```bash
   npm run deps:profile:minimal
   npm run deps:profile:core-ai
   npm run deps:profile:frontend
   npm run deps:profile:trading
   npm run deps:profile:full-empire
   ```
5. Validate dependency governance and hermetic environment:
   ```bash
   npm run deps:graph
   npm run deps:policy
   npm run deps:repro-check
   ```

### Hermetic environment pins
- Node: `.nvmrc` (`20`)
- Python: `.python-version` (`3.11`)
- Python lock strategy: `uv.lock` from `pyproject.toml`

---
## Deployment Steps
To deploy bots or static content:
1. Push changes to the `deployment-setup` branch.
2. Enable **GitHub Pages** in repository settings for frontend hosting.
3. Add and customize workflows to automate bot tasks (see GitHub Actions).

---
## AI Model Editions — Free & Paid Tiers

All AI model integrations support three subscription tiers:

| Tier       | Price/month | Requests/month | Models | Support            |
|------------|-------------|----------------|--------|--------------------|
| **Free**   | $0.00       | 500            | 9      | Community          |
| **Pro**    | $49.00      | 10,000         | 18     | Email (48 h SLA)   |
| **Enterprise** | $299.00 | Unlimited      | 20     | Dedicated 24/7     |

### Free Edition
- GPT-3.5 Turbo, BERT Base, T5 Small *(NLP)*
- YOLOv5, ResNet-50 *(Computer Vision)*
- DALL-E 2, Stable Diffusion 1.4 *(Generative AI)*
- Prophet, XGBoost *(Data Analytics)*

### Pro Edition ($49/month)
Everything in Free, **plus**:
- GPT-4, BERT Large, T5-XL *(NLP)*
- YOLOv8, ResNet-152 *(Computer Vision)*
- DALL-E 3, Stable Diffusion XL *(Generative AI)*
- AutoML, LightGBM *(Data Analytics)*
- Batch processing, fine-tuning, analytics dashboard

### Enterprise Edition ($299/month)
Everything in Pro, **plus**:
- CLIP, GPT-4 Vision *(multimodal)*
- Custom models, SLA guarantee, dedicated support, white-label

To switch tiers, set `DREAMCOBOTS_TIER=FREE|PRO|ENTERPRISE` in your environment
or pass `tier=Tier.PRO` when constructing `AIModelsIntegration` / `Chatbot`.

See full documentation in:
- [`bots/ai-models-integration/README.md`](bots/ai-models-integration/README.md)
- [`bots/ai_chatbot/README.md`](bots/ai_chatbot/README.md)

---
## Folder Explanation
### `framework`
- Contains the mandatory **GLOBAL AI SOURCES FLOW** pipeline module
  (`global_ai_sources_flow.py`) that every bot must import and use.

### `tools`
- `check_bot_framework.py` — static analysis script to verify all bot files
  reference the framework.

### `bots`
- Contains all bot scripts such as the `government-contract-grant-bot`.
- `bots/ai-models-integration/` — tiered AI model integration (free/pro/enterprise).
- `bots/ai_chatbot/` — tier-aware AI chatbot built on top of the model integration.
- `config.json` needs to be configured with required API keys and bot settings.

### `automation-tools`
- **Workplace Audit Tool** — 5S methodology audit with scoring and recommendations.
- **Color Palette Generator** — Brand and design palette generation with scheme support.
- **Smart Meeting Scheduler** — Conflict detection and intelligent meeting scheduling.

### `education-tools`
- **Recipe Scaling Tool** — Scale recipes for any serving size with unit conversion.

### `healthcare-tools`
- **Mental Health Screening Bot** — PHQ-2, PHQ-9, and GAD-7 evidence-based screening.
- **Drug Discovery Pipeline AI** — Lipinski Rule-of-Five, ADMET prediction, docking scores.

### `analytics-elites`
- **Loyalty Program Impact Simulator** — Model ROI, CLV uplift, and churn reduction.
- **Predictive Engagement Tool** — Score customer engagement and predict churn risk.
- **Algorithmic Trading Bot** — SMA crossover, RSI signals, and backtesting engine.

### `real-estate-tools`
- **Real Estate Cashflow Simulator** — Cashflow, cap rate, CoC return, and portfolio analysis.

### `compliance-tools`
- Coming soon.

### `examples`
- Contains example use cases for different bots like `Referral Bot` and `Hustle Bot`.

---
## How to Run Bots Locally
1. Navigate to the bot directory. For example:
   ```bash
   cd bots/government-contract-grant-bot
   ```
2. Run the bot script. For example:
   ```bash
   python bot.py
   ```
3. Make sure necessary APIs and configurations are set before running.

---
## GitHub Pages Instructions
1. Navigate to **Settings > Pages**.
2. Select the `deployment-setup` branch and root directory as the publishing source.
3. Save your settings to host the frontend.

---
## 🔑 Environment Variables & Secrets Setup

All sensitive credentials are loaded from environment variables.  **Never
hard-code real keys in source files.**

### Local development

```bash
cp .env.example .env
# Edit .env and fill in your real values
```

### GitHub Actions

Add the following secrets in **Settings → Secrets and variables → Actions →
New repository secret**:

| Secret name | Description |
|---|---|
| `AI_INTEGRATIONS_OPENAI_API_KEY` | OpenAI key used by the AI-integrations bot |
| `OPENAI_API_KEY` | General-purpose OpenAI API key |
| `OPENAI_ENDPOINT` | Custom OpenAI-compatible base URL (optional) |
| `GITHUB_TOKEN` | Auto-provided in GitHub Actions; set manually for local dev and Replit |
| `STRIPE_API_KEY` | Stripe secret key |
| `ZILLOW_API_KEY` | Zillow API key |
| `SCRAPER_API_KEY` | Web scraper API key |

### Replit

1. Open your Repl and click the **🔒 Secrets** icon in the left sidebar.
2. Add each of the secrets listed above as a key/value pair.
3. Replit injects them as environment variables at runtime — no `.env` file needed.

> **Resources:** The project is designed to run within Replit's
> **2 vCPU / 4 GiB RAM** Boost configuration.  Set `SIMULATION_MODE=true`
> (the default) to avoid live API calls while testing.

---
