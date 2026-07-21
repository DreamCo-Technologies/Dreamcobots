# CloserBot

Closes high-priority leads or flags them for further nurturing.

## Overview

CloserBot is the final stage in the sales pipeline. It evaluates each enriched
lead's score and either closes the deal immediately or routes the lead back to
the nurture sequence.

## Usage

```python
from bots.CloserBot.main import attempt_close, qualify_lead

priority = qualify_lead(lead)   # "high" or "medium"
closed   = attempt_close(lead)  # True if deal closed
```

## Scoring

Leads with a score ≥ 70 (set by `CLOSE_SCORE_THRESHOLD`) are considered
high-priority and closed immediately. All others are sent back to nurture.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — `attempt_close(lead)`, `qualify_lead(lead)` |
| `config.json` | Bot configuration |
| `metrics.py` | Activity tracking |
| `README.md` | This file |
