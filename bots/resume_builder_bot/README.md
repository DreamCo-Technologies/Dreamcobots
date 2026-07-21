# ResumeBuilderBot

A tier-aware bot for building professional resumes with ATS optimization.

## Tiers
- **FREE**: 1 template, basic formatting, PDF-ready text
- **PRO**: 10 templates, cover letter, ATS score, keyword suggestions
- **ENTERPRISE**: Unlimited templates, multi-language, industry-specific tailoring

## Usage
```python
from bots.resume_builder_bot import ResumeBuilderBot
from tiers import Tier

bot = ResumeBuilderBot(tier=Tier.PRO)
resume = bot.build_resume("Jane Doe", ["Software Engineer at ACME"], ["Python", "Django"], "BS Computer Science")
score = bot.calculate_ats_score(resume)
```
