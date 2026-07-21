# DreamCo Revenue Generation Guide

Everything you need to understand and maximize revenue from the DreamCo Money Operating System.

---

## Revenue Streams Overview

DreamCo generates income through five primary channels:

| Stream | Module | Est. Monthly Revenue | Effort Level |
|--------|--------|---------------------|-------------|
| Affiliate Marketing | `money/affiliate_engine.js` | $500–$5,000 | Low |
| Lead Generation & Selling | `money/lead_seller.js` | $1,000–$10,000 | Medium |
| Fiverr Automation | `workflows/fiverr.json` | $2,000–$8,000 | Medium |
| Real Estate Deals | `workflows/real_estate.json` | $5,000–$50,000 | High |
| Government Grants | `workflows/grants.json` | $25,000–$200,000 | High |
| Crypto Trading | `workflows/crypto.json` | $500–$5,000 | Low |
| Legal Claims | `workflows/legal_money.json` | $2,000–$20,000 | High |

---

## 1. Affiliate Marketing Setup

The `affiliate_engine.js` module manages multiple affiliate programs simultaneously.

### Register Your Programs

```js
const { affiliateEngine } = require('./money');

// Register Amazon Associates
affiliateEngine.registerProgram('amazon', {
  displayName: 'Amazon Associates',
  baseUrl: 'https://www.amazon.com/dp/',
  commissionRate: 0.04,    // 4%
  cookieDays: 24,
  category: 'general'
});

// Generate a tracked link
const link = affiliateEngine.generateLink('amazon', 'B08N5WRWNW', 'user_123');
console.log(link.url); // https://www.amazon.com/dp/B08N5WRWNW?tag=user_123&ref=...

// Track performance
affiliateEngine.trackConversion(link.linkId, 299.99);
const earnings = affiliateEngine.getEarnings('amazon');
console.log(earnings); // { program: 'amazon', earnings: 12.00, clicks: 1, conversions: 1 }
```

### Pre-Loaded Programs

5 programs are pre-loaded out of the box:
- **Amazon Associates** (4% commission, 24h cookie)
- **ClickBank** (50% commission, 60-day cookie)
- **ShareASale** (15% commission, 30-day cookie)
- **Impact** (20% commission, 30-day cookie)
- **CJ Affiliate** (8% commission, 45-day cookie)

### Environment Variables

```env
AMAZON_ASSOCIATE_TAG=yourtag-20
CLICKBANK_API_KEY=your_key
SHAREASALE_AFFILIATE_ID=your_id
```

---

## 2. Lead Generation & Selling

The `lead_seller.js` module captures, scores, and sells leads to buyers.

### Lead Capture Flow

```js
const { leadSeller } = require('./money');

// Capture a new lead
const lead = leadSeller.captureLead({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '555-1234',
  source: 'linkedin',
  category: 'real_estate'   // real_estate scores 30 bonus points
});

// AI-score the lead (0–100)
const { score } = leadSeller.scoreLead(lead.leadId);
console.log(`Lead score: ${score}`);  // e.g., 91

// Sell the lead to a buyer
const sold = leadSeller.sellLead(lead.leadId, 'Realty Corp', 75);
console.log(sold.status);  // 'sold'

// Check revenue
const revenue = leadSeller.getRevenue();
console.log(`Total: $${revenue.total}`);
```

### Lead Score Breakdown

| Factor | Points |
|--------|--------|
| Has name | +10 |
| Has email | +15 |
| Has phone | +15 |
| Non-organic source | +10 |
| Real estate category | +30 |
| Crypto category | +25 |
| Business category | +20 |
| Lead < 1 hour old | +20 |
| Lead < 24 hours old | +10 |

### Lead Pricing Guide

| Category | Typical Market Price |
|----------|---------------------|
| Real Estate | $50–$200 |
| Crypto/Investment | $30–$150 |
| Business | $20–$100 |
| Insurance | $15–$80 |
| Legal | $25–$120 |
| General | $5–$25 |

---

## 3. Fiverr Automation

The Fiverr workflow runs every 6 hours to find and apply to gigs automatically.

### Enable the Workflow

```json
// workflows.json — ensure fiverr is enabled
{ "id": "fiverr", "enabled": true, "priority": 1 }
```

### Configuration

```env
FIVERR_USERNAME=your_username
FIVERR_PASSWORD=your_password
FIVERR_MIN_BUDGET=50
FIVERR_CATEGORIES=digital-marketing,programming,writing
```

### Revenue Expectation

- **Proposals sent per cycle**: 5–10
- **Response rate**: 20–40%
- **Close rate**: 30–50%
- **Average deal size**: $75–$500
- **Revenue per cycle**: ~$350
- **Monthly revenue**: ~$1,750 (at 5 cycles/day)

---

## 4. Real Estate Bot Setup

The real estate workflow scans listings daily and contacts motivated sellers.

### Requirements

- Zillow API key (free tier available)
- MLS access (optional but recommended)
- Real estate license or agent partnership (for closing)

### Configure Target Markets

```env
REAL_ESTATE_ZIP_CODES=90210,10001,60601,77001
REAL_ESTATE_MAX_PRICE=500000
REAL_ESTATE_MIN_CAP_RATE=0.08
REAL_ESTATE_PROPERTY_TYPES=single_family,multi_family
```

### Deal Pipeline

1. Bot scans 100–500 listings per day
2. AI filters to top 20 by ROI score
3. Automated outreach to sellers (email + SMS)
4. Qualified leads booked for viewing automatically
5. Offer submitted with AI-assisted negotiation
6. Deal tracked through closing

### Revenue Expectation

- **Listings scanned daily**: 100–500
- **Qualified leads**: 5–20/week
- **Deal close rate**: 5–15%
- **Average deal profit**: $5,000–$30,000
- **Monthly revenue**: $15,000–$100,000+

---

## 5. Government Grants

The most lucrative stream — grant awards are non-dilutive (free money).

### SAM.gov Setup

1. Register at [sam.gov](https://sam.gov)
2. Get your API key from [open.sam.gov](https://open.sam.gov)
3. Add to `.env`:
   ```env
   SAM_GOV_API_KEY=your_key
   ```

### Certifications That Increase Eligibility

- **8(a)** — Small disadvantaged business
- **HUBZone** — Historically underutilized business zone
- **WOSB** — Women-owned small business
- **SDVOSB** — Service-disabled veteran-owned

### Grant Pipeline

```
Search → Score (min 65%) → AI Draft → Review → Submit → Track
```

### Revenue Expectation

- **Grant opportunities found weekly**: 10–50
- **Eligible grants per cycle**: 3–10
- **Application success rate**: 10–25%
- **Average award**: $25,000–$500,000
- **Annual potential**: $100,000–$2,000,000

---

## 6. Crypto Bot

Automated trading on Binance, Coinbase, and Kraken.

### Setup

```env
CRYPTO_EXCHANGE=binance
CRYPTO_EXCHANGE_API_KEY=your_key
CRYPTO_EXCHANGE_API_SECRET=your_secret
CRYPTO_PAIRS=BTC/USDT,ETH/USDT,SOL/USDT
```

### Risk Management

The bot automatically enforces:
- Max 15% portfolio exposure per trade
- 3% stop-loss on every position
- 6% take-profit target
- Max 48-hour hold time
- Pause on high volatility

> **Start with paper trading.** Set `CRYPTO_PAPER_TRADE=true` for 30 days before going live.

---

## 7. Revenue Dashboard Walkthrough

The admin dashboard at `http://localhost:3000` shows:

### Summary Cards (top)
- **Total Revenue** — Sum of all monetization streams
- **Active Bots** — Count of bots currently running
- **Total Leads** — Cumulative leads in pipeline
- **Deals Closed** — Completed transactions

### Revenue Chart
- Line chart of daily revenue over 30 days
- Auto-refreshes every 30 seconds
- Fetches from `GET /api/status`

### Bot Performance Chart
- Bar chart showing top 6 revenue-generating bots
- Click any bar to see bot details

### Bot Status Table
- Live status (Active/Idle/Error) for all bots
- Revenue per bot, leads generated, last run time
- Start/Stop buttons for manual control

### Leads Table
- Recent leads with source, category, AI score, status
- Color-coded badges (green=qualified, yellow=contacted, blue=sold)

### Workflow Cards
- Each pipeline's enable/disable status
- Estimated revenue per cycle
- One-click run trigger

---

## 8. Revenue Tracking

All revenue is tracked in the `revenue` table:

```sql
SELECT source, SUM(amount) as total, COUNT(*) as transactions
FROM revenue
GROUP BY source
ORDER BY total DESC;
```

Via the API:
```bash
curl http://localhost:3000/api/revenue
```

Via Node.js:
```js
const db = require('./database');
const stats = await db.getStats();
console.log(`Total revenue: $${stats.revenue}`);
```

---

## Tips for Maximizing Revenue

1. **Enable all workflows** — Each pipeline compounds your earnings
2. **Score leads aggressively** — Higher-score leads sell for 3–5x more
3. **Set up affiliate links first** — Lowest effort, fastest payback
4. **Apply for certifications** — 8(a) + WOSB doubles grant eligibility
5. **Review crypto strategy monthly** — Markets change; tune the signals
6. **Build your buyer network** — Pre-qualified lead buyers → instant sales
7. **Automate follow-up emails** — `cron/send_emails.js` has 3-sequence templates
