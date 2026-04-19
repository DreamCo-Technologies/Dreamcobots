# AI Marketplace

A platform for purchasing, customising, and deploying DreamCo bots.

## Overview

The AI Marketplace allows users to:
- Browse and purchase bots across multiple categories
- Choose subscription tiers (FREE / PRO / ENTERPRISE)
- Generate SDK stubs (Python & Node.js) for easy integration
- Manage billing through Stripe / PayPal

## Architecture

```
AIMarketplace/
├── marketplace.py         — Core marketplace engine (product catalogue + subscriptions)
├── monetization_api.py    — Stripe / PayPal billing scaffold
├── sdk_builder.py         — Python & Node.js SDK stub generator
├── gui_config.json        — Front-end configuration for the marketplace GUI
└── plugins.md             — Plugin documentation (this file's predecessor)
```

## Quick Start

```python
from AIMarketplace.marketplace import AIMarketplace

market = AIMarketplace()
product = market.add_product(
    name="DreamMimic Voice Bot",
    description="AI-powered TTS and voice cloning.",
    category="voice",
    price_usd=29.99,
)
sub = market.subscribe(user_id="user_001", product_id=product["product_id"])
print(sub)
```

## SDK Generation

```python
from AIMarketplace.sdk_builder import SDKBuilder

builder = SDKBuilder()
print(builder.generate_python(product_id="abc123", package_name="dreammimic_voice"))
print(builder.generate_nodejs(product_id="abc123", package_name="dreammimic-voice"))
```

## Monetisation

```python
from AIMarketplace.monetization_api import MonetizationAPI

api = MonetizationAPI(provider="stripe")
charge = api.charge(user_id="user_001", amount_usd=29.99, description="DreamMimic Voice Bot PRO")
```

## Plugin Sets

See [`plugins.md`](plugins.md) for the original plugin documentation.
