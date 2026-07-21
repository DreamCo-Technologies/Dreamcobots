# DreamCo Bot Usage Guide

A complete reference for understanding, configuring, and running all DreamCo bots.

---

## Bot Architecture

Every bot in DreamCo follows a three-tier capability model:

| Tier | Cost | Capabilities |
|------|------|-------------|
| **FREE** | $0/mo | Basic automation, limited requests/day, watermarked outputs |
| **PRO** | $49/mo | Full automation, unlimited requests, priority queue, analytics |
| **ENTERPRISE** | $199/mo | Custom integrations, dedicated scheduler, SLA, white-label |

### Directory Structure

```
bots/
├── lead_scraper/           # Multi-source lead generation
├── fiverr/                 # Fiverr gig automation
├── real_estate/            # Property scanning & deal closing
├── crypto/                 # Automated trading
├── grants/                 # Government grant finder
├── legal/                  # Legal claims automation
├── email/                  # Email campaign automation
└── affiliate/              # Affiliate link optimizer
```

Each bot directory contains:
- `bot_name.py` — Main Python bot file
- `config.json` — Bot-specific configuration
- `README.md` — Bot-specific documentation

---

## Running Individual Bots

### Python Bots

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run a single bot
python bots/lead_scraper/multi_source_lead_scraper.py

# Run with custom config
python bots/crypto/crypto_trader.py --config config/crypto_custom.json

# Run with tier override
BOT_TIER=PRO python bots/fiverr/fiverr_auto_apply.py
```

### Node.js Scheduler (runs all bots)

```bash
# Start the cron scheduler (runs all bots on schedule)
node cron/run_bots.js

# Run a single scrape cycle
node -e "require('./cron/scrape_leads').runFullScrape().then(console.log)"

# Send email campaigns
node -e "require('./cron/send_emails').sendCampaign('camp_xyz')"
```

---

## Bot Categories & Configuration

### 1. Lead Scraper Bot

**Purpose**: Scrapes leads from LinkedIn, Google, Indeed, and Zillow.

**Config** (`bots/lead_scraper/config.json`):
```json
{
  "tier": "PRO",
  "sources": ["linkedin", "google", "zillow", "indeed"],
  "keywords": ["real estate investor", "business owner"],
  "max_per_run": 50,
  "dedup": true
}
```

**Environment variables**:
```env
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=yourpass
INDEED_EMAIL=your@email.com
SELENIUM_HEADLESS=true
```

### 2. Fiverr Automation Bot

**Purpose**: Finds high-demand gigs, submits proposals, manages orders.

**Config**:
```env
FIVERR_USERNAME=your_username
FIVERR_PASSWORD=your_password
FIVERR_CATEGORIES=digital-marketing,programming
FIVERR_MIN_BUDGET=50
```

**Expected output**: 3-10 new proposals per 6-hour cycle, $50-$500 per closed deal.

### 3. Real Estate Bot

**Purpose**: Scans MLS/Zillow, scores properties by ROI, contacts sellers.

**Config**:
```env
ZILLOW_API_KEY=your_key
MLS_API_KEY=your_key
REAL_ESTATE_ZIP_CODES=90210,10001,60601
REAL_ESTATE_MAX_PRICE=500000
REAL_ESTATE_MIN_CAP_RATE=0.08
```

### 4. Crypto Trading Bot

**Purpose**: Monitors prices, generates signals, executes trades automatically.

**Config**:
```env
CRYPTO_EXCHANGE_API_KEY=your_key
CRYPTO_EXCHANGE_API_SECRET=your_secret
CRYPTO_EXCHANGE=binance
CRYPTO_PAIRS=BTC/USDT,ETH/USDT
CRYPTO_MAX_POSITION_SIZE=0.05
```

> ⚠️ **Warning**: Only use paper trading mode until you've verified the strategy.

### 5. Grant Finder Bot

**Purpose**: Searches SAM.gov and Grants.gov for matching opportunities.

**Config**:
```env
SAM_GOV_API_KEY=your_key
GRANT_NAICS_CODES=541511,541512
GRANT_BUSINESS_TYPE=small_business
GRANT_MIN_AWARD=25000
```

### 6. Email Campaign Bot

**Purpose**: Sends personalized email sequences to leads.

**Config**:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
EMAIL_FROM=you@yourdomain.com
```

---

## Money Pipeline Explanation

Every bot feeds into a unified money pipeline:

```
[Bot Runs] → [Leads Captured] → [Leads Scored] → [Leads Sold / Converted]
                                                         ↓
[Payment Processed] → [Revenue Logged] → [Dashboard Updated] → [Cycle Repeats]
```

### Data Flow

1. **Bots run** on schedule via `cron/run_bots.js`
2. **Leads are captured** in `money/lead_seller.js` with auto-scoring
3. **Deals are created** in `database/index.js` for tracking
4. **Payments are processed** via `money/auto_checkout.js` (Stripe/PayPal)
5. **Revenue is logged** in the `revenue` table
6. **Dashboard refreshes** every 30 seconds at `/public/index.html`

---

## Adding a New Bot

### Step 1: Create the Python bot file

```python
# bots/my_category/my_bot.py
import os
import json

TIER = os.getenv('BOT_TIER', 'FREE')

def run():
    results = []
    # Your automation logic here
    results.append({
        'name': 'Sample Lead',
        'email': 'sample@example.com',
        'source': 'my_source',
        'category': 'my_category',
        'score': 75
    })
    return results

if __name__ == '__main__':
    data = run()
    print(json.dumps(data, indent=2))
```

### Step 2: Register in the bot catalog

Add your bot to the bot catalog in `index.js`:

```js
{
  id: 'my_new_bot',
  name: 'My New Bot',
  category: 'my_category',
  tier: 'FREE',
  status: 'active',
  description: 'What this bot does'
}
```

### Step 3: Add to the scheduler

```js
// cron/run_bots.js — add to SCHEDULES array
{ botName: 'my_new_bot', intervalMs: 3 * 60 * 60 * 1000, category: 'my_category', description: 'Run every 3h' }
```

### Step 4: Add a workflow (optional)

Create `workflows/my_workflow.json` and register it in `workflows.json`.

---

## Monitoring Bot Performance

All bot runs are logged to:
- **Console**: Colored output with level, namespace, message
- **File**: `logs/app.log` (JSON lines, rotated at 10 MB)
- **Database**: `automation_logs` table

Access logs programmatically:
```js
const { getRecentLogs } = require('./utils/logger');
const errors = getRecentLogs(50, 'ERROR');
```

---

## Troubleshooting Bots

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Bot exits immediately | Missing API key | Check `.env` |
| 0 leads returned | Source blocked/rate limited | Reduce frequency |
| Payment failures | Stripe key invalid | Verify `STRIPE_SECRET_KEY` |
| Crypto bot not trading | Low balance or position limits | Check exchange account |
| Grant bot no results | SAM.gov key expired | Renew at sam.gov |
