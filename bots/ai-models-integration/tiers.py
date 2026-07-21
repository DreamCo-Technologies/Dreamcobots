"""
Tier definitions and access control for AI model integrations.

Tiers:
  - FREE:       Basic access, limited requests/month, subset of models.
  - PRO:        Expanded access, higher limits, advanced model variants.
  - ENTERPRISE: Unlimited access, all models, priority support.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name (e.g. "Free", "Pro").
    tier : Tier
        Enum value identifying the tier.
    price_usd_monthly : float
        Monthly subscription price in USD.
    requests_per_month : int | None
        Maximum inference requests per calendar month.  ``None`` means unlimited.
    models_allowed : list
        List of model IDs accessible on this tier.
    features : list
        Feature flags enabled on this tier.
    support_level : str
        Description of the support offering (e.g. "Community", "Email (48 h SLA)").
    """
    name: str
    tier: Tier
    price_usd_monthly: float
    requests_per_month: Optional[int]   # None = unlimited
    models_allowed: list
    features: list
    support_level: str

    def is_unlimited(self) -> bool:
        return self.requests_per_month is None

    def can_use_model(self, model_id: str) -> bool:
        return model_id in self.models_allowed

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# ---------------------------------------------------------------------------
# Model IDs referenced in tier configs
# ---------------------------------------------------------------------------

# NLP
NLP_GPT35 = "nlp/gpt-3.5-turbo"
NLP_GPT4 = "nlp/gpt-4"
NLP_BERT_BASE = "nlp/bert-base"
NLP_BERT_LARGE = "nlp/bert-large"
NLP_T5_SMALL = "nlp/t5-small"
NLP_T5_XL = "nlp/t5-xl"

# Computer Vision
CV_YOLO_V5 = "cv/yolov5"
CV_YOLO_V8 = "cv/yolov8"
CV_RESNET_50 = "cv/resnet50"
CV_RESNET_152 = "cv/resnet152"
CV_CLIP = "cv/clip"

# Generative AI
GEN_DALLE2 = "gen/dall-e-2"
GEN_DALLE3 = "gen/dall-e-3"
GEN_SD_14 = "gen/stable-diffusion-1-4"
GEN_SD_XL = "gen/stable-diffusion-xl"
GEN_GPT4V = "gen/gpt-4-vision"

# Data Analytics
DA_PROPHET = "da/prophet"
DA_AUTOML = "da/automl"
DA_XGBOOST = "da/xgboost"
DA_LIGHTGBM = "da/lightgbm"

FREE_MODELS = [
    NLP_GPT35,
    NLP_BERT_BASE,
    NLP_T5_SMALL,
    CV_YOLO_V5,
    CV_RESNET_50,
    GEN_DALLE2,
    GEN_SD_14,
    DA_PROPHET,
    DA_XGBOOST,
]

PRO_MODELS = FREE_MODELS + [
    NLP_GPT4,
    NLP_BERT_LARGE,
    NLP_T5_XL,
    CV_YOLO_V8,
    CV_RESNET_152,
    GEN_DALLE3,
    GEN_SD_XL,
    DA_AUTOML,
    DA_LIGHTGBM,
]

ENTERPRISE_MODELS = PRO_MODELS + [
    CV_CLIP,
    GEN_GPT4V,
]

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_BASIC_INFERENCE = "basic_inference"
FEATURE_BATCH_PROCESSING = "batch_processing"
FEATURE_FINE_TUNING = "fine_tuning"
FEATURE_CUSTOM_MODELS = "custom_models"
FEATURE_API_ACCESS = "api_access"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"
FEATURE_PRIORITY_QUEUE = "priority_queue"
FEATURE_SLA_GUARANTEE = "sla_guarantee"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_WHITE_LABEL = "white_label"

FREE_FEATURES = [
    FEATURE_BASIC_INFERENCE,
    FEATURE_API_ACCESS,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_BATCH_PROCESSING,
    FEATURE_FINE_TUNING,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_PRIORITY_QUEUE,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_CUSTOM_MODELS,
    FEATURE_SLA_GUARANTEE,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_WHITE_LABEL,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        requests_per_month=500,
        models_allowed=FREE_MODELS,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        requests_per_month=10_000,
        models_allowed=PRO_MODELS,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        requests_per_month=None,
        models_allowed=ENTERPRISE_MODELS,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    """Return all tier configs ordered from cheapest to most expensive."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next higher tier, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
