# AI Writing Bot

A tier-aware AI-powered content generation and SEO optimization bot for the Dreamcobots platform. Generates articles, product descriptions, emails, and more, with word-limit enforcement and SEO scoring per subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.ai_writing_bot.bot import AIWritingBot
from bots.ai_writing_bot.tiers import get_ai_writing_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)            | Pro ($49/mo)                             | Enterprise ($299/mo)                      |
|--------------------------|-------------------------|------------------------------------------|-------------------------------------------|
| Templates                | 5                       | 50                                       | 100 (unlimited)                           |
| Words per month          | 1,000                   | 50,000                                   | Unlimited                                 |
| SEO optimization         | Basic (score: 0.5)      | Advanced (score: 0.75)                   | Full (score: 0.9)                         |
| Tone control             | ❌                      | ✅                                       | ✅                                        |
| Plagiarism check         | ❌                      | ✅                                       | ✅                                        |
| Brand voice training     | ❌                      | ❌                                       | ✅                                        |
| Multi-language           | ❌                      | ❌                                       | ✅                                        |
| API access               | ❌                      | ❌                                       | ✅                                        |

## Usage

### Initialize the bot

```python
from bots.ai_writing_bot.bot import AIWritingBot
from tiers import Tier

bot = AIWritingBot(tier=Tier.PRO)
```

### Generate content

```python
request = {
    "topic": "sustainable energy",
    "type": "blog post",
    "tone": "professional"
}

result = bot.generate_content(request)
print(result)
# {
#   "content": "Mock content about sustainable energy in blog post format with professional tone...",
#   "word_count": 24,
#   "seo_score": 0.75,
#   "tier": "pro"
# }
```

### Optimize SEO

```python
result = bot.optimize_seo("Your article content here...")
print(result)
# {
#   "original_length": 26,
#   "suggestions": ["Add more keywords", "Improve title", ...],
#   "score": 0.75,
#   "tier": "pro"
# }
```

### Get available templates

```python
templates = bot.get_templates()
print(f"Available templates: {len(templates)}")
# Free: 5, Pro: 50, Enterprise: 100
print(templates[0])
# {"name": "Template 1: Blog Post", "type": "blog post"}
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 2,
#   "requests_remaining": "998",
#   "words_used": 156,
#   "buddy_integration": True
# }
```

## License

MIT
