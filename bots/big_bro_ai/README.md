# Big Bro AI

> **"I don't hype. I build. Sit with me if you want to win."**

Big Bro AI is a tier-aware autonomous mentor platform that fuses
**DreamCo + Clawdbot** capabilities into a single, stand-alone system.
It runs in any browser — computer, tablet, phone, Xbox One — with no
downloads and no installs.

---

## System Architecture

Big Bro AI is composed of **eleven core modules** (plus tiers and dashboard):

| Layer | Module | Purpose |
|---|---|---|
| 1 | `personality.py` | Hard-coded character rules, tone logic, roast/defense engine |
| 2 | `memory_system.py` | Consent-based user life profiles (names, goals, struggles, wins) |
| 3 | `mentor_engine.py` | Multi-domain mentoring (money, tech, relationships, confidence) |
| 4 | `bot_factory.py` | Automated bot creation with missions, prospectuses & readiness scores |
| 5 | `continuous_study.py` | Modular knowledge crawlers keeping Big Bro current |
| 6 | `prospectus.py` | Bot prospectus documents with ROI bridges & study paths |
| 7 | `courses_system.py` | Courses-as-systems with automation hooks |
| 8 | `route_gps.py` | Route & GPS intelligence — resource and franchise navigation |
| 9 | `sales_monetization.py` | Income streams, compound interest, revenue projections |
| 10 | `catalog_franchise.py` | Product catalog + franchise territory management |
| 11 | `master_dashboard.py` | Unified command-and-control panel (multi-device) |

---

## Tiers

| Tier | Price | Bots | AI Models | Features |
|---|---|---|---|---|
| FREE | $0/mo | 1 | 3 | Core mentor, memory, personality, roast defense |
| PRO | $49/mo | 10 | 20 | All modules + study engine, courses, GPS, sales |
| ENTERPRISE | $199/mo | Unlimited | 20 | All PRO + franchise, white-label, dedicated support |

---

## Quick Start

```python
from bots.big_bro_ai import BigBroAI, Tier

# Create a Big Bro instance
big_bro = BigBroAI(tier=Tier.PRO, name="Big Bro")

# Chat interface (BuddyAI compatible)
response = big_bro.chat("What's the fastest way to make $100 today?")
print(response["message"])

# Create a user profile (memory system)
big_bro.create_user("user_001", "Marcus", nickname="M", how_we_met="Discord")

# Teach a lesson
lesson = big_bro.teach("user_001", domain=big_bro.mentor.MentorDomain.MONEY)

# Project income
projection = big_bro.project_income(daily_users=5, price_per_user=20.0)
print(projection["explanation"])

# Full dashboard
dashboard = big_bro.get_dashboard()
```

---

## Big Bro Core Rules (Non-Negotiable)

1. Never embarrasses family
2. Protects first, jokes second
3. Explains, never flexes
4. Remembers people because they matter
5. Teaches money as freedom, not greed
6. Tells the truth even when it's uncomfortable
7. Never disappears when things get hard
8. Never roasts height, body, or appearance
9. Roasts excuses, laziness, fake flexing, and weak thinking
10. Adapts tone to each person's situation

---

## Running Tests

```bash
python -m pytest tests/test_big_bro_ai.py -v
```

---

## Framework Compliance

Big Bro AI adheres to the **GLOBAL AI SOURCES FLOW** mandatory pipeline.
See `framework/global_ai_sources_flow.py` for the full specification.
