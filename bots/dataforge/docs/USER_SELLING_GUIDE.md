# DataForge AI - User Data Selling Guide

## How to Monetize Your Data

DataForge AI provides a marketplace where you can contribute your data and earn revenue.

## Revenue Split

- **70%** goes to you (the data contributor)
- **30%** goes to the platform

## Getting Started

### Step 1: Sign Up
```python
from bots.dataforge.user_marketplace import UserMarketplace

marketplace = UserMarketplace()
user = marketplace.signup_user(
    user_id="your_unique_id",
    name="Your Name",
    email="you@example.com"
)
```

### Step 2: Opt In as Contributor
```python
marketplace.opt_in_contributor("your_unique_id")
```

### Step 3: Submit Your Data
```python
submission = marketplace.submit_data("your_unique_id", {
    "type": "conversation",
    "content": "...",
    "metadata": {"language": "en", "topic": "customer_service"}
})
```

### Step 4: Track Your Earnings
```python
dashboard = marketplace.get_dashboard("your_unique_id")
print(f"Total earned: ${dashboard['total_earned']:.2f}")
print(f"Pending payout: ${dashboard['pending_payout']:.2f}")
```

### Step 5: Request Payout
```python
payout = marketplace.process_payout("your_unique_id")
print(f"Paid: ${payout['amount_paid']:.2f}")
```

## Data Types We Accept

| Data Type | Value Range | Notes |
|-----------|-------------|-------|
| Voice recordings | $$-$$$ | Must be your own voice |
| Text conversations | $$-$$ | Anonymized required |
| Product reviews | $ | Must be authentic |
| Behavioral patterns | $$$-$$$$ | Anonymized required |
| Survey responses | $-$$ | Must be opt-in |

## Privacy & Your Rights

- You retain ownership of your original data
- You can revoke consent at any time
- All data is anonymized before distribution
- You can request deletion of your data

## Compliance Requirements

Before submitting data, ensure:
1. ✅ You have the right to share this data
2. ✅ Any third parties mentioned have consented
3. ✅ No private personal information (PII) is included
4. ✅ Medical, financial, or sensitive data is properly anonymized

## Support

Contact the DataForge AI team for questions about data submission,
payout processing, or compliance requirements.
