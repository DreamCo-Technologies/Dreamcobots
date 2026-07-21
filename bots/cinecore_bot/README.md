# DreamCo CineCore Bot 🎬

AI-Powered Commercial & Video Creation System for the DreamCo Technologies ecosystem.

## What It Does

CineCore automates the full lifecycle of AI-powered commercials and video content:

- **Script Generation** — hooks, emotional storytelling, and CTAs
- **AI Video Generation** — Runway AI and Pika Labs integration
- **Voiceover Creation** — emotional tone control, voice cloning
- **Multi-Platform Distribution** — TikTok, YouTube, Instagram, Facebook
- **Legal Lead Generation** — public business directories with human-in-loop outreach
- **AI Closer** — deal closing support with objection handling
- **Stripe Billing** — subscription and one-time payment management
- **Analytics Dashboard** — views, clicks, conversions, revenue per ad
- **Bulk Commercial Generator** — mass production mode
- **Self-Healing System** — auto-detection and fixing of issues

## Directory Structure

```
bots/cinecore_bot/
├── cinecore_bot.py   # Main CineCoreBot class + 10 engines
├── tiers.py          # FREE/PRO/ENTERPRISE tier configuration
├── __init__.py       # Package exports
└── README.md
```

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Script generation | 5/day | 50/day | Unlimited |
| Video generation | ❌ | ✅ Runway + Pika (15s) | ✅ All providers (60s) |
| Voiceover tones | Neutral only | All tones | All + voice cloning |
| Platforms | TikTok | All 4 | All + custom |
| Lead searches | 3/day | 50/day | Unlimited |
| Bulk generation | 1 | 20/run | Unlimited |
| Stripe billing | View only | ✅ | ✅ Full management |
| Auto-posting | ❌ | ✅ | ✅ + scheduling |
| Analytics | Views only | Full | Full + revenue dashboard |
| Self-healing | ✅ | ✅ | ✅ |
| White-label / SaaS | ❌ | ❌ | ✅ |

## Quick Start

```python
from bots.cinecore_bot import CineCoreBot
from tiers import Tier

# Create bot instance
bot = CineCoreBot(tier=Tier.PRO)

# Generate a commercial script
script = bot.generate_script(
    business_name="Local Cafe",
    product="specialty coffee",
    target_audience="young professionals",
    genre="ad"
)
print(script["script"])

# Generate AI video from the script
video = bot.generate_video(script["script"], provider="runway", duration=15)
print(video["video_url"])

# Find and score leads
leads = bot.find_leads("restaurant near me")
scored = bot.score_leads(leads)
print(scored[0])

# Generate outreach draft (requires human approval before sending)
outreach = bot.generate_outreach(leads[0])
print(outreach["message"])

# Create Stripe subscription
subscription = bot.create_subscription("client@example.com", plan="pro")
print(subscription["subscription_id"])

# Get analytics
analytics = bot.get_analytics(video["video_id"])
print(analytics)

# Run a full campaign pipeline
report = bot.run_full_campaign("Local Cafe", "specialty coffee", "young professionals")
print(report["steps_completed"])
```

## Bulk Commercial Generation

```python
businesses = [
    {"name": "Joe's Diner",   "product": "lunch specials",    "target_audience": "office workers"},
    {"name": "AutoFix Pro",   "product": "oil change",        "target_audience": "car owners"},
    {"name": "Sunset Realty", "product": "home listings",     "target_audience": "homebuyers"},
]

results = bot.bulk_generate(businesses, genre="ad", include_video=True)
for r in results:
    print(r["script"]["hook"])
```

## API Keys (Production)

Set these in your `.env` file:

```env
RUNWAY_API_KEY=your_runway_key_here
PIKA_API_KEY=your_pika_key_here
STRIPE_KEY=your_stripe_key_here
OPENAI_KEY=your_openai_key_here
TIKTOK_API_KEY=your_tiktok_key_here
YOUTUBE_API_KEY=your_youtube_key_here
INSTAGRAM_API_KEY=your_instagram_key_here
```

## Outreach Policy

All outreach functionality uses a **human-in-the-loop** model:
- The bot **generates** outreach drafts
- A human **reviews and approves** each message before sending
- No automated spam or unsolicited mass messaging

This ensures compliance with platform terms of service and anti-spam regulations.

## Self-Healing System

```python
# Monitor a component
health = bot.monitor_component("video_engine", status="error")
print(health)  # {"health": "degraded", "issue": {...}, "fix": {"status": "resolved"}}

# Get overall system health
system = bot.system_health()
print(system)  # {"status": "healthy", "fixes_applied": 1, ...}
```

## 200 Features Blueprint

CineCore is designed around the 200-feature DreamCo blueprint:

- **AI + Creation (1–40)**: Script, hook, emotional storytelling, scene builder, voice cloning, subtitles, cinematic transitions, genre switching, product showcase, CTA/thumbnail/title generators
- **Automation (41–80)**: Bulk video creation, auto posting, scheduling, cross-platform sync, campaign duplication, funnel builder, A/B testing, lead scraping, email/SMS outreach, CRM, pipeline tracking, auto follow-ups, Stripe billing, queue system, failover
- **Money + Growth (81–120)**: Client acquisition AI, AI closer, upsell engine, revenue dashboard, pricing optimizer, SaaS builder, white-label system, agency mode, API monetization, licensing
- **System + Security (121–160)**: Auth, role permissions, encryption, rate limiting, logging, error tracking, self-healing, backup/restore, load balancing, Docker, CI/CD, health monitoring, GDPR compliance, fraud detection
- **Future + Domination (161–200)**: Autonomous company mode, AI CEO agent, real-time video, interactive videos, VR/AR support, metaverse integration, developer SDK, global scaling, cultural adaptation, blockchain ownership, DreamCo global network
