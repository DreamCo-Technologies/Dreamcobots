# Job Application Bot

A Python bot that automates logging in, parsing resumes, and submitting job
applications across multiple sites (LinkedIn, Indeed, and any site you add).

---

## Table of Contents
1. [Features](#features)
2. [Directory Structure](#directory-structure)
3. [Setup](#setup)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Scalability](#scalability)
7. [Legal & Ethical Notes](#legal--ethical-notes)

---

## Features
- **Multi-site login** – authenticates to any configured site using credentials
  stored in environment variables (preferred) or `config.json`.
- **Resume parsing** – extracts text from PDF and DOCX resumes and identifies
  matching skills/qualifications via keyword matching.
- **Automated applications** – uses Selenium to find job listings and submit
  applications (LinkedIn Easy Apply, Indeed Apply).
- **CLI interface** – simple command-line commands to run individual steps or
  the full pipeline.
- **Scalable design** – adding a new site requires only a new credential entry
  in `config.json` and a new handler method in `application_submitter.py`.

---

## Directory Structure

```
bots/job-application-bot/
├── bot.py                   # Main entry point
├── cli.py                   # CLI argument parsing and command dispatch
├── login_handler.py         # Selenium-based login for multiple sites
├── resume_parser.py         # PDF/DOCX text extraction and skill matching
├── application_submitter.py # Site-specific application automation
├── config.json              # Sample configuration (credentials + sites)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Setup

### Prerequisites
- Python 3.10+
- Google Chrome (or Chromium) installed
- `chromedriver` matching your Chrome version (or use
  `webdriver-manager` to manage it automatically)

### Install dependencies

```bash
cd bots/job-application-bot
pip install -r requirements.txt
```

### ChromeDriver

Download `chromedriver` from https://googlechromelabs.github.io/chrome-for-testing/
(Chrome 115+) and either place it on your `PATH` or set the `webdriver_path` field in
`config.json`.

Alternatively, let `webdriver-manager` (included in `requirements.txt`) handle it
automatically by updating `cli.py`:

```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

---

## Configuration

Copy `config.json` and fill in your real credentials and search URLs.

```json
{
  "credentials": [
    {
      "site": "linkedin",
      "url": "https://www.linkedin.com/login",
      "username": "REPLACE_WITH_YOUR_EMAIL",
      "password": "REPLACE_WITH_YOUR_PASSWORD"
    }
  ],
  "resume_path": "resume.pdf",
  "applications": [
    {
      "site": "linkedin",
      "search_url": "https://www.linkedin.com/jobs/search/?keywords=Software+Engineer",
      "keywords": ["Python", "Software Engineer"],
      "max_applications": 10
    }
  ],
  "required_skills": ["Python", "SQL", "Git"]
}
```

### Using environment variables (recommended)

Instead of storing passwords in `config.json`, export environment variables
before running the bot:

```bash
export LINKEDIN_USERNAME="you@example.com"
export LINKEDIN_PASSWORD="s3cr3t"
export INDEED_USERNAME="you@example.com"
export INDEED_PASSWORD="s3cr3t"
```

The bot checks for `<SITE>_USERNAME` / `<SITE>_PASSWORD` first and falls back
to the values in `config.json`.

---

## Usage

All commands are run from inside the `bots/job-application-bot/` directory.

```bash
# Display help
python bot.py --help

# Parse a resume and display the qualification summary
python bot.py parse-resume --resume path/to/resume.pdf

# Test logins for all configured sites
python bot.py login

# Test login for a specific site only
python bot.py login --site linkedin

# Submit applications (opens a browser window)
python bot.py apply

# Submit applications in headless mode (no visible browser)
python bot.py apply --headless

# Full pipeline: parse resume → login → apply
python bot.py run --headless
```

---

## Scalability

### Adding a new job site

1. **`config.json`** – add a new entry to `credentials` and `applications`.
2. **`login_handler.py`** – add the site's login field selectors to
   `LoginHandler.SITE_SELECTORS`.
3. **`application_submitter.py`** – add a new `_apply_<site>` method and
   register it in `ApplicationSubmitter.SITE_HANDLERS`.

No other files need to change.

### Adding new required skills

Update the `required_skills` list in `config.json`.

### Running at scale

- Use a job scheduler (cron, GitHub Actions, Airflow) to run the bot on a
  schedule.
- Store credentials in a secrets manager (AWS Secrets Manager, HashiCorp
  Vault) and inject them as environment variables at runtime.
- Run multiple bot instances in parallel, one per site, for higher throughput.

---

## Legal & Ethical Notes

- **Terms of Service**: Review the Terms of Service for every site you
  automate.  Many job sites explicitly prohibit automated scraping or
  application submission.  Use this bot only where permitted.
- **Rate limiting**: Add deliberate delays (`time.sleep`) between actions to
  avoid overloading servers and to reduce detection risk.
- **Data privacy**: Never commit real credentials to the repository.  Use
  environment variables or a secrets manager.
- **Accuracy**: Always review the applications submitted by the bot to ensure
  accuracy and appropriateness before relying on them professionally.
