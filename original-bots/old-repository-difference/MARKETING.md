# DreamCobots Marketing Guide

## Overview

This guide helps you promote DreamCobots bots to non-technical users, small business owners, freelancers, and communities who need automation but don't know how to build it. Use these strategies to drive signups, referrals, and recurring revenue.

---

## DreamCobots Competitive Advantages

| Advantage | Description |
|---|---|
| **Open source** | Users own and control their bots — no vendor lock-in |
| **Plain English config** | Bots configured via JSON/env files, not code |
| **One-command deployment** | `python bot.py` or `docker run` — nothing more |
| **Workflow-ready** | Every bot ships with Zapier, N8n, and Make.com integration |
| **Category-specific** | Bots built for real niches: government contracting, job hunting, social services, side hustles |
| **No subscription required** | Download once, run forever — or offer as managed SaaS |
| **Community-powered** | Open to contributions, templates, and niche extensions |

---

## Bot Promotion Strategies by Category

### 🏛️ Government Contract & Grant Bot

**Target Audience:** Small government contractors, 8(a) certified firms, veteran-owned businesses, grant writers, proposal managers

**Channels:**
- LinkedIn: Post in "Government Contracting" and "Federal Procurement" groups
- Reddit: r/govcontracting, r/SmallBusiness
- SAM.gov user communities and forums
- PTAC (Procurement Technical Assistance Centers) networks
- Email newsletters for WOSB / SDVOSB / 8(a) business owners

**Messaging:**
> "Stop missing out on $700B in government contracts. Our bot monitors SAM.gov 24/7 and emails you the moment a matching opportunity posts — with a draft proposal ready to go."

**Lead Magnet:** Free "How to Use SAM.gov" PDF with bot download CTA

---

### 🤝 211 Resource Eligibility Bot

**Target Audience:** Nonprofits, social workers, case managers, community health workers, legal aid organizations

**Channels:**
- LinkedIn: Social work and nonprofit professional groups
- Facebook: Local community groups, mutual aid networks
- Direct outreach to 211 regional operators and United Way chapters
- NASW (National Association of Social Workers) publications

**Messaging:**
> "Help your clients find food, housing, and healthcare assistance in seconds — not hours. Our free bot screens eligibility and surfaces local resources automatically."

**Lead Magnet:** Free "Social Services Technology Guide for Nonprofits" with bot download CTA

---

### 💼 Selenium Job Application Bot

**Target Audience:** Active job seekers, career coaches, resume writers, workforce development programs

**Channels:**
- Reddit: r/cscareerquestions, r/jobs, r/jobsearchhacks
- TikTok / YouTube: "Job search hacks" content creators
- LinkedIn: Job seeker communities and career coach profiles
- Discord: Programming and career channels

**Messaging:**
> "Apply to 50 jobs while you sleep. Our bot searches Indeed, LinkedIn, Glassdoor, and more — and submits your resume automatically, so you spend time on interviews, not applications."

**Lead Magnet:** Free "Job Application Tracker" spreadsheet template

---

### 💡 AI Side Hustle Bot

**Target Audience:** Aspiring freelancers, content creators, people looking for extra income, entrepreneurs

**Channels:**
- TikTok / Instagram Reels: "Side hustle ideas" and "make money online" niches
- Reddit: r/sidehustle, r/digitalnomad, r/freelance
- YouTube: "passive income", "make money with AI" content
- Newsletter sponsorships in personal finance and entrepreneurship categories

**Messaging:**
> "Not sure which side hustle to start? Our AI bot tells you exactly what to sell, where to find clients, and how much you can make — based on your skills and schedule."

**Lead Magnet:** Free "Top 10 Side Hustles for 2024" guide with bot download CTA

---

## Platform Integration Guide

### Zapier (No-Code Automation)

Zapier lets non-technical users connect DreamCobots bots to 6,000+ apps.

**Setup (5 minutes):**
1. Create a free account at [zapier.com](https://zapier.com)
2. Click **Create Zap** → Trigger: **Webhooks by Zapier → Catch Hook**
3. Copy the webhook URL
4. Paste into your bot's config: `"webhook_url": "https://hooks.zapier.com/..."`
5. Choose your action app (Google Sheets, Gmail, Slack, Trello, etc.)

**Top Zap Ideas per Bot:**

| Bot | Trigger | Action |
|---|---|---|
| Gov Contract Bot | New SAM.gov opportunity | Add row to Google Sheets + Send Slack alert |
| 211 Bot | Eligibility check completed | Email resource list to client |
| Job Bot | Application campaign done | Log results to Airtable |
| Hustle Bot | Marketing plan generated | Save plan to Notion database |

---

### N8n (Self-Hosted Automation)

For users who want privacy and control, N8n is the open-source alternative to Zapier.

**Setup:**
```bash
# Option 1: Docker
docker run -it --rm -p 5678:5678 n8nio/n8n

# Option 2: npm
npm install n8n -g && n8n start
```

1. Open `http://localhost:5678`
2. Add a **Webhook** node, copy the URL
3. Set as `WEBHOOK_URL` in your `.env` file
4. Build your downstream workflow visually

---

### Make.com (Integromat)

Make.com offers a visual drag-and-drop builder with generous free tiers.

1. Sign up at [make.com](https://make.com)
2. Create a scenario → Add **Webhooks → Custom Webhook**
3. Copy the URL → set in bot config
4. Add modules: Google Sheets, Gmail, Slack, Airtable, Notion

---

## Non-Technical User Onboarding Guide

For users who have never used a terminal, guide them through this exact flow:

### Step 1: Install Python (5 minutes)
- Go to [python.org/downloads](https://python.org/downloads)
- Click the yellow "Download Python 3.x" button
- Run the installer — **check "Add Python to PATH"** before clicking Install

### Step 2: Download DreamCobots (2 minutes)
- Go to the GitHub repo
- Click the green **Code** button → **Download ZIP**
- Extract the ZIP to your Desktop

### Step 3: Install the Bot (3 minutes)
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac**: Press `Cmd + Space`, type `Terminal`, press Enter
- In the terminal, type:
  ```
  cd Desktop/DreamCobots/bots/ai-side-hustle-bots
  pip install -r requirements.txt
  ```

### Step 4: Run the Bot (1 minute)
```bash
python bot.py
```
Answer the on-screen questions. That's it!

---

## Pricing & Monetization Suggestions

DreamCobots can be offered as:

| Tier | Model | Price Suggestion |
|---|---|---|
| **Free** | Open source, self-hosted | $0 |
| **Starter** | Hosted bot + email notifications | $9–$19/month |
| **Pro** | All bots + Zapier integration + priority support | $49/month |
| **Agency** | White-label + unlimited runs + custom branding | $199/month |
| **Done-For-You** | Setup service (one-time) | $200–$500 per bot |

**Additional Revenue Streams:**
- Fiverr gig: "I'll set up your DreamCobots government contract bot"
- YouTube tutorials: Monetize with AdSense + affiliate links
- Newsletter: Curated government opportunities or side hustle tips with bot upsell
- Consulting: Automation audits for small businesses

---

## Social Media Marketing Templates

### Twitter / X

> 🤖 Most small businesses miss out on government contracts because they don't know about SAM.gov opportunities in time.
>
> Our free bot monitors SAM.gov 24/7 and sends you alerts + proposal drafts automatically.
>
> Download: [link] #GovCon #SmallBusiness #Automation

---

> 💼 Applied to 0 jobs this week because job searching is exhausting?
>
> Our Selenium Job Bot searches Indeed, LinkedIn & Glassdoor for you — and applies automatically.
>
> Set it up once. Let it run. #JobSearch #Automation #SideHustle

---

### LinkedIn

> **Attention government contractors and small business owners:**
>
> Every day, hundreds of relevant contract opportunities are posted to SAM.gov.
> Most businesses never see them because manual searching is too slow.
>
> The DreamCobots Government Contract Bot monitors SAM.gov automatically, filters by your NAICS codes and keywords, and sends you an instant notification — with a proposal draft already generated.
>
> It takes 15 minutes to set up and costs $0.
>
> 👉 [Link to repo / landing page]

---

### TikTok / YouTube Short Script

> "Did you know there's an open-source bot that finds government contracts for you?
> It monitors SAM.gov 24/7, filters opportunities by your industry,
> and even writes the first draft of your proposal.
> It's completely free. I'll show you how to set it up in 5 minutes."

---

## License

MIT License — see repo root for details.
