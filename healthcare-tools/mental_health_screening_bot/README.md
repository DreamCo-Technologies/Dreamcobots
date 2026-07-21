# Mental Health Screening Bot

Evidence-based mental health screening using PHQ-2, PHQ-9, and GAD-7 instruments.

**DISCLAIMER:** This tool is for informational purposes only. It does not constitute
medical advice, diagnosis, or treatment. Always consult a licensed healthcare professional.

## Tiers
- **Free** ($0/mo): PHQ-2 screening, basic risk indicator
- **Pro** ($39/mo): PHQ-9 screening, GAD-7 screening, detailed risk report, resource referrals
- **Enterprise** ($149/mo): Custom questionnaires, EHR integration, analytics dashboard

## Usage
```python
import sys
sys.path.insert(0, "healthcare-tools/mental_health_screening_bot")
from mental_health_screening_bot import MentalHealthScreeningBot

bot = MentalHealthScreeningBot(tier="pro")
result = bot.run_phq9([0, 1, 2, 1, 0, 1, 2, 0, 0])
```
