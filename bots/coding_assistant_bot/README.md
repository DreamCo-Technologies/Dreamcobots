# Coding Assistant Bot

A tier-aware AI-powered code completion, review, and test generation bot for the Dreamcobots platform. Supports multiple programming languages with advanced capabilities based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.coding_assistant_bot.bot import CodingAssistantBot
from bots.coding_assistant_bot.tiers import get_coding_assistant_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)                     | Pro ($49/mo)                              | Enterprise ($299/mo)                       |
|--------------------------|----------------------------------|-------------------------------------------|--------------------------------------------|
| Languages                | 3 (Python, JS, HTML)             | 20 languages                              | All languages                              |
| Code completion          | Basic (1 suggestion)             | Advanced (3 suggestions)                  | Full AI (5 suggestions)                    |
| Code review              | Basic bug detection              | Full review + suggestions                 | Full review + security analysis            |
| Test generation          | ❌                               | ✅                                        | ✅                                         |
| Refactoring              | ❌                               | ✅                                        | ✅                                         |
| Custom model training    | ❌                               | ❌                                        | ✅                                         |
| Team analytics           | ❌                               | ❌                                        | ✅                                         |
| IDE plugins              | ❌                               | ❌                                        | ✅                                         |

## Usage

### Initialize the bot

```python
from bots.coding_assistant_bot.bot import CodingAssistantBot
from tiers import Tier

bot = CodingAssistantBot(tier=Tier.PRO)
```

### Complete code

```python
request = {
    "code": "def calculate_average(numbers):",
    "language": "python",
    "instruction": "calculate and return the average of a list"
}

result = bot.complete_code(request)
print(result)
# {
#   "completion": "# Advanced python completion\ndef calculate_average(numbers):\n...",
#   "language": "python",
#   "suggestions": [
#     "Add type hints for better python readability.",
#     "Consider extracting this into a separate function.",
#     "Add unit tests for the new implementation."
#   ],
#   "tier": "pro"
# }
```

### Review code

```python
code = """
def process(data):
    result = data['value']
    return result * 2
"""

result = bot.review_code(code, "python")
print(result)
# {
#   "language": "python",
#   "issues": ["Check for potential null reference errors.", ...],
#   "suggestions": ["Add comments to improve readability.", ...],
#   "score": 0.75,
#   "tier": "pro"
# }
```

### Generate tests (PRO/ENTERPRISE)

```python
code = "def add(a, b):\n    return a + b"
result = bot.generate_tests(code, "python")
print(result)
# {
#   "language": "python",
#   "tests": "# Auto-generated pytest tests for python\n...",
#   "framework": "pytest",
#   "tier": "pro"
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 4,
#   "requests_remaining": "996",
#   "buddy_integration": True
# }
```

## License

MIT
