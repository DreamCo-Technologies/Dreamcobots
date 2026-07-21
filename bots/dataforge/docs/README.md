# DataForge AI Bot

DataForge AI Bot is a comprehensive data generation, packaging, compliance, and monetization system built on the Dreamcobots platform.

## Overview

DataForge AI Bot orchestrates:
- **Synthetic Dataset Generation**: Voice, facial expression, item/product, behavioral conversation, and emotion engine datasets
- **Multi-format Packaging**: JSON, CSV, JSONL, COCO, and WAV manifest formats
- **Compliance**: GDPR, CCPA, HIPAA, and biometric data protection
- **Marketplace Distribution**: HuggingFace Hub, Kaggle, AWS Marketplace, and direct API sales
- **100 API Connectors**: Covering AI/ML, speech, vision, finance, weather, news, e-commerce, and more
- **User Revenue Sharing**: 70/30 split for data contributors

## Architecture

```
bots/
  bot_base.py                    # Base class for all bots
  dataforge/
    dataforge_bot.py             # Main orchestrator
    compliance.py                # GDPR, CCPA, HIPAA, biometric
    user_marketplace.py          # User contribution and revenue sharing
    sales_channels.py            # Multi-channel dataset sales
    dataset_generators/          # 5 synthetic data generators
    packaging/                   # 5 output format packagers
    licensing/                   # License and consent management
    marketplace/                 # 4 marketplace publishers
    apis/
      api_manager.py             # Lazy-loading API connector manager
      api_registry.py            # Registry of all 100 APIs
      connectors/                # 100 individual API connectors
    tests/                       # Unit tests
    docs/                        # Documentation
```

## Quick Start

```python
from bots.dataforge.dataforge_bot import DataForgeBot

bot = DataForgeBot()
results = bot.run()
```

## Dataset Types

| Dataset | Records | Format | License |
|---------|---------|--------|---------|
| Voice Emotion | 100+ | WAV manifest | CC-BY-4.0 |
| Facial Expression | 200+ | COCO JSON | CC-BY-4.0 |
| Product/Item | 500+ | CSV | CC-BY-4.0 |
| Behavioral Conversations | 100+ | JSONL | CC-BY-4.0 |
| Emotion Engine (Multi-modal) | 200+ | JSON | CC-BY-4.0 |

## Revenue Model

- **Enterprise datasets**: $5,000 - $15,000 per bundle
- **API Subscription**: $499/month
- **Research License**: $999/year
- **User Revenue Split**: 70% user / 30% platform

## License

All synthetic datasets are licensed under CC-BY-4.0. See [LEGAL_COMPLIANCE.md](LEGAL_COMPLIANCE.md) for details.
