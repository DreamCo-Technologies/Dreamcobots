# Security Tech Bot

A tier-aware vulnerability scanning and security analysis bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Scans/month | Support          |
|------------|-------------|----------------|-------------|------------------|
| Free       | $0.00       | 500            | 5           | Community        |
| Pro        | $49.00      | 10,000         | 100         | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Unlimited   | Dedicated 24/7   |

---

## Features per Tier

| Feature                              | Free | Pro | Enterprise |
|-------------------------------------|------|-----|------------|
| Basic vulnerability scan             | ✓    | ✓   | ✓          |
| Password strength checker            | ✓    | ✓   | ✓          |
| 5 scans/month                        | ✓    |     |            |
| Full vulnerability assessment        |      | ✓   | ✓          |
| Code security review                 |      | ✓   | ✓          |
| 100 scans/month                      |      | ✓   |            |
| CVE database lookup                  |      | ✓   | ✓          |
| Dependency audit                     |      | ✓   | ✓          |
| Continuous monitoring                |      |     | ✓          |
| Penetration test reports             |      |     | ✓          |
| Compliance scanning (SOC2, HIPAA)    |      |     | ✓          |
| Unlimited scans                      |      |     | ✓          |
| Incident response playbooks          |      |     | ✓          |
| Security dashboard                   |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.security_tech_bot.security_tech_bot import SecurityTechBot

# Free tier — basic scan
bot = SecurityTechBot(tier=Tier.FREE)
result = bot.scan_vulnerabilities("example.com")
print(result)

# Check password strength
strength = bot.check_password_strength("MyP@ssw0rd123!")
print(strength)

# Pro tier — full scan and dependency audit
pro_bot = SecurityTechBot(tier=Tier.PRO)
full_scan = pro_bot.scan_vulnerabilities("api.example.com", scan_type="full")
deps = pro_bot.audit_dependencies([
    {"name": "requests", "version": "1.2.3"},
    {"name": "flask", "version": "2.0.1"},
])
print(deps)

# Enterprise — security report
ent_bot = SecurityTechBot(tier=Tier.ENTERPRISE)
report = ent_bot.generate_security_report([full_scan])
print(report)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/security_tech_bot/
├── security_tech_bot.py  # Main bot class
├── tiers.py              # Bot-specific tier config
├── __init__.py
└── README.md             # This file
```
