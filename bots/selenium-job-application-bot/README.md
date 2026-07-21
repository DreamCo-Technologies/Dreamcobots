# Selenium Job Application Bot

## Overview

The **Selenium Job Application Bot** automates job searching and application submission across major platforms including **Indeed, LinkedIn, Glassdoor, ZipRecruiter,** and **Monster**. It uses browser automation to fill out application forms, upload your resume, and submit — all while you focus on interview prep.

Built for job seekers who want to maximize application volume without spending hours clicking through job boards manually.

---

## Features

| Feature | Description |
|---|---|
| **Multi-Platform Search** | Search Indeed, LinkedIn, Glassdoor, ZipRecruiter, and Monster in one run |
| **Automated Form Filling** | Auto-fills application fields using your stored profile |
| **Resume Upload** | Uploads your resume PDF or DOCX automatically |
| **Cover Letter Generation** | Attaches custom or template cover letters |
| **Application Tracking** | Logs every application with status (applied, skipped, error) |
| **Simulation Mode** | Test the bot without a real browser or job sites |
| **Zapier / N8n Integration** | Push application results to downstream workflows |
| **Campaign Management** | Run a full multi-platform campaign with a single command |

---

## Prerequisites

- Python 3.9+
- Google Chrome browser installed
- ChromeDriver (auto-installed via `webdriver-manager`)
- A resume file in PDF or DOCX format

---

## Setup & Installation

### 1. Navigate to the bot directory

```bash
cd bots/selenium-job-application-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure environment

Create a `.env` file:

```env
JOB_KEYWORDS=Python developer,software engineer
JOB_LOCATION=Austin, TX
RESUME_PATH=/path/to/your/resume.pdf
MAX_APPLICATIONS=20
HEADLESS=true
WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID
```

---

## Usage

### Interactive CLI

```bash
python bot.py
```

### Run a campaign programmatically

```python
from bot import SeleniumJobApplicationBot

bot = SeleniumJobApplicationBot(config={
    "headless": True,
    "delay_seconds": 3,
    "simulation_mode": True,   # Set False for live runs
})

results = bot.run_job_campaign(
    keywords="Python developer",
    location="Austin, TX",
    resume_path="/path/to/resume.pdf",
    max_applications=15,
)
print(f"Applied to {results['applied']} jobs!")
```

### Search jobs only (no applications)

```python
jobs = bot.search_jobs("marketing manager", "New York, NY", platform="linkedin")
for job in jobs:
    print(f"{job['title']} @ {job['company']} — {job['url']}")
```

---

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `headless` | bool | `True` | Run browser in headless (no window) mode |
| `delay_seconds` | int | `2` | Pause between actions to avoid bot detection |
| `simulation_mode` | bool | auto-detect | Use simulated data instead of real browsing |
| `log_file` | str | `None` | Path to write application log JSON |

---

## ChromeDriver Setup

The bot uses `webdriver-manager` to automatically download and manage ChromeDriver:

```bash
pip install webdriver-manager
```

No manual ChromeDriver download required. The correct version is fetched automatically.

For server/Docker environments, ensure Google Chrome (or Chromium) is installed:

```bash
apt-get install -y chromium-driver
```

---

## Zapier Integration

1. Create a Zap: **Webhooks → Catch Hook**, copy the URL
2. Set `WEBHOOK_URL` in your `.env`
3. The bot POSTs campaign results after completion
4. Connect to:
   - **Google Sheets**: Log every application with date, company, status
   - **Slack**: Notify when campaign completes or on errors
   - **Airtable**: Build a full job application tracker

---

## N8n Integration

1. Create a **Webhook** trigger node and copy the URL
2. Set `WEBHOOK_URL` in `.env`
3. Add downstream nodes:
   - **Spreadsheet File**: Log applications
   - **Send Email**: Daily application summary
   - **Notion**: Create database entries per application

---

## Deployment

### Docker

```bash
docker build -t job-application-bot .
docker run --env-file .env -v /path/to/resume.pdf:/app/resume.pdf job-application-bot
```

### Scheduled Runs (GitHub Actions / Cron)

Add a cron schedule to `.github/workflows/bot-ci.yml` to run job campaigns daily:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1-5'   # 9 AM Monday–Friday
```

---

## Non-Technical User Guide

1. **Install Python** from [python.org](https://python.org)
2. **Install Google Chrome** if not already installed
3. Open a terminal and run: `pip install -r requirements.txt`
4. Run: `python bot.py`
5. Follow the prompts — enter keywords, location, and resume path
6. The bot handles everything else!

> **Tip:** Start with `simulation_mode: True` to see how the bot works before running live applications.

---

## License

MIT License — see repo root for details.
