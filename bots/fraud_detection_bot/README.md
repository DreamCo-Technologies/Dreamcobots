# Fraud Detection Bot

A tier-aware AI-powered transaction fraud detection and risk analysis bot for the Dreamcobots platform. Analyzes transactions using rule-based and ML-based methods, scores user risk, and generates compliance reports based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.fraud_detection_bot.bot import FraudDetectionBot
from bots.fraud_detection_bot.tiers import get_fraud_detection_tier_info
```

## Tiers

| Feature                     | Free ($0/mo)              | Pro ($49/mo)                         | Enterprise ($299/mo)                          |
|-----------------------------|---------------------------|--------------------------------------|-----------------------------------------------|
| Transactions per month      | 100                       | 50,000                               | Unlimited                                     |
| Detection method            | Rule-based                | ML detection                         | Advanced ML + behavioral analytics            |
| Fraud flag threshold        | > 0.7                     | > 0.6                                | > 0.55                                        |
| Real-time alerts            | ❌                        | ✅                                   | ✅                                            |
| User risk scoring           | ❌                        | ✅                                   | ✅ (behavioral)                               |
| Custom rules                | ❌                        | ✅                                   | ✅                                            |
| Report generation           | ❌                        | ✅                                   | ✅                                            |
| Compliance reports          | ❌                        | ❌                                   | ✅                                            |
| API integration             | ❌                        | ❌                                   | ✅                                            |

## Usage

### Initialize the bot

```python
from bots.fraud_detection_bot.bot import FraudDetectionBot
from tiers import Tier

bot = FraudDetectionBot(tier=Tier.PRO)
```

### Analyze a transaction

```python
transaction = {
    "transaction_id": "TXN-001",
    "amount": 12500.0,
    "merchant": "Electronics Store",
    "user_id": "USER-42"
}

result = bot.analyze_transaction(transaction)
print(result)
# {
#   "transaction_id": "TXN-001",
#   "risk_score": 0.6,
#   "fraud_flag": True,
#   "reasons": ["High transaction amount", "Above-average transaction amount"],
#   "tier": "pro"
# }
```

### Get user risk score (PRO/ENTERPRISE)

```python
data = {
    "user_id": "USER-42",
    "transaction_count": 65,
    "total_amount": 125000.0
}

result = bot.get_risk_score(data)
print(result)
# {
#   "user_id": "USER-42",
#   "risk_score": 0.7,
#   "risk_level": "high",
#   "tier": "pro"
# }
```

### Generate a report (PRO/ENTERPRISE)

```python
report = bot.generate_report("monthly")
print(report)
# {
#   "period": "monthly",
#   "total_transactions": 150,
#   "flagged": 12,
#   "risk_distribution": {"low": 90, "medium": 48, "high": 12},
#   "tier": "pro"
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 5,
#   "requests_remaining": "49995",
#   "transactions_analyzed": 5,
#   "buddy_integration": True
# }
```

## License

MIT
