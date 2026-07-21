"""
Model registry: metadata, capabilities, and tier requirements for every
AI model supported by the Dreamcobots platform.
"""

from dataclasses import dataclass, field
from typing import Optional
from tiers import (
    Tier,
    NLP_GPT35, NLP_GPT4, NLP_BERT_BASE, NLP_BERT_LARGE, NLP_T5_SMALL, NLP_T5_XL,
    CV_YOLO_V5, CV_YOLO_V8, CV_RESNET_50, CV_RESNET_152, CV_CLIP,
    GEN_DALLE2, GEN_DALLE3, GEN_SD_14, GEN_SD_XL, GEN_GPT4V,
    DA_PROPHET, DA_AUTOML, DA_XGBOOST, DA_LIGHTGBM,
)


@dataclass
class ModelInfo:
    model_id: str
    display_name: str
    category: str
    description: str
    min_tier: Tier
    provider: str
    context_window: Optional[int] = None   # tokens (NLP/Gen models)
    input_types: list = field(default_factory=list)
    output_types: list = field(default_factory=list)
    paid_upgrade_note: str = ""


MODEL_REGISTRY: dict[str, ModelInfo] = {
    # ------------------------------------------------------------------
    # NLP Models
    # ------------------------------------------------------------------
    NLP_GPT35: ModelInfo(
        model_id=NLP_GPT35,
        display_name="GPT-3.5 Turbo",
        category="nlp",
        description="Fast, cost-efficient chat completion model. Ideal for "
                    "question answering, summarisation, and text generation.",
        min_tier=Tier.FREE,
        provider="OpenAI",
        context_window=16_385,
        input_types=["text"],
        output_types=["text"],
        paid_upgrade_note="Upgrade to Pro to access GPT-4 with stronger "
                          "reasoning and larger context windows.",
    ),
    NLP_GPT4: ModelInfo(
        model_id=NLP_GPT4,
        display_name="GPT-4",
        category="nlp",
        description="State-of-the-art language model with advanced reasoning "
                    "and instruction following.",
        min_tier=Tier.PRO,
        provider="OpenAI",
        context_window=128_000,
        input_types=["text"],
        output_types=["text"],
    ),
    NLP_BERT_BASE: ModelInfo(
        model_id=NLP_BERT_BASE,
        display_name="BERT Base",
        category="nlp",
        description="Bidirectional encoder for classification, NER, and Q&A.",
        min_tier=Tier.FREE,
        provider="Google / HuggingFace",
        context_window=512,
        input_types=["text"],
        output_types=["embeddings", "classification"],
        paid_upgrade_note="Upgrade to Pro to access BERT Large with higher accuracy.",
    ),
    NLP_BERT_LARGE: ModelInfo(
        model_id=NLP_BERT_LARGE,
        display_name="BERT Large",
        category="nlp",
        description="Larger BERT variant with improved accuracy on NLP benchmarks.",
        min_tier=Tier.PRO,
        provider="Google / HuggingFace",
        context_window=512,
        input_types=["text"],
        output_types=["embeddings", "classification"],
    ),
    NLP_T5_SMALL: ModelInfo(
        model_id=NLP_T5_SMALL,
        display_name="T5 Small",
        category="nlp",
        description="Lightweight text-to-text transfer transformer for translation, "
                    "summarisation, and question answering.",
        min_tier=Tier.FREE,
        provider="Google / HuggingFace",
        context_window=512,
        input_types=["text"],
        output_types=["text"],
        paid_upgrade_note="Upgrade to Pro to access T5-XL for higher quality outputs.",
    ),
    NLP_T5_XL: ModelInfo(
        model_id=NLP_T5_XL,
        display_name="T5-XL",
        category="nlp",
        description="Large T5 variant optimised for high-quality text generation tasks.",
        min_tier=Tier.PRO,
        provider="Google / HuggingFace",
        context_window=512,
        input_types=["text"],
        output_types=["text"],
    ),
    # ------------------------------------------------------------------
    # Computer Vision Models
    # ------------------------------------------------------------------
    CV_YOLO_V5: ModelInfo(
        model_id=CV_YOLO_V5,
        display_name="YOLOv5",
        category="computer_vision",
        description="Fast real-time object detection. Suitable for basic "
                    "detection tasks in images and video streams.",
        min_tier=Tier.FREE,
        provider="Ultralytics",
        input_types=["image", "video"],
        output_types=["bounding_boxes", "labels", "confidence_scores"],
        paid_upgrade_note="Upgrade to Pro to access YOLOv8 with higher mAP and speed.",
    ),
    CV_YOLO_V8: ModelInfo(
        model_id=CV_YOLO_V8,
        display_name="YOLOv8",
        category="computer_vision",
        description="Next-generation YOLO with improved accuracy and native "
                    "segmentation support.",
        min_tier=Tier.PRO,
        provider="Ultralytics",
        input_types=["image", "video"],
        output_types=["bounding_boxes", "labels", "confidence_scores", "masks"],
    ),
    CV_RESNET_50: ModelInfo(
        model_id=CV_RESNET_50,
        display_name="ResNet-50",
        category="computer_vision",
        description="50-layer residual network for image classification and "
                    "feature extraction.",
        min_tier=Tier.FREE,
        provider="Microsoft / HuggingFace",
        input_types=["image"],
        output_types=["classification", "embeddings"],
        paid_upgrade_note="Upgrade to Pro to access ResNet-152 for higher accuracy.",
    ),
    CV_RESNET_152: ModelInfo(
        model_id=CV_RESNET_152,
        display_name="ResNet-152",
        category="computer_vision",
        description="Deeper ResNet with state-of-the-art classification performance.",
        min_tier=Tier.PRO,
        provider="Microsoft / HuggingFace",
        input_types=["image"],
        output_types=["classification", "embeddings"],
    ),
    CV_CLIP: ModelInfo(
        model_id=CV_CLIP,
        display_name="CLIP",
        category="computer_vision",
        description="Contrastive Language–Image Pretraining model for zero-shot "
                    "image classification and multimodal search.",
        min_tier=Tier.ENTERPRISE,
        provider="OpenAI",
        input_types=["image", "text"],
        output_types=["embeddings", "similarity_scores"],
    ),
    # ------------------------------------------------------------------
    # Generative AI Models
    # ------------------------------------------------------------------
    GEN_DALLE2: ModelInfo(
        model_id=GEN_DALLE2,
        display_name="DALL-E 2",
        category="generative_ai",
        description="Generate 1024×1024 images from text prompts.",
        min_tier=Tier.FREE,
        provider="OpenAI",
        input_types=["text"],
        output_types=["image"],
        paid_upgrade_note="Upgrade to Pro to access DALL-E 3 for higher quality "
                          "and larger resolutions.",
    ),
    GEN_DALLE3: ModelInfo(
        model_id=GEN_DALLE3,
        display_name="DALL-E 3",
        category="generative_ai",
        description="Generate photorealistic images up to 1792×1024. Better prompt "
                    "adherence and detail than DALL-E 2.",
        min_tier=Tier.PRO,
        provider="OpenAI",
        input_types=["text"],
        output_types=["image"],
    ),
    GEN_SD_14: ModelInfo(
        model_id=GEN_SD_14,
        display_name="Stable Diffusion 1.4",
        category="generative_ai",
        description="Open-source latent diffusion model for image generation.",
        min_tier=Tier.FREE,
        provider="Stability AI",
        input_types=["text"],
        output_types=["image"],
        paid_upgrade_note="Upgrade to Pro to access Stable Diffusion XL for "
                          "higher resolution outputs.",
    ),
    GEN_SD_XL: ModelInfo(
        model_id=GEN_SD_XL,
        display_name="Stable Diffusion XL",
        category="generative_ai",
        description="High-resolution (1024×1024) open-source image generation with "
                    "improved quality and style adherence.",
        min_tier=Tier.PRO,
        provider="Stability AI",
        input_types=["text"],
        output_types=["image"],
    ),
    GEN_GPT4V: ModelInfo(
        model_id=GEN_GPT4V,
        display_name="GPT-4 Vision",
        category="generative_ai",
        description="Multimodal GPT-4 that accepts image inputs alongside text for "
                    "visual Q&A and detailed scene analysis.",
        min_tier=Tier.ENTERPRISE,
        provider="OpenAI",
        input_types=["text", "image"],
        output_types=["text"],
    ),
    # ------------------------------------------------------------------
    # Data Analytics Models
    # ------------------------------------------------------------------
    DA_PROPHET: ModelInfo(
        model_id=DA_PROPHET,
        display_name="Prophet",
        category="data_analytics",
        description="Facebook's time-series forecasting library for business "
                    "metrics and demand prediction.",
        min_tier=Tier.FREE,
        provider="Meta / Open Source",
        input_types=["time_series"],
        output_types=["forecast"],
        paid_upgrade_note="Upgrade to Pro to access AutoML for automated model "
                          "selection and hyperparameter tuning.",
    ),
    DA_XGBOOST: ModelInfo(
        model_id=DA_XGBOOST,
        display_name="XGBoost",
        category="data_analytics",
        description="Gradient-boosted decision tree library for tabular data "
                    "classification and regression.",
        min_tier=Tier.FREE,
        provider="Open Source",
        input_types=["tabular"],
        output_types=["prediction"],
        paid_upgrade_note="Upgrade to Pro to access LightGBM and AutoML.",
    ),
    DA_AUTOML: ModelInfo(
        model_id=DA_AUTOML,
        display_name="AutoML",
        category="data_analytics",
        description="Automated machine learning pipeline covering feature "
                    "engineering, model selection, and optimisation.",
        min_tier=Tier.PRO,
        provider="Dreamcobots",
        input_types=["tabular", "time_series"],
        output_types=["prediction", "model_artifact"],
    ),
    DA_LIGHTGBM: ModelInfo(
        model_id=DA_LIGHTGBM,
        display_name="LightGBM",
        category="data_analytics",
        description="Fast gradient boosting framework using tree-based learning "
                    "algorithms, optimised for large datasets.",
        min_tier=Tier.PRO,
        provider="Microsoft",
        input_types=["tabular"],
        output_types=["prediction"],
    ),
}


def get_model_info(model_id: str) -> ModelInfo:
    """Return ModelInfo for the given model_id.

    Raises KeyError if model_id is not in the registry.
    """
    if model_id not in MODEL_REGISTRY:
        raise KeyError(f"Model '{model_id}' is not registered.")
    return MODEL_REGISTRY[model_id]


def list_models_for_tier(tier: Tier) -> list[ModelInfo]:
    """Return all models accessible at the given tier level."""
    order = {Tier.FREE: 0, Tier.PRO: 1, Tier.ENTERPRISE: 2}
    return [
        info
        for info in MODEL_REGISTRY.values()
        if order[info.min_tier] <= order[tier]
    ]


def list_models_by_category(category: str) -> list[ModelInfo]:
    """Return all models in the given category."""
    return [m for m in MODEL_REGISTRY.values() if m.category == category]
