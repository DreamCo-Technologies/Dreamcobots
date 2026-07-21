# OutreachBot

Contacts leads via personalized e-mail using an extendable SMTP-based module.

## Overview

OutreachBot is the third stage in the sales pipeline. It takes enriched leads
from EnrichmentBot and sends a personalised opening message to each one.

## Usage

```python
from bots.OutreachBot.main import outreach, run

# Single lead
outreach(lead)

# Batch
run(leads)
```

## Production Setup

Replace the placeholder in `main.py` with real SMTP credentials:

```python
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
```

Alternatively, swap in SendGrid or Mailgun for higher deliverability.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — `outreach(lead)`, `run(leads)` |
| `config.json` | Bot configuration |
| `metrics.py` | Activity tracking |
| `README.md` | This file |
