# AI Models Integration

This module provides tiered access to 20 AI models across four categories:
**NLP**, **Computer Vision**, **Generative AI**, and **Data Analytics**.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Models | Support            |
|------------|-------------|----------------|--------|--------------------|
| Free       | $0.00       | 500            | 9      | Community          |
| Pro        | $49.00      | 10,000         | 18     | Email (48 h SLA)   |
| Enterprise | $299.00     | Unlimited       | 20     | Dedicated 24/7     |

---

## Included Models per Tier

### Free Tier
| Category          | Model                    | Notes                                     |
|-------------------|--------------------------|-------------------------------------------|
| NLP               | GPT-3.5 Turbo            | Fast chat completion                      |
| NLP               | BERT Base                | Classification & embeddings               |
| NLP               | T5 Small                 | Text-to-text generation                   |
| Computer Vision   | YOLOv5                   | Real-time object detection                |
| Computer Vision   | ResNet-50                | Image classification                      |
| Generative AI     | DALL-E 2                 | 1024×1024 image generation                |
| Generative AI     | Stable Diffusion 1.4     | Open-source image generation              |
| Data Analytics    | Prophet                  | Time-series forecasting                   |
| Data Analytics    | XGBoost                  | Tabular data prediction                   |

### Pro Tier ($49/month)
Everything in Free, **plus**:
| Category          | Model                    | Notes                                     |
|-------------------|--------------------------|-------------------------------------------|
| NLP               | GPT-4                    | Advanced reasoning, 128k context          |
| NLP               | BERT Large               | Higher accuracy NLP                       |
| NLP               | T5-XL                    | High-quality generation                   |
| Computer Vision   | YOLOv8                   | Improved mAP + segmentation               |
| Computer Vision   | ResNet-152               | Deeper feature extraction                 |
| Generative AI     | DALL-E 3                 | Photorealistic, up to 1792×1024           |
| Generative AI     | Stable Diffusion XL      | 1024×1024 open-source generation          |
| Data Analytics    | AutoML                   | Automated model selection & tuning        |
| Data Analytics    | LightGBM                 | Fast large-dataset gradient boosting      |

### Enterprise Tier ($299/month)
Everything in Pro, **plus**:
| Category          | Model                    | Notes                                     |
|-------------------|--------------------------|-------------------------------------------|
| Computer Vision   | CLIP                     | Zero-shot multimodal search               |
| Generative AI     | GPT-4 Vision             | Visual Q&A and scene analysis             |

---

## Feature Flags per Tier

| Feature                | Free | Pro | Enterprise |
|------------------------|------|-----|------------|
| Basic Inference        | ✓    | ✓   | ✓          |
| API Access             | ✓    | ✓   | ✓          |
| Batch Processing       |      | ✓   | ✓          |
| Fine-Tuning            |      | ✓   | ✓          |
| Analytics Dashboard    |      | ✓   | ✓          |
| Priority Queue         |      | ✓   | ✓          |
| Custom Models          |      |     | ✓          |
| SLA Guarantee          |      |     | ✓          |
| Dedicated Support      |      |     | ✓          |
| White-Label            |      |     | ✓          |

---

## Quick Start

```python
from ai_models_integration import AIModelsIntegration, Tier

# 1. Instantiate with your subscription tier
client = AIModelsIntegration(tier=Tier.FREE)

# 2. List available models
for model in client.available_models():
    print(model.display_name, "-", model.category)

# 3. Run a model
result = client.run_model(
    "nlp/gpt-3.5-turbo",
    input_data={"prompt": "Summarise this article..."}
)
print(result)

# 4. See your tier details
client.describe_tier()

# 5. Understand what upgrading unlocks
client.show_upgrade_path()

# 6. Compare all tiers side-by-side
AIModelsIntegration.compare_tiers()
```

---

## Switching / Upgrading Tiers

Pass the desired `Tier` enum value when constructing the client:

```python
from ai_models_integration import AIModelsIntegration, Tier

# Free (default)
free_client = AIModelsIntegration(tier=Tier.FREE)

# Pro
pro_client = AIModelsIntegration(tier=Tier.PRO)

# Enterprise
ent_client = AIModelsIntegration(tier=Tier.ENTERPRISE)
```

For production deployments, store the tier value in your configuration file or
environment variable and inject it at startup:

```python
import os
from ai_models_integration import AIModelsIntegration, Tier

tier = Tier[os.environ.get("DREAMCOBOTS_TIER", "FREE").upper()]
client = AIModelsIntegration(tier=tier)
```

---

## Running the Demo

```bash
cd bots/ai-models-integration
python ai_models_integration.py
```

---

## Directory Structure

```
bots/ai-models-integration/
├── ai_models_integration.py   # Main integration interface
├── tiers.py                   # Tier definitions, configs, and model lists
├── models/
│   └── registry.py            # Full model metadata registry
└── README.md                  # This file
```
