# Education Bot

A tier-aware course management and learning platform bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Course Limit | Support          |
|------------|-------------|----------------|--------------|------------------|
| Free       | $0.00       | 500            | 3            | Community        |
| Pro        | $49.00      | 10,000         | 25           | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Unlimited    | Dedicated 24/7   |

---

## Features per Tier

| Feature                     | Free | Pro | Enterprise |
|----------------------------|------|-----|------------|
| 3 active courses            | ✓    |     |            |
| Basic quiz generation       | ✓    | ✓   | ✓          |
| Progress tracking           | ✓    | ✓   | ✓          |
| 25 active courses           |      | ✓   |            |
| Advanced assessments        |      | ✓   | ✓          |
| Certificate generation      |      | ✓   | ✓          |
| Student analytics           |      | ✓   | ✓          |
| Video lesson support        |      | ✓   | ✓          |
| Unlimited courses           |      |     | ✓          |
| AI-powered tutoring         |      |     | ✓          |
| Custom LMS integration      |      |     | ✓          |
| Bulk enrollment             |      |     | ✓          |
| Compliance reporting        |      |     | ✓          |
| White-label branding        |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.education_bot.education_bot import EducationBot

# Create a course
bot = EducationBot(tier=Tier.FREE)
course = bot.create_course("Intro to Python", ["Variables", "Loops", "Functions"])
print(course)

# Generate a quiz
quiz = bot.generate_quiz(course["course"]["course_id"], num_questions=3)
print(quiz)

# Submit an answer
answer = bot.submit_answer(course["course"]["course_id"], "Q-001", "Option A")
print(answer)

# Get progress
progress = bot.get_progress(course["course"]["course_id"])
print(progress)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/education_bot/
├── education_bot.py  # Main bot class
├── tiers.py          # Bot-specific tier config
├── __init__.py
└── README.md         # This file
```
