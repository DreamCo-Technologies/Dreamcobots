# FollowUpBot

Conducts follow-up sequences to nurture leads that have not yet converted.

## Overview

FollowUpBot is the fourth stage in the sales pipeline. After OutreachBot sends
the initial message, FollowUpBot keeps the conversation alive with a series of
timed follow-up messages until the lead responds or the sequence is exhausted.

## Usage

```python
from bots.FollowUpBot.main import follow_up

messages_sent = follow_up(lead)
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — `follow_up(lead)` |
| `config.json` | Bot configuration |
| `metrics.py` | Activity tracking |
| `README.md` | This file |
